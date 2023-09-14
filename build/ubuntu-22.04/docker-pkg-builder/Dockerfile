FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install --no-install-recommends --yes build-essential \
        fakeroot devscripts wget git equivs liblz4-tool sudo python-is-python3 \
        pkg-config unzip curl xz-utils binutils cpio rpm2cpio python3-dev \
        nasm llvm clang ocaml ocamlbuild

# rust env
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > rustup-init.sh && \
    chmod a+x rustup-init.sh
RUN ./rustup-init.sh -y --profile minimal --default-toolchain nightly-2023-08-28

ENV PATH=$PATH:/root/.cargo/bin   
RUN cargo install cargo-xbuild && \
    rustup component add rust-src
