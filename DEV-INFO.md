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
            "results_dir": "./results/onnx-runtime/stable",
            "core_packages": ["onnxruntime"]
        },
        "onnxtf": {
            "name": "ONNX-TF",
            "results_dir": "./results/tensorflow/stable",
            "core_packages": ["onnx-tf", "tensorflow"]
        }
    },
    "development": {
        "onnxruntime": {
            "name": "ONNX-Runtime",
            "results_dir": "./results/onnxruntime/development"
        },
        "onnxtf": {
            "name": "ONNX-TF",
            "results_dir": "./results/tensorflow/development",
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
`docker build -t scoreboard-onnx -f runtimes/onnx-runtime/stable/Dockerfile .`

* ONNX-TF: <br/>
`docker build -t scoreboard-tensorflow -f runtimes/tensorflow/stable/Dockerfile .`

### Development versions (built from source)

* ONNX-Runtime: <br/>
`docker build -t scoreboard-onnx -f runtimes/onnx-runtime/development/Dockerfile .`

* ONNX-TF: <br/>
`docker build -t scoreboard-tensorflow -f runtimes/tensorflow/development/Dockerfile .`


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
`docker run --name onnx-runtime --env-file setup/env.list -v ~/backend-scoreboard/results/onnx-runtime/stable:/root/results scoreboard/onnx`

* ONNX-TF <br/>
`docker run --name tensorflow --env-file setup/env.list -v ~/backend-scoreboard/results/tensorflow/stable:/root/results scoreboard/tensorflow`

### Development (build from source)

* ONNX-Runtime <br/>
`docker run --name onnx-runtime --env-file setup/env.list -v ~/backend-scoreboard/results/onnx-runtime/development:/root/results scoreboard/onnx`

* ONNX-TF <br/>
`docker run --name tensorflow --env-file setup/env.list -v ~/backend-scoreboard/results/tensorflow/development:/root/results scoreboard/tensorflow`


## Generation of the Scoreboard pages

From the main directory of the repository, issue the following command:

`python3 website-generator/generator.py --config ./setup/config.json`

where `--config` parameter is the path to `config.json` file.

This will generate an HTML version of the Scoreboard in the `docs` directory
(or another specified in `deploy_paths` in `config.json`).

