#!/bin/bash

set -e

CURR_DIR="$(dirname "$(readlink -f "$0")")"
UPSTREAM_URI="https://download.qemu.org/qemu-6.0.0-rc1.tar.bz2"
UPSTREAM_VERSION="6.0.0-rc1"
UPSTREAM_BASE_COMMIT="6d40ce00c1166c317e298ad82ecf10e650c4f87d"
DOWNSTREAM_GIT_URI="https://github.com/intel/qemu-tdx.git"
DOWNSTREAM_TAG="tdx-qemu-2021.11.29-v6.0.0-rc1-mvp"
UPTRREAM_FILE="${UPSTREAM_URI##*/}"
DOWNSTREAM_VERSION=$(echo $DOWNSTREAM_TAG|cut -d'-' -f 3)
PATCHES_TARBALL_NAME="patches-tdx-qemu-${UPSTREAM_VERSION}-${DOWNSTREAM_VERSION}.tar.gz"
SPEC_FILE="${CURR_DIR}/tdx-qemu.spec"
RPMBUILD_DIR=${CURR_DIR}/rpmbuild

get_origin() {
    echo "**** Download origin package ****"
    if [[ ! -f ${RPMBUILD_DIR}/SOURCES/${UPTRREAM_FILE} ]]; then
        wget -O ${UPTRREAM_FILE} ${UPSTREAM_URI}
        mv ${UPTRREAM_FILE} "${RPMBUILD_DIR}"/SOURCES
    fi

    if [[ ! -f qemu-kvm-2.12.0-88.module_el8.1.0+266+ba744077.2.src.rpm ]]; then
        wget https://vault.centos.org/8.1.1911/AppStream/Source/SPackages/qemu-kvm-2.12.0-88.module_el8.1.0+266+ba744077.2.src.rpm
    fi
    pushd "${RPMBUILD_DIR}"/SOURCES
    rpm2cpio "${CURR_DIR}"/qemu-kvm-2.12.0-88.module_el8.1.0+266+ba744077.2.src.rpm | cpio -idmv
    popd
}

generate_patchset() {
    echo "**** Create patchset ****"
    if [[ ! -d qemu-tdx ]]; then
        git clone --single-branch --branch ${DOWNSTREAM_TAG} ${DOWNSTREAM_GIT_URI}
    fi
    if [[ ! -f "${RPMBUILD_DIR}"/SOURCES/"${PATCHES_TARBALL_NAME}" ]]; then
        mkdir -p patches
        pushd qemu-tdx
        git format-patch -q $UPSTREAM_BASE_COMMIT..$DOWNSTREAM_TAG -o ../patches
        popd
        tar czf "${RPMBUILD_DIR}"/SOURCES/"${PATCHES_TARBALL_NAME}" patches/
    fi
}

prepare() {
    echo "Prepare..."
}

build() {
    echo "Build..."
    sudo -E dnf builddep -y "${SPEC_FILE}"
    rpmbuild --define "_topdir ${RPMBUILD_DIR}" -v -ba "${SPEC_FILE}"
}

pushd "${CURR_DIR}"
mkdir -p "${RPMBUILD_DIR}"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
get_origin
generate_patchset
prepare
build
popd
