#!/bin/bash

set -ex

CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_GIT_URI="https://github.com/tianocore/edk2-staging.git"
UPSTREAM_TAG="2023-tdvf-ww36.2"
SPEC_FILE="${CURR_DIR}/ovmf.spec"
RPMBUILD_DIR="${CURR_DIR}/rpmbuild"
PACKAGE_SRC="mvp-tdx-ovmf"

get_origin() {
    echo "**** Download origin package ****"
    if [[ ! -d ${CURR_DIR}/${PACKAGE_SRC} ]]; then
        git clone --branch ${UPSTREAM_TAG} ${UPSTREAM_GIT_URI} ${PACKAGE_SRC}
        pushd ${PACKAGE_SRC}
        git submodule init
        git submodule sync
        git submodule update
        git apply ../0001*.patch
        popd
    fi
}

prepare() {
    echo "**** Prepare ****"
    tar --exclude=.git -czf "${RPMBUILD_DIR}/SOURCES/${PACKAGE_SRC}.tar.gz" ${PACKAGE_SRC}
}

build() {
    echo "**** Build ****"
    sudo -E dnf builddep -y "${SPEC_FILE}"
    rpmbuild --define "_topdir ${RPMBUILD_DIR}" -v -ba "${SPEC_FILE}"
}

pushd "$CURR_DIR"
mkdir -p "${RPMBUILD_DIR}"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
get_origin
prepare
build
popd
