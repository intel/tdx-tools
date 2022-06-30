#!/bin/bash

set -e

CURR_DIR=$(dirname "$(readlink -f "$0")")
DOWNSTREAM_GIT_URI="https://github.com/tianocore/edk2-staging.git"
DOWNSTREAM_TAG="tdvf-2022-ww20.1"

PACKAGE="tdx-tdvf"
PACKAGE_VERSION="2022.5.16"

get_origin() {
    echo "**** Download origin package ****"
    cd "${CURR_DIR}"
    if [[ ! -f ${CURR_DIR}/edk2.tar.gz ]]; then
        git clone --single-branch --branch ${DOWNSTREAM_TAG} ${DOWNSTREAM_GIT_URI}
        pushd edk2-staging
        git submodule set-url UnitTestFrameworkPkg/Library/CmockaLib/cmocka https://github.com/clibs/cmocka
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
    cp "${CURR_DIR}"/edk2.tar.gz "${CURR_DIR}"/${PACKAGE}-${PACKAGE_VERSION}
    cp "${CURR_DIR}"/debian/ "${CURR_DIR}"/${PACKAGE}-${PACKAGE_VERSION} -fr
    tar -zxf edk2.tar.gz --strip-components=1 --directory "${CURR_DIR}"/${PACKAGE}-${PACKAGE_VERSION}
}

build() {
    echo "**** Build ****"
    cd "${CURR_DIR}"/${PACKAGE}-${PACKAGE_VERSION}
    sudo -E mk-build-deps --install --build-dep --build-indep '--tool=apt-get --no-install-recommends -y' debian/control
    dpkg-source --before-build .
    debuild -uc -us -b
}

pushd "$CURR_DIR"
mkdir -p "${CURR_DIR}"/${PACKAGE}-${PACKAGE_VERSION}
get_origin
prepare
build
popd

