FROM ubuntu:20.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Install Python dependencies
RUN apt-get update && apt-get install -y \
    python \
    python-dev \
    python3 \
    python3-dev \
    python3-pip && \
    apt-get clean autoclean && apt-get autoremove -y

RUN pip3 install --upgrade pip setuptools wheel

# Copy local directories
COPY ./test /root/test
COPY ./setup /root/setup

# Install test report dependencies
RUN pip3 install --no-cache-dir -r /root/setup/requirements_report.txt

############## ONNX Backend dependencies ###########
ENV ONNX_BACKEND="ngraph_onnx.onnx_importer.backend"

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    unzip \
    curl \
    autogen \
    automake \
    autoconf \
    zlib1g \
    zlib1g-dev \
    libtool \
    libtinfo-dev && \
    apt-get clean autoclean && apt-get autoremove -y

# ONNX dependencies
RUN apt-get update && apt-get -y install \
    protobuf-compiler \
    libprotobuf-dev && \
    apt-get clean autoclean && apt-get autoremove -y

# Build nGraph
WORKDIR /root
RUN git clone --depth 1 https://github.com/NervanaSystems/ngraph.git
RUN mkdir /root/ngraph/build
WORKDIR /root/ngraph/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/root/ngraph_dist -DNGRAPH_USE_PREBUILT_LLVM=TRUE -DNGRAPH_CPU_ENABLE=TRUE -DNGRAPH_ONNX_IMPORT_ENABLE=TRUE -DCMAKE_BUILD_TYPE=Release ..
RUN make -j"$(nproc)"
RUN make install

# Build Python bindings for nGraph
WORKDIR /root/ngraph/python
RUN git clone --depth 1 --branch v2.2.4 https://github.com/pybind/pybind11.git
ENV NGRAPH_ONNX_IMPORT_ENABLE=TRUE
ENV PYBIND_HEADERS_PATH=/root/ngraph/python/pybind11
ENV NGRAPH_CPP_BUILD_PATH=/root/ngraph_dist
ENV LD_LIBRARY_PATH=/root/ngraph_dist/lib
RUN pip install .

# Install nGraph-ONNX
WORKDIR /root
RUN git clone --depth 1 https://github.com/NervanaSystems/ngraph-onnx.git
WORKDIR /root/ngraph-onnx
RUN pip install -r requirements.txt
RUN pip install -r requirements_test.txt
RUN pip install .
####################################################

CMD . /root/setup/docker-setup.sh && \
    pytest /root/test/test_backend.py --onnx_backend=${ONNX_BACKEND} -k 'not _cuda' -v
