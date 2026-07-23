FROM ubuntu:22.04

# Disable interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Install Python, locale, and Rust build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gcc \
    locales \
    python3 \
    python3-dev \
    python3-pip \
    && apt-get clean autoclean && apt-get autoremove -y \
    && pip3 install --upgrade pip setuptools wheel

# Install a pinned Rust toolchain used to build the RTen bridge runner.
ENV RUSTUP_HOME=/opt/rustup
ENV CARGO_HOME=/opt/cargo
ENV PATH="/opt/cargo/bin:${PATH}"
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
    sh -s -- -y --profile minimal --default-toolchain stable

# Copy local directories
COPY ./test /root/test
COPY ./setup /root/setup
COPY ./backends/rten/backend.py /root/rten_backend.py
COPY ./rten_bridge /root/rten_bridge
COPY ./rten_bridge_runner /root/rten_bridge_runner

# Build the RTen bridge runner once at image build time so tests don't need
# network access or a writable cargo cache at runtime.
RUN cargo build --release --locked \
    --manifest-path /root/rten_bridge_runner/Cargo.toml

# Install test report dependencies
RUN pip3 install --no-cache-dir -r /root/setup/requirements_report.txt

############## ONNX Backend dependencies ###########
ENV ONNX_BACKEND="rten_backend"
ENV PYTHONPATH="/root"

# Set locale and install ONNX + bridge dependencies.
RUN locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8 && \
    pip3 install --no-cache-dir \
    onnx \
    safetensors
####################################################

RUN useradd -m -u 1000 runner && chown -R runner:runner /root
USER runner
WORKDIR /root

CMD ["sh", "-c", ". /root/setup/docker-setup.sh && pytest /root/test/test_backend.py --onnx_backend=${ONNX_BACKEND} -k 'not _cuda' -v"]
