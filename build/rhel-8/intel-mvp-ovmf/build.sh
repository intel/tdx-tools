#!/bin/bash

set -e

CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_GIT_URI="https://github.com/tianocore/edk2.git"
UPSTREAM_TAG="edk2-stable202302"
SPEC_FILE="${CURR_DIR}/ovmf.spec"
RPMBUILD_DIR="${CURR_DIR}/rpmbuild"

get_origin() {
    echo "**** Download origin package ****"
    if [[ ! -f ${CURR_DIR}/edk2.tar.gz ]]; then
        git clone --branch ${UPSTREAM_TAG} ${UPSTREAM_GIT_URI}
        pushd edk2
        git submodule init
        git submodule sync
        git submodule update
        rm -rf .git/
        popd
        tar czf edk2.tar.gz edk2
    fi
}

prepare() {
    echo "**** Prepare ****"
    cp "${CURR_DIR}/edk2.tar.gz" "${RPMBUILD_DIR}/SOURCES/"
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
