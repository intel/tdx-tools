#!/bin/bash

set -ex


CURR_DIR=$(dirname "$(readlink -f "$0")")
RPMBUILD_DIR="${CURR_DIR}/rpmbuild"

DOWNSTREAM_GIT_URI="https://github.com/intel/tdx/"
DOWNSTREAM_TAG="tdx-kvm-2021.11.29-v5.12-rc2-mvp"
DOWNSTREAM_VERSION=$(echo $DOWNSTREAM_TAG|cut -d '-' -f 3)

UPSTREAM_URI="https://github.com/torvalds/linux/archive/refs/tags/v5.12-rc2.tar.gz"
UPSTREAM_FILE="${UPSTREAM_URI##*/}"
UPSTREAM_VERSION="5.12-rc2"
UPSTREAM_BASE_COMMIT="a38fd8748464831584a19438cbb3082b5a2dab15"

PATCHES_TARBALL_NAME="patches-tdx-host-kernel-${UPSTREAM_VERSION}-${DOWNSTREAM_VERSION}.tar.gz"
SPEC_FILE="${CURR_DIR}/tdx-host-kernel.spec"

get_origin() {
    echo "Download origin package..."
    cd "${CURR_DIR}"
    if [[ ! -f "${RPMBUILD_DIR}/SOURCES/${UPSTREAM_FILE}" ]]; then
        wget -O "${UPSTREAM_FILE}" ${UPSTREAM_URI}
        mv "${UPSTREAM_FILE}" "${RPMBUILD_DIR}"/SOURCES
    fi
}

generate_patchset() {
    echo "Create patchset ..."
    if [[ ! -d linux ]]; then
        git clone -b ${DOWNSTREAM_TAG} --single-branch ${DOWNSTREAM_GIT_URI} linux
    fi
    if [[ ! -f "${RPMBUILD_DIR}"/SOURCES/"${PATCHES_TARBALL_NAME}" ]]; then
        mkdir -p patches
        pushd linux 
        git format-patch -q $UPSTREAM_BASE_COMMIT..$DOWNSTREAM_TAG -o ../patches
        popd
        tar czf "${RPMBUILD_DIR}"/SOURCES/"${PATCHES_TARBALL_NAME}" patches/
    fi
}

prepare() {
    echo "Prepare..."
    cp "${CURR_DIR}"/*.config "${RPMBUILD_DIR}"/SOURCES/
}

build() {
    echo "Build..."
    sudo -E dnf builddep -y "${SPEC_FILE}"
    rpmbuild --define "_topdir ${RPMBUILD_DIR}" --undefine=_disable_source_fetch -v -ba "${SPEC_FILE}"
}

mkdir -p "${RPMBUILD_DIR}"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
get_origin
generate_patchset
prepare
build
