#!/bin/bash

set -ex

CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_GIT_URI="https://github.com/qemu/qemu.git"
UPSTREAM_TAG="v7.2.0"
PACKAGE="mvp-tdx-qemu-${UPSTREAM_TAG}"
PATCHSET="${CURR_DIR}/../../common/patches-tdx-qemu-MVP-QEMU-7.2-v1.10.tar.gz"

if [[ $(grep "Ubuntu" /etc/os-release) == "" ]]; then
    echo "Please build the packages in Ubuntu"
    exit 1
fi

get_source() {
    echo "Get downstream source code..."
    cd "${CURR_DIR}"
    if [[ ! -d ${PACKAGE} ]]; then
        git clone ${UPSTREAM_GIT_URI} ${PACKAGE}
        tar xf "${PATCHSET}"
        cd ${PACKAGE}
        git checkout ${UPSTREAM_TAG}
        git config user.name "${USER:-tdx-builder}"
        git config user.email "${USER:-tdx-builder}"@"$HOSTNAME"
        for i in ../patches/*; do
           git am "$i"
        done
        git submodule update --init
    fi
}

prepare() {
    echo "Prepare..."
    cp "${CURR_DIR}"/debian/ "${CURR_DIR}"/"${PACKAGE}" -fr

    sudo apt update
    sudo apt install systemd -y
    sudo DEBIAN_FRONTEND=noninteractive TZ=Asia/Shanghai apt install tzdata libcapstone-dev -y
}

build() {
    echo "Build..."
    cd "${CURR_DIR}"/"${PACKAGE}"
    sudo -E mk-build-deps --install --build-dep --build-indep '--tool=apt-get --no-install-recommends -y' debian/control
    dpkg-source --before-build .
    debuild -uc -us -b
}

get_source
prepare
build
