use std::collections::HashMap;
use std::env;
use std::path::{Path, PathBuf};

use anyhow::{anyhow, bail, Context, Result};
use rten::{Model, Value, ValueOrView};
use rten_serialize::{Value as SerializedValue, View as SerializedView};
use rten_tensor::{AsView, Layout, Tensor};

struct Args {
    model: PathBuf,
    inputs: PathBuf,
    outputs: PathBuf,
}

fn parse_args() -> Result<Args> {
    let mut args = env::args().skip(1);
    let mut model = None;
    let mut inputs = None;
    let mut outputs = None;

    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--model" => model = args.next().map(PathBuf::from),
            "--inputs" => inputs = args.next().map(PathBuf::from),
            "--outputs" => outputs = args.next().map(PathBuf::from),
            other => bail!("unexpected argument {other}"),
        }
    }

    Ok(Args {
        model: model.context("missing --model")?,
        inputs: inputs.context("missing --inputs")?,
        outputs: outputs.context("missing --outputs")?,
    })
}

fn saturating_i32_from_i64(value: i64) -> i32 {
    value.clamp(i32::MIN as i64, i32::MAX as i64) as i32
}

fn saturating_i32_from_u64(value: u64) -> i32 {
    value.min(i32::MAX as u64) as i32
}

fn convert_input(value: SerializedValue) -> Result<Value> {
    Ok(match value {
        SerializedValue::Float32(tensor) => Value::from(tensor),
        SerializedValue::Int32(tensor) => Value::from(tensor),
        SerializedValue::Int8(tensor) => Value::from(tensor),
        SerializedValue::UInt8(tensor) => Value::from(tensor),
        SerializedValue::Bool(tensor) => {
            let shape = tensor.shape().to_vec();
            let data: Vec<_> = tensor.iter().map(|value| i32::from(*value)).collect();
            Value::from(Tensor::<i32>::from_data(&shape, data))
        }
        SerializedValue::Int16(tensor) => {
            let shape = tensor.shape().to_vec();
            let data: Vec<_> = tensor.iter().map(|value| i32::from(*value)).collect();
            Value::from(Tensor::<i32>::from_data(&shape, data))
        }
        SerializedValue::Int64(tensor) => {
            let shape = tensor.shape().to_vec();
            let data: Vec<_> = tensor
                .iter()
                .map(|value| saturating_i32_from_i64(*value))
                .collect();
            Value::from(Tensor::<i32>::from_data(&shape, data))
        }
        SerializedValue::UInt16(tensor) => {
            let shape = tensor.shape().to_vec();
            let data: Vec<_> = tensor.iter().map(|value| i32::from(*value)).collect();
            Value::from(Tensor::<i32>::from_data(&shape, data))
        }
        SerializedValue::UInt32(tensor) => {
            let shape = tensor.shape().to_vec();
            let data: Vec<_> = tensor
                .iter()
                .map(|value| saturating_i32_from_u64(u64::from(*value)))
                .collect();
            Value::from(Tensor::<i32>::from_data(&shape, data))
        }
        SerializedValue::UInt64(tensor) => {
            let shape = tensor.shape().to_vec();
            let data: Vec<_> = tensor
                .iter()
                .map(|value| saturating_i32_from_u64(*value))
                .collect();
            Value::from(Tensor::<i32>::from_data(&shape, data))
        }
        SerializedValue::Float64(tensor) => {
            let shape = tensor.shape().to_vec();
            let data: Vec<_> = tensor.iter().map(|value| *value as f32).collect();
            Value::from(Tensor::<f32>::from_data(&shape, data))
        }
        _ => bail!("unsupported serialized input type for RTen bridge"),
    })
}

fn read_inputs(path: &Path) -> Result<HashMap<String, Value>> {
    let tensors = rten_serialize::safetensors::read_from_file(path)
        .with_context(|| format!("failed to read inputs from {}", path.display()))?;
    tensors
        .into_iter()
        .map(|(name, value)| Ok((name, convert_input(value)?)))
        .collect()
}

fn output_view(value: &Value) -> Result<SerializedView<'_>> {
    match value {
        Value::FloatTensor(tensor) => Ok(tensor.view().into()),
        Value::Int32Tensor(tensor) => Ok(tensor.view().into()),
        Value::Int8Tensor(tensor) => Ok(tensor.view().into()),
        Value::UInt8Tensor(tensor) => Ok(tensor.view().into()),
        Value::Sequence(_) => Err(anyhow!(
            "sequence outputs are not supported by the RTen bridge"
        )),
        _ => Err(anyhow!(
            "unsupported RTen output variant for bridge serialization"
        )),
    }
}

fn write_outputs(path: &Path, names: &[String], outputs: &[Value]) -> Result<()> {
    let tensors: Vec<(String, SerializedView<'_>)> = names
        .iter()
        .zip(outputs.iter())
        .map(|(name, value)| Ok((name.clone(), output_view(value)?)))
        .collect::<Result<_>>()?;

    rten_serialize::safetensors::write_to_file(
        path,
        tensors
            .iter()
            .map(|(name, view)| (name.as_str(), view.clone())),
    )
    .with_context(|| format!("failed to write outputs to {}", path.display()))
}

fn main() -> Result<()> {
    let args = parse_args()?;
    let model = Model::load_file(&args.model)
        .with_context(|| format!("failed to load model {}", args.model.display()))?;
    let mut inputs_by_name = read_inputs(&args.inputs)?;

    let named_inputs: Vec<(rten::NodeId, ValueOrView<'static>)> = model
        .input_ids()
        .iter()
        .copied()
        .map(|id| {
            let info = model
                .node_info(id)
                .ok_or_else(|| anyhow!("missing input info for node {id:?}"))?;
            let name = info
                .name()
                .ok_or_else(|| anyhow!("input node {id:?} has no name"))?;
            let value = inputs_by_name
                .remove(name)
                .ok_or_else(|| anyhow!("missing input tensor {name}"))?;
            Ok((id, value.into()))
        })
        .collect::<Result<_>>()?;

    if let Some(unused) = inputs_by_name.keys().next() {
        bail!("unexpected input tensor {unused}");
    }

    let output_ids = model.output_ids();
    let output_names: Vec<String> = output_ids
        .iter()
        .map(|id| {
            model
                .node_info(*id)
                .and_then(|info| info.name().map(|name| name.to_string()))
                .ok_or_else(|| anyhow!("output node {id:?} has no name"))
        })
        .collect::<Result<_>>()?;

    let outputs = model
        .run(named_inputs, output_ids, None)
        .context("model run failed")?;
    write_outputs(&args.outputs, &output_names, &outputs)?;
    Ok(())
}
