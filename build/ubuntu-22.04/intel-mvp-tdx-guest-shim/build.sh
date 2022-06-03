#!/bin/bash

CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_URI="https://github.com/rhboot/shim/releases/download/15.4/shim-15.4.tar.bz2"
UPSTREAM_VERSION="15.4"
DOWNSTREAM_GIT_URI="https://github.com/intel/shim-tdx"
DOWNSTREAM_TAG="tdx-guest-ubuntu-20.04-2021.09.27"
PACKAGE="mvp-tdx-guest-shim"

if [[ $(grep "Ubuntu" /etc/os-release) == "" ]]; then
    echo "Please build the packages in Ubuntu"
    exit 1
fi

get_source() {
    echo "Get downstream source code..."
    cd ${CURR_DIR}
    if [[ ! -d ${PACKAGE}-${UPSTREAM_VERSION} ]]; then
        git clone --branch ${DOWNSTREAM_TAG} --single-branch --depth 1 \
            ${DOWNSTREAM_GIT_URI} ${PACKAGE}-${UPSTREAM_VERSION}
        cd ${PACKAGE}-${UPSTREAM_VERSION}
        git submodule update --init
        rm ${PACKAGE}-${UPSTREAM_VERSION}/.git -fr
    fi
}

prepare() {
    echo "Prepare..."
    cp ${CURR_DIR}/debian/ ${CURR_DIR}/${PACKAGE}-${UPSTREAM_VERSION} -fr
    cp ${CURR_DIR}/Makefile ${CURR_DIR}/${PACKAGE}-${UPSTREAM_VERSION}
}

build() {
    echo "Build..."
    cd ${CURR_DIR}/${PACKAGE}-${UPSTREAM_VERSION}
    sudo mk-build-deps --install --build-dep '--tool=apt-get --no-install-recommends -y' debian/control
    # TODO: fail to build source, so build binary only first
    debuild -uc -us -i -I -b
}

get_source
prepare
build
