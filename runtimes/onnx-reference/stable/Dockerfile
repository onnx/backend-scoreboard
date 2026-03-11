FROM ubuntu:24.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Install Python and locales dependencies
RUN apt-get update && apt-get install -y \
	python3 \
    python3-dev \
    python3-pip \
    locales && \
    apt-get clean autoclean && apt-get autoremove -y

# Copy local directories
COPY ./test /root/test
COPY ./setup /root/setup
COPY ./backends/onnx_reference/backend.py /root/onnx_reference_backend.py

# Install test report dependencies
RUN pip3 install --no-cache-dir -r /root/setup/requirements_report.txt

############## ONNX Backend dependencies ###########
ENV ONNX_BACKEND="onnx_reference_backend"
ENV PYTHONPATH="/root"

# Set locale which is required for StringNormalizer
RUN locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8

# Install dependencies
RUN pip3 install \
    onnx \
    numpy \
    protobuf
####################################################

CMD ["sh", "-c", ". /root/setup/docker-setup.sh && pytest /root/test/test_backend.py --onnx_backend=${ONNX_BACKEND} -k 'not _cuda' -v"]