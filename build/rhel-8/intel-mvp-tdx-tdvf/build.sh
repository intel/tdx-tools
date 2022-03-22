#!/bin/bash

set -e

CURR_DIR=$(dirname "$(readlink -f "$0")")
DOWNSTREAM_GIT_URI="https://github.com/tianocore/edk2-staging.git"
DOWNSTREAM_TAG="2021-ww50.5"
SPEC_FILE="${CURR_DIR}/tdvf.spec"
RPMBUILD_DIR="${CURR_DIR}/rpmbuild"

get_origin() {
    echo "**** Download origin package ****"
    if [[ ! -f ${CURR_DIR}/edk2.tar.gz ]]; then
        git clone --single-branch --branch ${DOWNSTREAM_TAG} \
            ${DOWNSTREAM_GIT_URI}
        pushd edk2-staging
	    git submodule set-url UnitTestFrameworkPkg/Library/CmockaLib/cmocka \
            https://github.com/clibs/cmocka
        git submodule init
        git submodule sync
        git submodule update
        rm -rf .git/
        popd
        tar czf edk2.tar.gz edk2-staging/
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
