# ONNX Backend Scoreboard

## Build docker images
From the main dir (onnx-backend-scoreboard/) 

* ONNX-runtime <br/>
`docker build -t scoreboard-onnx -f runtimes/onnx-runtime/Dockerfile .`

* nGraph <br/>
`docker build -t scoreboard-ngraph -f runtimes/ngraph/Dockerfile .`

* PyTorch <br/>
`docker build -t scoreboard-pytorch -f runtimes/pytorch/Dockerfile .`

* Tensorflow <br/>
`docker build -t scoreboard-tensorflow -f runtimes/tensorflow/Dockerfile .`


<br/>

###### Proxy settings
Use --build-arg to set http and https proxy

`docker build -t scoreboard-<backend> --build-arg http_proxy=your-http-proxy.com/ --build-arg https_proxy=your-https-proxy.com/ -f runtimes/<backend>/Dockerfile .`
