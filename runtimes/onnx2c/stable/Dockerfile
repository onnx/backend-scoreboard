FROM ubuntu:24.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Install Python, build tools, and protobuf dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    cmake \
    gcc \
    g++ \
    git \
    libprotobuf-dev \
    protobuf-compiler \
    && apt-get clean autoclean && apt-get autoremove -y

# Copy local directories
COPY ./test /root/test
COPY ./setup /root/setup
COPY ./backends/onnx2c/backend.py /root/onnx2c_backend.py

# Install test report dependencies
RUN pip3 install --no-cache-dir -r /root/setup/requirements_report.txt

############## ONNX Backend dependencies ###########
ENV ONNX_BACKEND="onnx2c_backend"
ENV PYTHONPATH="/root"

# Install onnx (needed for Python backend wrapper and onnx2c build)
RUN pip3 install onnx

# Build onnx2c from source
RUN git clone --recurse-submodules https://github.com/kraiskil/onnx2c /opt/onnx2c && \
    cd /opt/onnx2c && \
    git checkout e6308a729d067ea3be729c840558ee7832e10b6c && \
    git submodule update --init --recursive && \
    mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j$(nproc) && \
    cp onnx2c /usr/local/bin/onnx2c
####################################################

RUN useradd -m runner && chown -R runner:runner /root
USER runner
WORKDIR /root

CMD ["sh", "-c", ". /root/setup/docker-setup.sh && pytest /root/test/test_backend.py --onnx_backend=${ONNX_BACKEND} -k 'not _cuda' -v"]
