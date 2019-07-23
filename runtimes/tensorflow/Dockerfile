FROM ubuntu:18.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Set proxy
ARG http_proxy
ARG https_proxy
ENV http_proxy ${http_proxy}
ENV https_proxy ${https_proxy}

# Python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python \
    python-dev \
    python-pip 

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install ONNX-tf and dependencies
RUN pip install --no-cache-dir \
    onnx \
    tensorflow \
    onnx-tf

# Install test dependencies
RUN pip install --no-cache-dir \
    pytest \
    tabulate

# # Install tensorflow from source
# RUN apt-get update && apt-get install -y --no-install-recommends git
# RUN git clone git@github.com:onnx/onnx-tensorflow.git 
# WORKDIR /onnx-tensorflow
# RUN pip install -e .

# Run pytest
WORKDIR /root/src
COPY ./src/test_backend_tensorflow.py /root/src
CMD pytest test_backend_tensorflow.py

# # # Run resnet50 using tensorflow backend
# ADD ./models/resnet50.tar.gz /root/models
# WORKDIR /root/src
# COPY ./src/test_resnet50_tensorflow.py /root/src
# CMD python test_resnet50_tensorflow.py