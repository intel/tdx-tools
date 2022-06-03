#!/bin/bash

# set -ex

CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_VERSION="5.15"
DOWNSTREAM_GIT_URI="https://github.com/intel/linux-kernel-dcp.git"

DOWNSTREAM_TAG="SPR-BKC-PC-v8.5"
PACKAGE="mvp-linux-kernel"

get_source() {
    echo "Get downstream source code..."
    cd ${CURR_DIR}
    if [[ ! -d ${PACKAGE}-${UPSTREAM_VERSION} ]]; then
	git config --global --add safe.directory /github/workspace
	git config --global --add safe.directory /repo
        git clone --branch ${DOWNSTREAM_TAG} --single-branch --depth 1 \
            ${DOWNSTREAM_GIT_URI} ${PACKAGE}-${UPSTREAM_VERSION}
        cd ${PACKAGE}-${UPSTREAM_VERSION}
        git submodule update --init
    fi
}

prepare() {
    echo "Prepare..."
    cp ${CURR_DIR}/debian/ ${CURR_DIR}/${PACKAGE}-${UPSTREAM_VERSION} -fr
    cp ${CURR_DIR}/debian.master/ ${CURR_DIR}/${PACKAGE}-${UPSTREAM_VERSION} -fr
    cp ${CURR_DIR}/linux-5.15.0/* ${CURR_DIR}/${PACKAGE}-${UPSTREAM_VERSION} -fr

    sudo apt update
    sudo apt install software-properties-common -y
    sudo add-apt-repository "deb-src http://linux-ftp.sh.intel.com/pub/mirrors/ubuntu/ jammy main multiverse universe restricted" -y -s
    sudo DEBIAN_FRONTEND=noninteractive TZ=Asia/Shanghai apt install tzdata -y
}

build() {
    echo "Build..."
    cd ${CURR_DIR}/${PACKAGE}-${UPSTREAM_VERSION}
    sudo -E mk-build-deps --install --build-dep --build-indep '--tool=apt-get --no-install-recommends -y' debian/control
    dpkg-source --before-build .
    debuild -uc -us -b
}

get_source
prepare
build
