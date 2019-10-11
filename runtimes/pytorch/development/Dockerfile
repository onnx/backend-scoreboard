FROM ubuntu:18.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Install Python dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip && \
    apt-get clean autoclean && apt-get autoremove -y

RUN pip3 install --upgrade pip setuptools wheel

# Copy local directories
COPY ./test /root/test
COPY ./setup /root/setup

# Install test report dependencies
RUN pip3 install --no-cache-dir -r /root/setup/requirements_report.txt

############## ONNX Backend dependencies ###########
ENV ONNX_BACKEND="caffe2.python.onnx.backend"

# Install dependencies
RUN pip3 install --no-cache-dir onnx

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
    protobuf-compiler && \
    apt-get clean autoclean && apt-get autoremove -y

RUN pip3 install --no-cache-dir \
    future \
    numpy \
    protobuf \
    typing \
    hypothesis \
    six \
    pyyaml

RUN apt-get install -y --no-install-recommends \
    libgflags-dev \
    cmake && \
    apt-get clean autoclean && apt-get autoremove -y

# Download pytorch
RUN git clone https://github.com/pytorch/pytorch.git
WORKDIR /pytorch
RUN git submodule update --init --recursive
RUN python3 setup.py install
####################################################

CMD . /root/setup/docker-setup.sh && \
    pytest /root/test/test_backend.py --onnx_backend=${ONNX_BACKEND} -k 'not _cuda' -v
