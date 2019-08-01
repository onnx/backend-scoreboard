FROM ubuntu:18.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Set proxy
ARG http_proxy
ARG https_proxy
ENV http_proxy ${http_proxy}
ENV https_proxy ${https_proxy}

# Python dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip

RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Install ONNX-tf and dependencies
RUN pip3 install --no-cache-dir \
    onnx \
    tensorflow \
    onnx-tf

# Install test dependencies
RUN pip3 install --no-cache-dir \
    pytest \
    tabulate

# ONNX-backend test results dir
RUN mkdir -p /root/results/csv
ENV CSVDIR=/root/results/csv
RUN mkdir -p /root/results/json
ENV RESULTS_DIR=/root/results/json

# Run pytest
WORKDIR /root/test
COPY ./test/conftest.py /root/test
COPY ./test/test_backend.py /root/test
CMD pytest test_backend.py --onnx_backend="onnx_tf.backend" -k 'not _cuda'
