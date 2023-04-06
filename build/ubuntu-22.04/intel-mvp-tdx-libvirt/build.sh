#!/bin/bash

set -e

CURR_DIR=$(dirname "$(readlink -f "$0")")

UPSTREAM_URI="https://libvirt.org/sources/libvirt-8.6.0.tar.xz"
UPSTREAM_VERSION="8.6.0"
UPSTREAM_BASE_COMMIT="f8b6c7e59afd1b700d446239922ee097a6f1433c"
DOWNSTREAM_GIT_URI="https://github.com/intel/libvirt-tdx.git"
DOWNSTREAM_TAG="tdx-libvirt-2022.11.17"

PACKAGE="tdx-libvirt"
PACKAGE_VERSION="2022.11.17"

UPTRREAM_FILE="${UPSTREAM_URI##*/}"
DOWNSTREAM_VERSION=${DOWNSTREAM_TAG#tdx-libvirt-}
PATCHES_TARBALL_NAME="patches-tdx-libvirt-${UPSTREAM_VERSION}-${DOWNSTREAM_VERSION}.tar.gz"

get_origin() {
    echo "**** Download origin package ****"
    if [[ ! -f ${PACKAGE}-${PACKAGE_VERSION}/${UPTRREAM_FILE} ]]; then
        wget -O ${UPTRREAM_FILE} ${UPSTREAM_URI}
        mv ${UPTRREAM_FILE} ${PACKAGE}-${PACKAGE_VERSION}
    fi
}

generate_patchset() {
    echo "**** Create patchset ****"
    if [[ ! -d libvirt ]]; then
        git clone -b ${DOWNSTREAM_TAG} --single-branch ${DOWNSTREAM_GIT_URI} libvirt
    fi
    pushd libvirt
    if [[ ! -f ${CURR_DIR}/${PACKAGE}-${PACKAGE_VERSION}/${PATCHES_TARBALL_NAME} ]]; then
        git format-patch $UPSTREAM_BASE_COMMIT..$DOWNSTREAM_TAG
        cp "${CURR_DIR}/1001-Add-private-memfd-host-memory-backend-for-QEMU.patch" .
        tar czf "${CURR_DIR}"/${PACKAGE}-${PACKAGE_VERSION}/${PATCHES_TARBALL_NAME} ./*.patch
    fi
    popd
}

prepare() {
    echo "**** Prepare ****"
    cp "${CURR_DIR}"/debian/ "${CURR_DIR}"/${PACKAGE}-${PACKAGE_VERSION} -fr
    cd "${CURR_DIR}"/${PACKAGE}-${PACKAGE_VERSION}
    tar -xf libvirt-${UPSTREAM_VERSION}.tar.xz --strip-components=1 --directory \
        "${CURR_DIR}"/${PACKAGE}-${PACKAGE_VERSION}
}

build() {
    echo "**** Build ****"
    cd "${CURR_DIR}"/${PACKAGE}-${PACKAGE_VERSION}
    echo "Patch..."
    if [[ ! -f patch.done ]]; then
        for p in ../libvirt/*.patch; do
           [ -f "$p" ] || break
           patch -N -p1 -i "$p"
        done
        touch patch.done
    fi
    sudo -E mk-build-deps --install --build-dep --build-indep \
        '--tool=apt-get --no-install-recommends -y' debian/control
    dpkg-source --before-build .
    debuild -uc -us -b
}

pushd "${CURR_DIR}"
mkdir -p "${CURR_DIR}"/${PACKAGE}-${PACKAGE_VERSION}
get_origin
generate_patchset
prepare
build
popd
