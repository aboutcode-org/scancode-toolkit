#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

FROM python:3.6-slim-buster 

# Requirements as per https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html
RUN apt-get update \
 && apt-get install -y bzip2 xz-utils zlib1g libxml2-dev libxslt1-dev libgomp1 \
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
