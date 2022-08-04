#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

FROM python:3.8-slim-buster 

# Requirements as per https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html
RUN apt-get update \
 && apt-get install -y bzip2 xz-utils zlib1g libxml2-dev libxslt1-dev libgomp1 libpopt0\
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create directory for scancode sources
RUN mkdir scancode-toolkit

# Copy sources into docker container
COPY . scancode-toolkit

# Set workdir
WORKDIR scancode-toolkit

# Run scancode once for initial configuration, with --reindex-licenses to create the base license index
RUN ./scancode --reindex-licenses

# Add scancode to path
ENV PATH=$HOME/scancode-toolkit:$PATH

# Set entrypoint to be the scancode command, allows to run the generated docker image directly with the scancode arguments: `docker run (...) <containername> <scancode arguments>`
ENTRYPOINT ["./scancode"]
