#!/bin/bash

# set -ex

CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_VERSION="5.15"
DOWNSTREAM_GIT_URI="https://github.com/intel/linux-kernel-dcp.git"

DOWNSTREAM_TAG="SPR-BKC-PC-v8.8"
PACKAGE="mvp-linux-kernel"

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
    sudo add-apt-repository "deb-src http://mirrors.aliyun.com/ubuntu/ jammy main multiverse universe restricted" -y -s
    sudo DEBIAN_FRONTEND=noninteractive TZ=Asia/Shanghai apt install tzdata -y
}

build() {
    cd ${CURR_DIR}/${PACKAGE}-${UPSTREAM_VERSION}
    echo "Patch..."
    # fix BLR-665 Kernel SPR-BKC-PC-v8.8 fails to build on Ubuntu 22.04
    patch -N -p1 -i ${CURR_DIR}/patches/0001-efi-x86-stub-fix-absolute-symbol-reference.patch
    # fix BLR-670 Ubuntu 22.04: kernel panic when enabling TDX
    patch -N -p1 -i ${CURR_DIR}/patches/0001-X86-VIRTEXT-Fix-false-alarm-of-vmptrst-failure-in-ra.patch
    # fix BLR-667 Call trace UBSAN: shift-out-of-bounds in Ubuntu TDX kernel
    patch -N -p1 -i ${CURR_DIR}/patches/0001-x86-MM-Use-pgprot_cc_guest-in-__ioremap_caller-for-T.patch

    echo "Build..."
    sudo -E mk-build-deps --install --build-dep --build-indep '--tool=apt-get --no-install-recommends -y' debian/control
    dpkg-source --before-build .
    debuild -uc -us -b
}

get_source
prepare
build
