FROM ubuntu:22.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Install Python, gcc and locales dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    gcc \
    locales && \
    apt-get clean autoclean && apt-get autoremove -y && \
    pip3 install --upgrade pip setuptools wheel

# Copy local directories
COPY ./test /root/test
COPY ./setup /root/setup
COPY ./backends/emx_onnx_cgen/backend.py /root/emx_backend.py

# Install test report dependencies
RUN pip3 install --no-cache-dir -r /root/setup/requirements_report.txt

############## ONNX Backend dependencies ###########
ENV ONNX_BACKEND="emx_backend"
ENV PYTHONPATH="/root"

# Set locale which is required for StringNormalizer
RUN locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8

# Install emx-onnx-cgen and onnx
RUN pip3 install \
    onnx \
    emx-onnx-cgen
####################################################

RUN useradd -m -u 1000 runner && chown -R runner:runner /root
USER runner
WORKDIR /root

CMD ["sh", "-c", ". /root/setup/docker-setup.sh && pytest /root/test/test_backend.py --onnx_backend=${ONNX_BACKEND} -k 'not _cuda' -v"]
