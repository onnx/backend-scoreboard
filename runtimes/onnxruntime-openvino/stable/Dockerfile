FROM ubuntu:22.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and locale dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    locales \
    dos2unix && \
    apt-get clean autoclean && apt-get autoremove -y && \
    pip3 install --upgrade pip setuptools wheel

# Create working directory
RUN useradd -m onnx
WORKDIR /home/onnx

# Copy local directories
COPY ./test /home/onnx/test
COPY ./setup /home/onnx/setup
COPY ./backends/onnxruntime_openvino/backend.py /home/onnx/onnxruntime_openvino_backend.py

# Fix Windows line endings
RUN find /home/onnx/setup /home/onnx/test -type f \( -name "*.sh" -o -name "*.py" -o -name "*.txt" -o -name "*.json" \) -exec dos2unix {} + && \
    dos2unix /home/onnx/onnxruntime_openvino_backend.py

# Install test report dependencies
RUN pip3 install --no-cache-dir -r /home/onnx/setup/requirements_report.txt && \
    mkdir -p /home/onnx/results

############## ONNX Backend dependencies ###########
ENV ONNX_BACKEND="onnxruntime_openvino_backend"
ENV PYTHONPATH="/home/onnx"
ENV RESULTS_DIR="/home/onnx/results"
ENV CSVDIR="/home/onnx/results"

# Set locale and install ONNX Runtime with OpenVINO ABI EP plugin
RUN locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8 && \
    pip3 install --no-cache-dir \
    onnx \
    onnxruntime \
    onnxruntime-ep-openvino \
    protobuf \
    numpy
####################################################

CMD ["sh", "-c", ". /home/onnx/setup/docker-setup.sh && pytest /home/onnx/test/test_backend.py --onnx_backend=${ONNX_BACKEND} -k 'not _cuda' -v"]
