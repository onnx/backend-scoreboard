FROM ubuntu:18.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Install Python dependencies
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    protobuf-compiler \
    libprotoc-dev \
    python3.7 \
    python3.7-dev \
    python3.7-distutils \
    python3-setuptools \
    curl \
    build-essential && \
    apt-get clean autoclean && apt-get autoremove -y

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.7 get-pip.py
RUN pip3 install --upgrade pip setuptools wheel
RUN python3.7 -m pip install protobuf

# Copy local directories
COPY ./test /root/test
COPY ./setup /root/setup

# Install test report dependencies
RUN pip3 install --no-cache-dir -r /root/setup/requirements_report.txt

############## ONNX Backend dependencies ###########
ENV ONNX_BACKEND="onnx_tf.backend"

# Install dependencies
RUN mkdir /root/app && \
    cd /root/app && \
    git clone https://github.com/onnx/onnx.git && \
    cd onnx && \
    git submodule update --init --recursive && \
    python3.7 setup.py install
RUN pip3 install --no-cache-dir \
    tensorflow \
    onnx-tf
####################################################

CMD . /root/setup/docker-setup.sh && \
    pytest /root/test/test_backend.py --onnx_backend=${ONNX_BACKEND} -k 'not _cuda' -v
