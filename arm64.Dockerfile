FROM ubuntu:noble

RUN apt update \
 && apt install -y git curl build-essential libgeos-dev
# Install UV and setup cargo bin for rust tools (uv and cargo)
ENV PATH="/root/.cargo/bin:${PATH}"
ENV UV_INSTALL_DIR=/root/.cargo/bin
ENV UV_COMPILE_BYTECODE=1
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN uv self update

# create this...
WORKDIR /data

WORKDIR /app

# Copy necessary files from build stages
COPY modules ./modules
COPY pyproject.toml README.md ciroh-bgsafe.png ./

# RUN uv venv --python 3.13
RUN uv venv --python 3.13 && \
    uv pip install --no-cache-dir .\[copycatbmi\]

ENV PATH="/app/.venv/bin:${PATH}"

RUN echo "export PS1='\u\[\033[01;32m\]@ngiab_preprocess\[\033[00m\]:\[\033[01;35m\]\W\[\033[00m\]\$ '" >> ~/.bashrc

ENTRYPOINT ["python","-m","ngiab_data_cli","--output_root=/data"]
