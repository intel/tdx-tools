FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install --no-install-recommends --yes build-essential \
        fakeroot devscripts wget git equivs liblz4-tool sudo python-is-python3 \
        pkg-config unzip curl xz-utils binutils cpio rpm2cpio python3-dev mini-dinstall
