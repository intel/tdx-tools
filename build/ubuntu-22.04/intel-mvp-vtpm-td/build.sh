#!/bin/bash

set -e

CURR_DIR=$(dirname "$(readlink -f "$0")")
GIT_URI="https://github.com/intel/vtpm-td.git"
GIT_TAG="v0.1.1"
PKG_DIR="${CURR_DIR}"/vtpm-td

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

    if [[ $($HOME/.cargo/bin/cargo --version) =~ 1.67.0-nightly ]]; then
        echo "Found Cargo 1.67.0-nightly in $HOME/.cargo/"
    else
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > rustup-init.sh
        chmod +x rustup-init.sh;./rustup-init.sh -y --profile minimal --default-toolchain nightly-2022-11-15
    fi
    # shellcheck source=/dev/null
    source $HOME/.cargo/env
    cargo install cargo-xbuild
    rustup component add rust-src
    sudo apt install nasm llvm clang ocaml ocamlbuild -y
}

build() {
    echo "Build..."
    pushd "${PKG_DIR}"
    export CC=clang
    export AR=llvm-ar
    source sh_script/pre-build.sh
    source sh_script/build.sh
    popd

    dpkg-source --before-build .
    debuild -uc -us -b
}

get_source
prepare
build
