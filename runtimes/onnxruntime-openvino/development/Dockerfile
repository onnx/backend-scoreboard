FROM ubuntu:22.04

# Proxy build arguments (passed via --build-arg)
ARG http_proxy
ARG https_proxy
ARG ftp_proxy
ARG socks_proxy
ARG no_proxy

# Expose proxy settings to all subsequent RUN steps
ENV http_proxy=${http_proxy}
ENV https_proxy=${https_proxy}
ENV ftp_proxy=${ftp_proxy}
ENV socks_proxy=${socks_proxy}
ENV no_proxy=${no_proxy}

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and locale dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    locales \
    dos2unix && \
    apt-get clean autoclean && apt-get autoremove -y

RUN pip3 install --upgrade pip setuptools wheel

# Create a non-root user for running the container
RUN useradd -m -s /bin/bash onnx

# Copy local directories
COPY ./test /home/onnx/test
COPY ./setup /home/onnx/setup

# Fix Windows line endings on all shell scripts and Python files
RUN find /home/onnx/setup /home/onnx/test -type f \( -name "*.sh" -o -name "*.py" -o -name "*.txt" -o -name "*.json" \) -exec dos2unix {} +

# Install test report dependencies
RUN pip3 install --no-cache-dir -r /home/onnx/setup/requirements_report.txt

############## ONNX Backend dependencies ###########
# onnxruntime-openvino bundles ORT with the OpenVINO Execution Provider
# and exposes the same onnxruntime.backend.backend interface
ENV ONNX_BACKEND="onnxruntime.backend.backend"

# Set locale which is required for StringNormalizer
RUN locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8

# Install development/nightly onnxruntime-openvino (includes ORT + OpenVINO EP)
# pytest-forked isolates each test in a subprocess so that segfaults
# in the OpenVINO EP crash only that test, not the whole run.
# --pre allows installing pre-release/dev versions from PyPI.
RUN pip3 install --no-cache-dir --pre \
    onnx \
    onnxruntime-openvino \
    protobuf \
    numpy \
    pytest-forked
####################################################

# Ensure results directory exists so docker-setup.sh can write pip-list.json
RUN mkdir -p /home/onnx/results

# Override default paths (env.list uses /root) for the non-root user
ENV RESULTS_DIR=/home/onnx/results
ENV CSVDIR=/home/onnx/results

# Set ownership and switch to non-root user
RUN chown -R onnx:onnx /home/onnx
USER onnx

CMD ["sh", "-c", ". /home/onnx/setup/docker-setup.sh && pytest /home/onnx/test/test_backend.py --onnx_backend=${ONNX_BACKEND} -k 'not _cuda' --forked -v"]
