FROM python:3.9

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Install Python dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip && \
    apt-get clean autoclean && apt-get autoremove -y


# Copy local directories
COPY ./test /root/test
COPY ./setup /root/setup

# Install test report dependencies
RUN pip3 install --no-cache-dir -r /root/setup/requirements_report.txt

############## ONNX Backend dependencies ###########
ENV ONNX_BACKEND="jaxonnxruntime.backend"

# Install dependencies
RUN pip3 install --no-cache-dir \
    onnx \
    jaxonnxruntime

####################################################
RUN pip3 install --upgrade pip setuptools wheel pytest

############## JAX and JAXONNXRuntime configs ###########
# ref to https://github.com/google/jaxonnxruntime/blob/main/tests/onnx_ops_test.py
ENV JAX_ENABLE_X64=True
ENV JAX_NUMPY_RANK_PROMOTION=warn
ENV JAXORT_ONLY_ALLOW_INITIALIZERS_AS_STATIC_ARGS=0
ENV JAXORT_NONZERO_USE_FULLY_PADDING=1

CMD . /root/setup/docker-setup.sh && \
    pytest /root/test/test_backend.py --onnx_backend=${ONNX_BACKEND} -k 'not _cuda' -v
