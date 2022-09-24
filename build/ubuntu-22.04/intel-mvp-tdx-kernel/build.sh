#!/bin/bash

# set -ex

CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_VERSION="5.15"
DOWNSTREAM_GIT_URI="https://github.com/intel/linux-kernel-dcp.git"

DOWNSTREAM_TAG="710bb135da47ea71464198b9017e1c3f7e71f645"
PACKAGE="mvp-tdx-kernel"

if [[ $(grep "Ubuntu" /etc/os-release) == "" ]]; then
    echo "Please build the packages in Ubuntu"
    exit 1
fi

get_source() {
    echo "Get downstream source code..."
    cd ${CURR_DIR}
    if [[ ! -d ${PACKAGE}-${UPSTREAM_VERSION} ]]; then
	# add safe directory for running in docker
	git config --global --add safe.directory /github/workspace
	git config --global --add safe.directory /repo
        git clone ${DOWNSTREAM_GIT_URI} ${PACKAGE}-${UPSTREAM_VERSION}
        cd ${PACKAGE}-${UPSTREAM_VERSION}
        git checkout ${DOWNSTREAM_TAG}
        git submodule update --init
    fi
}

prepare() {
    echo "Prepare..."
    cp ${CURR_DIR}/debian/ ${CURR_DIR}/${PACKAGE}-${UPSTREAM_VERSION} -fr
    cp ${CURR_DIR}/debian.master/ ${CURR_DIR}/${PACKAGE}-${UPSTREAM_VERSION} -fr
    cp ${CURR_DIR}/linux-5.15.0/* ${CURR_DIR}/${PACKAGE}-${UPSTREAM_VERSION} -fr

    sudo apt update
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
