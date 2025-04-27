#Copied from https://github.com/kubernetes-sigs/blixt/blob

FROM alpine

WORKDIR /opt/blixt/

LABEL org.opencontainers.image.source=https://github.com/kubernetes-sigs/blixt
LABEL org.opencontainers.image.licenses=GPL-2.0-only,BSD-2-Clause

COPY dataplane/LICENSE.GPL-2.0 /opt/blixt/LICENSE.GPL-2.0
COPY dataplane/LICENSE.BSD-2-Clause /opt/blixt/LICENSE.BSD-2-Clause