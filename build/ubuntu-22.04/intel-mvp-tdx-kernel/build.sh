#!/bin/bash

set -ex

UPSTREAM_GIT_URI="https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git"
UPSTREAM_TAG="v5.19.17"

CURR_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=${CURR_DIR}/"mvp-tdx-kernel-${UPSTREAM_TAG}"
PATCHSET="${CURR_DIR}/../../common/patches-tdx-kernel-MVP-KERNEL-5.19.17-v4.0.tar.gz"

if [[ $(grep "Ubuntu" /etc/os-release) == "" ]]; then
    echo "Please build the packages in Ubuntu"
    exit 1
fi

get_source() {
    echo "Get upstream source code..."
    if [[ ! -d ${SOURCE_DIR} ]]; then
        git clone  -b ${UPSTREAM_TAG} --single-branch --depth 1 ${UPSTREAM_GIT_URI} "${SOURCE_DIR}"
        cd "${SOURCE_DIR}"
        tar xf "${PATCHSET}"
        git config user.name "${USER:-tdx-builder}"
        git config user.email "${USER:-tdx-builder}"@"${HOSTNAME}"
        for i in patches/*; do
            git am "$i"
        done
        git submodule update --init
    fi
}

prepare() {
    echo "Prepare..."

    cp "${CURR_DIR}"/debian/ "${SOURCE_DIR}" -fr
    cp "${CURR_DIR}"/debian.master/ "${SOURCE_DIR}" -fr
    cp "${CURR_DIR}"/linux-5.19.17/* "${SOURCE_DIR}" -fr

    sudo apt update
    sudo DEBIAN_FRONTEND=noninteractive TZ=Asia/Shanghai apt install tzdata -y
}

build() {
    echo "Build..."
    cd "${SOURCE_DIR}"
    sudo -E mk-build-deps --install --build-dep --build-indep '--tool=apt-get --no-install-recommends -y' debian/control
    dpkg-source --before-build .
    debuild -uc -us -b
}

pushd "${CURR_DIR}"
get_source
prepare
build
popd
