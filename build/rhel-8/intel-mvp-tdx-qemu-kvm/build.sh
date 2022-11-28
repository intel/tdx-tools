#!/bin/bash

set -ex

CURR_DIR="$(dirname "$(readlink -f "$0")")"

UPSTREAM_GIT_URI="https://github.com/qemu/qemu.git"
UPSTREAM_TAG="ad4c7f529a279685da84297773b4ec8080153c2d"
DOWNSTREAM_TARBALL="tdx-qemu.tar.gz"

PATCHSET="${CURR_DIR}/../../common/patches-tdx-qemu-MVP-QEMU-7.0-v1.2.tar.gz"
SPEC_FILE="${CURR_DIR}/tdx-qemu.spec"
RPMBUILD_DIR="${CURR_DIR}/rpmbuild"

create_tarball() {
    cd "${CURR_DIR}"
    if [[ ! -d qemu ]]; then
        git clone ${UPSTREAM_GIT_URI} qemu
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
        tar --exclude=.git -czf "${RPMBUILD_DIR}"/SOURCES/${DOWNSTREAM_TARBALL} qemu
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
