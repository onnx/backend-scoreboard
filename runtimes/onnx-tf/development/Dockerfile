FROM ubuntu:20.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Install Python dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    git && \
    apt-get clean autoclean && apt-get autoremove -y && \
    pip3 install --upgrade pip setuptools wheel

# Copy local directories
COPY ./test /root/test
COPY ./setup /root/setup

# Install test report dependencies (pytest<9 and tabulate<0.10 required for Python 3.8)
RUN pip3 install --no-cache-dir \
    "pytest>=8.0,<9" \
    "tabulate>=0.8.10,<0.10" \
    "PyYAML>=6.0.3"

############## ONNX Backend dependencies ###########
ENV ONNX_BACKEND="onnx_tf.backend"

RUN pip3 install onnx && \
    pip3 install --no-cache-dir \
        tensorflow \
        tensorflow-probability && \
    pip3 install git+https://github.com/onnx/onnx-tensorflow.git@main
####################################################

CMD ["sh", "-c", ". /root/setup/docker-setup.sh && pytest /root/test/test_backend.py --onnx_backend=${ONNX_BACKEND} -k 'not _cuda' -v"]
