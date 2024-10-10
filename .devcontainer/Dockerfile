ARG PYTHON_VERSION="3.10"
FROM python:${PYTHON_VERSION}-slim

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        coreutils \
        curl \
        dialog \
        dirmngr \
        gcc \
        git \
        gnupg2 \
        iproute2 \
        libssl1.1 \
        libxml2-dev \
        libxslt-dev \
        openssh-client \
        procps \
        psmisc \
        rsync \
        sudo \
        unzip \
        wget \
        zip \
        zlib1g \
        libz-dev \
    && rm -rf /var/lib/apt/lists/*

# Install common python tools for development
RUN pip install \
        autopep8 \
        black \
        flake8 \
        mypy \
        poetry \
        pre-commit \
        pylint

ARG USERNAME=vscode
ARG USER_ID=1000
ARG USER_GID=$USER_ID

# Run with non privileged user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd \
        --uid $USER_ID \
        --gid $USER_GID \
        --shell /bin/bash \
        --create-home $USERNAME

# sudo support
RUN echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

ENV CONFIGURE_SUPPORTED_PYTHON=${PYTHON_VERSION}

USER $USERNAME
