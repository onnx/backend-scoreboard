FROM ubuntu:18.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Set proxy
ARG http_proxy
ARG https_proxy
ENV http_proxy ${http_proxy}
ENV https_proxy ${https_proxy}

#Python dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip

RUN pip3 install --upgrade pip setuptools wheel

# Download onnx-runtime
RUN pip3 install --no-cache-dir onnx && \
    pip3 install --no-cache-dir onnxruntime && \
    pip3 install --no-cache-dir pytest && \
    pip3 install --no-cache-dir tabulate

# Run pytest
WORKDIR /root/src
COPY ./src/test_backend_onnx.py /root/src
CMD pytest test_backend_onnx.py
