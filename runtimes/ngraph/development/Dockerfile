FROM ubuntu:18.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Set proxy
ARG http_proxy
ARG https_proxy
ENV http_proxy ${http_proxy}
ENV https_proxy ${https_proxy}

# nGraph dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    clang-3.9 \
    git \
    unzip \
    curl \
    autogen \
    automake \
    autoconf \
    zlib1g \
    zlib1g-dev \
    libtool \
    libtinfo-dev

# Python dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip

RUN pip3 install --upgrade pip setuptools wheel

# ONNX dependencies
RUN apt-get update && apt-get -y install \
    protobuf-compiler \
    libprotobuf-dev

# Install nGraph in root/ngraph
WORKDIR /root
RUN git clone https://github.com/NervanaSystems/ngraph.git
RUN mkdir /root/ngraph/build
WORKDIR /root/ngraph/build
RUN cmake -DNGRAPH_USE_PREBUILT_LLVM=TRUE -DNGRAPH_CPU_ENABLE=TRUE  -DCMAKE_INSTALL_PREFIX=/root/ngraph_dist -DNGRAPH_ONNX_IMPORT_ENABLE=TRUE -DCMAKE_BUILD_TYPE=Release ..
RUN make -j"$(nproc)"
RUN make install

# Build Python package (Binary wheel) for nGraph
WORKDIR /root/ngraph/python
RUN git clone https://github.com/pybind/pybind11.git
ENV NGRAPH_ONNX_IMPORT_ENABLE=TRUE
ENV PYBIND_HEADERS_PATH=/root/ngraph/python/pybind11
ENV NGRAPH_CPP_BUILD_PATH=/root/ngraph_dist
ENV LD_LIBRARY_PATH=/root/ngraph_dist/lib
RUN python3 setup.py develop

# Install nGraph-ONNX
WORKDIR /root
RUN git clone -b master --single-branch --depth 1 https://github.com/NervanaSystems/ngraph-onnx.git
WORKDIR /root/ngraph-onnx
RUN pip install -r requirements.txt
RUN pip install -r requirements_test.txt
RUN pip install -e .

# Test report dependencies
RUN pip install --no-cache-dir pytest && \
    pip install --no-cache-dir tabulate

# ONNX-backend test results dir
RUN mkdir -p /root/results
ENV RESULTS_DIR=/root/results
ENV CSVDIR=/root/results

# Run pytest
WORKDIR /root/test
COPY ./test/conftest.py /root/test
COPY ./test/test_backend.py /root/test
CMD pytest test_backend.py --onnx_backend="ngraph_onnx.onnx_importer.backend" -k 'not _cuda'
