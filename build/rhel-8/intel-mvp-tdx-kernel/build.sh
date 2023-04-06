#!/bin/bash

set -ex

CURR_DIR="$(dirname "$(readlink -f "$0")")"

UPSTREAM_GIT_URI="https://github.com/torvalds/linux.git"
UPSTREAM_TAG="v6.2"

PATCHSET="${CURR_DIR}/../../common/patches-tdx-kernel-MVP-KERNEL-6.2-v1.8.tar.gz"
SPEC_FILE="${CURR_DIR}/tdx-kernel.spec"
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

    if [[ ! -f "${RPMBUILD_DIR}/SOURCES/linux-tdx-kernel.tar.gz" ]]; then
        if [[ ! -d linux-tdx-kernel ]]; then
            git clone -b ${UPSTREAM_TAG} --single-branch --depth 1 ${UPSTREAM_GIT_URI} linux-tdx-kernel
            tar xf "${PATCHSET}"
            cd linux-tdx-kernel
            git config user.name "${USER:-tdx-builder}"
            git config user.email "${USER:-tdx-builder}"@"$HOSTNAME"
            for i in ../patches/*; do
                git am "$i"
            done
            cd -
        fi
        tar --exclude=.git -czf linux-tdx-kernel.tar.gz linux-tdx-kernel
        mv linux-tdx-kernel.tar.gz "${RPMBUILD_DIR}"/SOURCES/
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
    rpmbuild --define "_topdir ${RPMBUILD_DIR}" --undefine=_disable_source_fetch -v -ba "${SPEC_FILE}" --without guest
}

pushd "${CURR_DIR}"
mkdir -p "${RPMBUILD_DIR}"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
prepare
build
popd
