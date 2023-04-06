#!/bin/bash

set -e

CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_URI="https://libvirt.org/sources/libvirt-8.6.0.tar.xz"
UPSTREAM_VERSION="8.6.0"
UPSTREAM_BASE_COMMIT="f8b6c7e59afd1b700d446239922ee097a6f1433c"
DOWNSTREAM_GIT_URI="https://github.com/intel/libvirt-tdx.git"
DOWNSTREAM_TAG="tdx-libvirt-2022.11.17"
UPTRREAM_FILE="${UPSTREAM_URI##*/}"
DOWNSTREAM_VERSION=${DOWNSTREAM_TAG#tdx-libvirt-}
PATCHES_TARBALL_NAME="patches-tdx-libvirt-${UPSTREAM_VERSION}-${DOWNSTREAM_VERSION}.tar.gz"
SPEC_FILE="${CURR_DIR}/tdx-libvirt.spec"
RPMBUILD_DIR="${CURR_DIR}/rpmbuild"

get_origin() {
    echo "**** Download origin package ****"
    if [[ ! -f "${RPMBUILD_DIR}"/SOURCES/"${UPTRREAM_FILE}" ]]; then
        wget -O "${UPTRREAM_FILE}" ${UPSTREAM_URI}
        mv "${UPTRREAM_FILE}" "${RPMBUILD_DIR}"/SOURCES
    fi
}

generate_patchset() {
    echo "**** Create patchset ****"
    if [[ ! -d libvirt ]]; then
        git clone -b ${DOWNSTREAM_TAG} --single-branch ${DOWNSTREAM_GIT_URI} libvirt
    fi
    pushd libvirt
    if [[ ! -f "${RPMBUILD_DIR}"/SOURCES/"${PATCHES_TARBALL_NAME}" ]]; then
        git format-patch $UPSTREAM_BASE_COMMIT..$DOWNSTREAM_TAG
        cp "${CURR_DIR}/1001-Add-private-memfd-host-memory-backend-for-QEMU.patch" .
        tar czf "${RPMBUILD_DIR}"/SOURCES/"${PATCHES_TARBALL_NAME}" ./*.patch
    fi
    popd
}

build() {
    echo "**** Build ****"
    sudo -E dnf builddep -y "${SPEC_FILE}"
    rpmbuild --define "_topdir ${RPMBUILD_DIR}" -v -ba "${SPEC_FILE}"
}

pushd "${CURR_DIR}"
mkdir -p "${RPMBUILD_DIR}"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
get_origin
generate_patchset
build
popd
