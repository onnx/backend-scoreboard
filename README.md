# ONNX Backend Scoreboard

## Build docker images
From the main dir (onnx-backend-scoreboard/) 

* nGraph <br/>
`docker build -t scoreboard-ngraph -f runtimes/ngraph/development/Dockerfile .`

* ONNX-runtime <br/>
`docker build -t scoreboard-onnx -f runtimes/onnx-runtime/stable/Dockerfile .`

* PyTorch <br/>
`docker build -t scoreboard-pytorch -f runtimes/pytorch/development/Dockerfile .`

* Tensorflow <br/>
`docker build -t scoreboard-tensorflow -f runtimes/tensorflow/stable/Dockerfile .`


<br/>

###### Proxy settings
Use --build-arg to set http and https proxy

`docker build -t scoreboard-<backend> --build-arg http_proxy=your-http-proxy.com/ --build-arg https_proxy=your-https-proxy.com/ -f <path_to_dockerfile>/Dockerfile .`
