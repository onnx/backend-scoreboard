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
    python3 \
    python3-dev \
    python3-pip

RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel
RUN pip3 install --no-cache-dir \
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
RUN pip3 install --no-cache-dir onnx

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgflags-dev \
    cmake

# Download pytorch
RUN git clone https://github.com/pytorch/pytorch.git
WORKDIR /pytorch
RUN git submodule update --init --recursive
RUN python3 setup.py install

# ONNX-backend test results dir
RUN mkdir -p /root/results/csv
ENV CSVDIR=/root/results/csv
RUN mkdir -p /root/results/json
ENV RESULTS_DIR=/root/results/json

# Run pytest
WORKDIR /root/test
COPY ./test/conftest.py /root/test
COPY ./test/test_backend.py /root/test
CMD pytest test_backend.py --onnx_backend="caffe2.python.onnx.backend" -k 'not _cuda'
