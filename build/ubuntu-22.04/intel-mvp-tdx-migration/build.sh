#!/bin/bash

set -e

CURR_DIR=$(dirname "$(readlink -f "$0")")
GIT_URI="https://github.com/intel/MigTD.git"
GIT_TAG="v0.3.0"
PKG_DIR="${CURR_DIR}"/migtd

get_source() {
    echo "Get upstream source code..."

    cd ${CURR_DIR}
    if [[ ! -d ${PKG_DIR} ]]; then
        git clone --single-branch --branch ${GIT_TAG} ${GIT_URI} ${PKG_DIR}
        pushd ${PKG_DIR}
        git submodule update --init --recursive
        popd
    fi
}

prepare() {
    echo "Prepare..."
    cp "${CURR_DIR}"/debian/ "${PKG_DIR}"/ -fr

    # Github runner overrides to /github/home
    user_id=$(id -u)
    if [ "$user_id" -eq 0 ]; then
        export HOME=/root
    fi

    # install rust and deps
    if [[ $($HOME/.cargo/bin/cargo --version) =~ 1.74.0-nightly ]]; then
        echo "Found Cargo 1.74.0-nightly in $HOME/.cargo/"
    else
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > rustup-init.sh
        chmod a+x rustup-init.sh
        ./rustup-init.sh -y --profile minimal --default-toolchain nightly-2023-08-28
    fi

    source $HOME/.cargo/env
    # install cargo xbuild
    cargo_build=$(cargo --list | grep xbuild | wc -l)
    if [[ $cargo_build == 0 ]]; then
        cargo install cargo-xbuild
    fi

    # install rust src
    rust_src=$(rustup component list | grep rust-src | wc -l)
    if [[ $rust_src == 0 ]]; then
        rustup component add rust-src
    fi

    sudo apt install nasm llvm clang ocaml ocamlbuild -y
}

build() {
    echo "Build..."
    cd "${PKG_DIR}"
    ./sh_script/preparation.sh
    cargo image
    cargo hash --image target/release/migtd.bin > ./migtd.servtd_info_hash
    dpkg-source --before-build .
    debuild -uc -us -b
}

get_source
prepare
build
