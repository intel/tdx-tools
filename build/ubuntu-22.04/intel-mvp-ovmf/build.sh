#!/bin/bash

set -e

CURR_DIR=$(dirname "$(readlink -f "$0")")
UPSTREAM_GIT_URI="https://github.com/tianocore/edk2.git"
UPSTREAM_TAG="0be81a4d83810cdb018d293bc264f489e7664043"

REPO_FOLDER="ovmf-0be81a4"

get_origin() {
    echo "**** Download origin package ****"
    cd "${CURR_DIR}"
    if [[ ! -f ${CURR_DIR}/edk2.tar.gz ]]; then
        git clone --single-branch ${UPSTREAM_GIT_URI} ${REPO_FOLDER}
        pushd ${REPO_FOLDER}
        git checkout ${UPSTREAM_TAG}
        git submodule init
        git submodule sync
        git submodule update
        rm -rf .git/
        popd
        tar czf edk2.tar.gz ${REPO_FOLDER}
    fi
}

prepare() {
    echo "**** Prepare ****"
    cp "${CURR_DIR}"/edk2.tar.gz "${CURR_DIR}"/${REPO_FOLDER}
    cp "${CURR_DIR}"/debian/ "${CURR_DIR}"/${REPO_FOLDER} -fr
    tar -zxf edk2.tar.gz --strip-components=1 --directory "${CURR_DIR}"/${REPO_FOLDER}
}

build() {
    echo "**** Build ****"
    cd "${CURR_DIR}"/${REPO_FOLDER}
    sudo -E mk-build-deps --install --build-dep --build-indep '--tool=apt-get --no-install-recommends -y' debian/control
    dpkg-source --before-build .
    debuild -uc -us -b
}

pushd "$CURR_DIR"
mkdir -p "${CURR_DIR}"/${REPO_FOLDER}
get_origin
prepare
build
popd

