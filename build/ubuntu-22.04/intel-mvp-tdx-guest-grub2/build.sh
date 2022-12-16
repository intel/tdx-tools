#!/bin/bash

CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_VERSION="2.06"
DOWNSTREAM_GIT_URI="https://github.com/intel/grub-tdx"
DOWNSTREAM_TAG="tdx-guest-ubuntu-22.04-2021.12.27"
PACKAGE="mvp-tdx-guest-grub2"

if [[ $(grep "Ubuntu" /etc/os-release) == "" ]]; then
    echo "Please build the packages in Ubuntu"
    exit 1
fi

get_source() {
    echo "Get downstream source code..."
    cd "${CURR_DIR}"
    if [[ ! -d ${PACKAGE}-${UPSTREAM_VERSION} ]]; then
	git config --global --add safe.directory /github/workspace
        git clone --branch ${DOWNSTREAM_TAG} --single-branch --depth 1 \
            ${DOWNSTREAM_GIT_URI} ${PACKAGE}-${UPSTREAM_VERSION}
        cd "${PACKAGE}-${UPSTREAM_VERSION}"
        git submodule update --init
    fi
}

prepare() {
    echo "Prepare..."
    cp "${CURR_DIR}"/debian/ "${CURR_DIR}"/${PACKAGE}-${UPSTREAM_VERSION} -fr
}

build() {
    echo "Build..."
    cd "${CURR_DIR}"/${PACKAGE}-${UPSTREAM_VERSION}
    GNULIB_URL=https://github.com/coreutils/gnulib.git ./bootstrap
    sudo mk-build-deps --install --build-dep '--tool=apt-get --no-install-recommends -y' debian/control
    dpkg-source --before-build .
    debuild -uc -us -b
}

get_source
prepare
build
