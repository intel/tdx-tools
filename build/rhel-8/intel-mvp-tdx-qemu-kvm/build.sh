#!/bin/bash

set -ex

CURR_DIR="$(dirname "$(readlink -f "$0")")"

UPSTREAM_GIT_URI="https://github.com/qemu/qemu.git"
UPSTREAM_TAG="v7.2.0"

PATCHSET="${CURR_DIR}/../../common/patches-tdx-qemu-MVP-QEMU-7.2-v1.10.tar.gz"
SPEC_FILE="${CURR_DIR}/tdx-qemu.spec"
RPMBUILD_DIR="${CURR_DIR}/rpmbuild"
DOWNSTREAM_TARBALL="${RPMBUILD_DIR}/SOURCES/tdx-qemu.tar.gz"

create_tarball() {
    cd "${CURR_DIR}"
    if [[ ! -d qemu ]]; then
        git clone ${UPSTREAM_GIT_URI} qemu
    fi
    if [[ ! -f ${DOWNSTREAM_TARBALL} ]]; then
        tar xf "${PATCHSET}"
        pushd qemu
        git checkout ${UPSTREAM_TAG}
        git config user.name "${USER:-tdx-builder}"
        git config user.email "${USER:-tdx-builder}"@"$HOSTNAME"
        for i in ../patches/*; do
           git am "$i"
        done
        git submodule update --init
        popd
        tar --exclude=.git -czf "${DOWNSTREAM_TARBALL}" qemu
    fi
}

prepare() {
    echo "Prepare..."
}

build() {
    echo "Build..."
    sudo -E dnf builddep -y "${SPEC_FILE}"
    rpmbuild --define "_topdir ${RPMBUILD_DIR}" --undefine=_disable_source_fetch -v -ba "${SPEC_FILE}"
}

mkdir -p "${RPMBUILD_DIR}"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
create_tarball
prepare
build
