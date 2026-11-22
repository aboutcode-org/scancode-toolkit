FROM python:3.12-slim AS builder
LABEL org.opencontainers.image.title="Builder Stage" org.opencontainers.image.version="1.0.0"
RUN echo building
FROM alpine:3.19
LABEL org.opencontainers.image.title="Final Stage" org.opencontainers.image.version="2.0.0"
