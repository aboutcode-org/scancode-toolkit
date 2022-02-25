FROM python:3-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        git \
        gnupg2 \
        openssh-client \
        php7.4 \
    && curl -JLO 'https://apt.puppet.com/puppet-tools-release-bullseye.deb' \
    && dpkg -i puppet-tools-release-bullseye.deb \
    && rm puppet-tools-release-bullseye.deb \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        pdk \
    && rm -rf /var/lib/apt/lists/*

# Run with non privileged user
RUN groupadd --gid 1000 user \
    && useradd --uid 1000 --gid user --shell /bin/bash --home-dir /workspace --create-home user
