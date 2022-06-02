#!/bin/bash

set -ex

CURR_DIR="$(dirname "$(readlink -f "$0")")"

DOWNSTREAM_GIT_URI="https://github.com/intel/linux-kernel-dcp.git"
DOWNSTREAM_TAG="SPR-BKC-PC-v8.8"

SPEC_FILE="${CURR_DIR}/spr-kernel.spec"
RPMBUILD_DIR="${CURR_DIR}/rpmbuild"

# Workaround to empty files not being downloadable
EMPTY_SOURCES=" \
    Module.kabi_aarch64 \
    Module.kabi_ppc64le \
    Module.kabi_s390x \
    Module.kabi_x86_64 \
    Module.kabi_dup_aarch64 \
    Module.kabi_dup_ppc64le \
    Module.kabi_dup_s390x \
    Module.kabi_dup_x86_64 \
    "

prepare() {
    echo "Prepare..."

    if [[ ! -f "${RPMBUILD_DIR}/SOURCES/linux-spr-kernel.tar.gz" ]]; then
        if [[ ! -d linux-spr-kernel ]]; then
            git clone -b ${DOWNSTREAM_TAG} --single-branch ${DOWNSTREAM_GIT_URI} linux-spr-kernel
        fi
        tar --exclude=.git -czf linux-spr-kernel.tar.gz linux-spr-kernel
        mv linux-spr-kernel.tar.gz "${RPMBUILD_DIR}"/SOURCES/
    fi

    cp "${CURR_DIR}"/*.config "${RPMBUILD_DIR}"/SOURCES/
    cp "${CURR_DIR}"/extra-sources/* "${RPMBUILD_DIR}"/SOURCES/
    for f in $EMPTY_SOURCES; do
        echo "" > "${RPMBUILD_DIR}"/SOURCES/"$f"
    done
}

build() {
    echo "Build..."
    sudo -E dnf builddep -y "${SPEC_FILE}"
    rpmbuild --define "_topdir ${RPMBUILD_DIR}" --undefine=_disable_source_fetch -v -ba "${SPEC_FILE}"
}

pushd "${CURR_DIR}"
mkdir -p "${RPMBUILD_DIR}"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
prepare
build
popd
