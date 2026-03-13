FROM ubuntu:24.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_BREAK_SYSTEM_PACKAGES=1
ENV CC=gcc-14

# Install Python, gcc and locales dependencies
# emx-onnx-cgen needs a compiler with C23 _BitInt(N) support. Ubuntu 24.04's
# default gcc-13 does not provide it on this target, so install and prefer gcc-14.
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    gcc-14 \
    g++-14 \
    locales && \
    apt-get clean autoclean && apt-get autoremove -y

RUN ln -sf /usr/bin/gcc-14 /usr/bin/gcc && \
    ln -sf /usr/bin/g++-14 /usr/bin/g++

# Copy local directories
COPY ./test /root/test
COPY ./setup /root/setup

# Install test report dependencies
RUN pip3 install --no-cache-dir -r /root/setup/requirements_report.txt

############## ONNX Backend dependencies ###########
ENV ONNX_BACKEND="emx_onnx_cgen.onnx_backend"

# Set locale which is required for StringNormalizer
RUN locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8

# Install emx-onnx-cgen backend and onnx
RUN pip3 install \
    onnx \
    emx-onnx-cgen
####################################################

RUN useradd -m runner && chown -R runner:runner /root
USER runner
WORKDIR /root

CMD ["sh", "-c", ". /root/setup/docker-setup.sh && pytest /root/test/test_backend.py --onnx_backend=${ONNX_BACKEND} -k 'not _cuda' -v"]
