FROM rockylinux:9.3 AS base

RUN echo "max_parallel_downloads=10" >> /etc/dnf/dnf.conf
RUN dnf update -y && \
    dnf install -y \
    git

    # Install UV and setup cargo bin for rust tools (uv and cargo)
ENV PATH="/root/.cargo/bin:${PATH}"
ENV UV_INSTALL_DIR=/root/.cargo/bin
ENV UV_COMPILE_BYTECODE=1
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN uv self update

FROM base AS final

# create this...
WORKDIR /data

WORKDIR /app

# Copy necessary files from build stages
COPY modules ./modules
COPY pyproject.toml README.md ciroh-bgsafe.png ./

RUN uv venv --python 3.12 && \
    uv pip install --no-cache-dir .\[copycatbmi\]
ENV PATH="/app/.venv/bin:${PATH}"

RUN echo "export PS1='\u\[\033[01;32m\]@ngiab_preprocess\[\033[00m\]:\[\033[01;35m\]\W\[\033[00m\]\$ '" >> ~/.bashrc

ENTRYPOINT ["python","-m","ngiab_data_cli","--output_root=/data"]
