#!/bin/bash

set -ex

CURR_DIR="$(dirname "$(readlink -f "$0")")"

DOWNSTREAM_GIT_URI="https://github.com/intel/qemu-dcp.git"
DOWNSTREAM_TAG="c8302707f6e89c955eae0883bfd97680202b8db2"
DOWNSTREAM_TARBALL="tdx-qemu.tar.gz"

SPEC_FILE="${CURR_DIR}/tdx-qemu.spec"
RPMBUILD_DIR="${CURR_DIR}/rpmbuild"

create_tarball() {
    cd "${CURR_DIR}"
    if [[ ! -d qemu ]]; then
        git clone ${DOWNSTREAM_GIT_URI} qemu
    fi
    if [[ ! -f "${RPMBUILD_DIR}"/SOURCES/${DOWNSTREAM_TARBALL} ]]; then
        pushd qemu
        git checkout ${DOWNSTREAM_TAG}
        git submodule update --init
        rm -rf .git/
        popd
        tar czf "${RPMBUILD_DIR}"/SOURCES/${DOWNSTREAM_TARBALL} qemu
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
