# Pinned base image; tool versions come from the Ubuntu 24.04 archive.
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential cmake ninja-build git ca-certificates \
      gcc-arm-none-eabi libnewlib-arm-none-eabi \
      cppcheck gcovr python3 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /work
