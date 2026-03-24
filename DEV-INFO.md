<!--- SPDX-License-Identifier: Apache-2.0 -->

# Debugging commands

The following commands may be useful, if you would like to reproduce the Scoreboard locally for testing.

### Configuration file

Configuration in the `config.json` file contains a list of frameworks included in ONNX Backend Scoreboard.
This is a place for base information like results paths and core packages names.
Each new runtime has to be added to this file.

Example of `config.json` file:
```json
{
    "stable": {
        "onnxruntime": {
            "name": "ONNX-Runtime",
            "link": "https://onnxruntime.ai/",
            "description": "Production-grade AI engine for running ONNX models efficiently across hardware and platforms.",
            "long_description": "ONNX Runtime is a production-focused inference and training engine for ONNX models across CPUs, GPUs, and accelerators.",
            "results_dir": "./results/ort/stable",
            "core_packages": ["onnxruntime"]
        },
        "onnxtf": {
            "name": "ONNX-TF",
            "link": "https://github.com/onnx/onnx-tensorflow",
            "description": "TensorFlow backend for ONNX that converts ONNX models to TensorFlow for execution.",
            "long_description": "ONNX-TF converts ONNX graphs into TensorFlow representations so they can be executed within the TensorFlow ecosystem.",
            "results_dir": "./results/onnx-tf/stable",
            "core_packages": ["onnx-tf", "tensorflow"]
        }
    },
    "development": {
        "onnxruntime": {
            "name": "ONNX-Runtime",
            "link": "https://onnxruntime.ai/",
            "description": "Production-grade AI engine for running ONNX models efficiently across hardware and platforms.",
            "long_description": "ONNX Runtime is a production-focused inference and training engine for ONNX models across CPUs, GPUs, and accelerators.",
            "results_dir": "./results/onnxruntime/development"
        },
        "onnxtf": {
            "name": "ONNX-TF",
            "link": "https://github.com/onnx/onnx-tensorflow",
            "description": "TensorFlow backend for ONNX that converts ONNX models to TensorFlow for execution.",
            "long_description": "ONNX-TF converts ONNX graphs into TensorFlow representations so they can be executed within the TensorFlow ecosystem.",
            "results_dir": "./results/onnx-tf/development",
            "core_packages": ["tensorflow"]
        }
    },
    "deploy_paths": {
        "index": "./docs",
        "subpages": "./docs",
        "resources": "./docs/resources"
    }
}
```

## Building Docker images

Use these commands from the main directory of this repository to build Docker images which run backend tests.

### Stable versions

* ONNX-Runtime: <br/>
`docker build -t scoreboard/ort -f runtimes/ort/stable/Dockerfile .`

* ONNX-TF: <br/>
`docker build -t scoreboard/onnx-tf -f runtimes/onnx-tf/stable/Dockerfile .`

* JaxOnnxRuntime <br/>
`docker build -t scoreboard/jaxonnxruntime -f runtimes/jaxonnxruntime/stable/Dockerfile .`

* emx-onnx-cgen <br/>
`docker build -t scoreboard/emx-onnx-cgen -f runtimes/emx-onnx-cgen/stable/Dockerfile .`

* tract <br/>
`docker build -t scoreboard/tract -f runtimes/tract/stable/Dockerfile .`

* ONNX Reference <br/>
`docker build -t scoreboard/onnx-reference -f runtimes/onnx-reference/stable/Dockerfile .`

### Development versions (built from source)

* ONNX-Runtime: <br/>
`docker build -t scoreboard/ort-dev -f runtimes/ort/development/Dockerfile .`

* ONNX-TF: <br/>
`docker build -t scoreboard/onnxtf-dev -f runtimes/onnx-tf/development/Dockerfile .`

* JaxOnnxRuntime <br/>
`docker build -t scoreboard/jaxonnxruntime-dev -f runtimes/jaxonnxruntime/development/Dockerfile .`

###### Proxy settings

If you're working behind a firewall use `--build-arg`s to set `http_proxy`  and `https_proxy`

```shell
docker build -t scoreboard-<backend> \
             --build-arg http_proxy=your-http-proxy.com \
             --build-arg https_proxy=your-https-proxy.com \
             -f <path_to_dockerfile>/Dockerfile .
```

## Run Docker containers

Running a Docker container based on the previously prepared image, will run ONNX tests and
store results in the directory specified as `results_dir` in `config.json`.

### Stable

* ONNX-Runtime <br/>
`docker run --name ort --env-file setup/env.list -v ~/backend-scoreboard/results/ort/stable:/root/results scoreboard/ort`

* ONNX-TF <br/>
`docker run --name onnx-tf --env-file setup/env.list -v ~/backend-scoreboard/results/onnx-tf/stable:/root/results scoreboard/onnx-tf`

* JaxOnnxRuntime <br/>
`docker run --name jaxonnxruntime --env-file setup/env.list -v ~/backend-scoreboard/results/jaxonnxruntime/stable:/root/results scoreboard/jaxonnxruntime`

* emx-onnx-cgen <br/>
`docker run --name emx-onnx-cgen --env-file setup/env.list -v ~/backend-scoreboard/results/emx-onnx-cgen/stable:/root/results scoreboard/emx-onnx-cgen`

* tract <br/>
`docker run --name tract --env-file setup/env.list -v ~/backend-scoreboard/results/tract/stable:/root/results scoreboard/tract`

* ONNX Reference <br/>
`docker run --name onnx-reference --env-file setup/env.list -v ~/backend-scoreboard/results/onnx-reference/stable:/root/results scoreboard/onnx-reference`

### Development (build from source)

* ONNX-Runtime <br/>
`docker run --name ort-dev --env-file setup/env.list -v ~/backend-scoreboard/results/ort/development:/root/results scoreboard/ort-dev`

* ONNX-TF <br/>
`docker run --name onnxtf-dev --env-file setup/env.list -v ~/backend-scoreboard/results/onnx-tf/development:/root/results scoreboard/onnxtf-dev`

* JaxOnnxRuntime <br/>
`docker run --name jaxonnxruntime-dev --env-file setup/env.list -v ~/backend-scoreboard/results/jaxonnxruntime/development:/root/results scoreboard/jaxonnxruntime-dev`



## Generation of the Scoreboard pages

From the main directory of the repository, issue the following command:

`python3 website-generator/generator.py --config ./setup/config.json`

where `--config` parameter is the path to `config.json` file.

This will generate an HTML version of the Scoreboard in the `docs` directory
(or another specified in `deploy_paths` in `config.json`).

