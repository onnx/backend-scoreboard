<!--- SPDX-License-Identifier: Apache-2.0 -->

## How to add new backend to the scoreboard?

The following tutorial provides steps needed to add an ONNX backend named `new_backend` to the Scoreboard.

### 1. Prepare Dockerfile

Use the [dockerfile template](examples/Dockerfile) from examples to create Dockerfile for a new runtime.

#### Find and edit code marked `## ONNX Backend dependencies ##`.

* Set `ONNX_BACKEND` variable to the Python dotted path of the ONNX backend module which provides an
  implementation of the `onnx.backend.base.Backend` interface class.
* Write commands required to install all dependencies.
* If you use a release version of the backend, place your Dockerfile in `runtimes/{new-backend}/stable`.
* You an also track a development version of the backend. In this case store the file in `runtimes/{new-backend}/development`.

```
############## ONNX Backend dependencies ###########
ENV ONNX_BACKEND="{new_backend.backend}"

# Install dependencies
RUN pip install onnx
RUN pip install {new_backend}

####################################################
```

### 2. Update configuration
* Add your backend to the [`config.json`](setup/config.json) file. Use the `stable` or `development` section as appropriate.

<br/> For `stable` version:

```json
"new_backend": {
            "name": "New Backend",
            "results_dir": "./results/new_backend/stable",
            "core_packages": ["new-backend"]
        }
```

For `development` version the `core_packages` list is optional:

```json
"new_backend": {
            "name": "New Backend",
            "results_dir": "./results/new-backend/development",
        }
```

### 3. Add new job to GitHub Actions workflow

* Edit [benchmark-backends.yml](.github/workflows/benchmark-backends.yml) file.
* Copy and paste this [job template](examples/job.yml) to the end of file.
* Fill `new_backend` with the new backend unique name.
* Change the `docker build` and `docker run` commands to match your backend.

```yml

 jobs:
  ... # other jobs

  new_backend:
    runs-on: ubuntu-latest
    timeout-minutes: 90
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Build docker image
        run: docker build -t scoreboard/new_backend -f runtimes/new_backend/stable/Dockerfile .

      - name: Set up SSH
        uses: webfactory/ssh-agent@v0.9.0
        with:
            ssh-private-key: |
                  ${{ secrets.DEPLOY_KEY }}

      - name: Git setup
        run: . setup/git-setup.sh

      - name: Run docker container
        run: docker run --name new_backend --env-file setup/env.list -v `pwd`/results/new_backend/stable:/root/results scoreboard/new_backend || true

      - name: Deploy results
        run: . setup/git-deploy-results.sh
```
