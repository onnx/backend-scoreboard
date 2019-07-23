FROM ubuntu:18.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Set proxy
ARG http_proxy
ARG https_proxy
ENV http_proxy ${http_proxy}
ENV https_proxy ${https_proxy}

# General dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libgoogle-glog-dev \
    libgtest-dev \
    libiomp-dev \
    libleveldb-dev \
    liblmdb-dev \
    libopencv-dev \
    libopenmpi-dev \
    libsnappy-dev \
    libprotobuf-dev \
    openmpi-bin \
    openmpi-doc \
    protobuf-compiler 

# Python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python \
    python-dev \
    python-pip 

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir \
      future \
      numpy \
      protobuf \
      typing \
      hypothesis \
      six \
      pyyaml \
      pytest \
      tabulate

# Install ONNX
RUN pip install --no-cache-dir onnx 

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgflags-dev \
    cmake

# Download pytorch
RUN git clone https://github.com/pytorch/pytorch.git
WORKDIR /pytorch
RUN git submodule update --init --recursive
RUN python setup.py install

# Run pytest
WORKDIR /root/src
COPY ./src/test_backend_pytorch.py /root/src
CMD pytest test_backend_pytorch.py

# # Run resnet50 using pytorch backend
# ADD ./models/resnet50.tar.gz /root/models
# WORKDIR /root/src
# COPY ./src/test_resnet50_pytorch.py /root/src
# CMD python test_resnet50_pytorch.py