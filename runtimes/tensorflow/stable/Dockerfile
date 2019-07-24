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

# Run pytest
WORKDIR /root/test
COPY ./test/conftest.py /root/test
COPY ./test/test_backend.py /root/test
CMD pytest test_backend.py --onnx_backend="onnx_tf.backend"
