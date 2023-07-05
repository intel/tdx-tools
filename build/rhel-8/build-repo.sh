#!/bin/bash

set -e
set -o pipefail

THIS_DIR=$(dirname "$(readlink -f "$0")")
STATUS_DIR="${THIS_DIR}/build-status"
LOG_DIR="${THIS_DIR}/build-logs"

PACKAGES_GUEST=( \
    intel-mvp-tdx-guest-grub2 \
    intel-mvp-tdx-guest-shim \
    )

PACKAGES_HOST=( \
    intel-mvp-tdx-kernel \
    intel-mvp-tdx-qemu-kvm \
    intel-mvp-tdx-libvirt \
    intel-mvp-ovmf \
    intel-mvp-tdx-migration \
    intel-mvp-vtpm-td \
    )

# For packages which need to be moved from host build to guest repo
PACKAGES_SPECIAL=( \
    intel-mvp-tdx-kernel \	
    )
    

build_repo() {
    packages=("${@:2}")
    repo_type=$1
    mkdir -p "${THIS_DIR}"/repo/"${repo_type}"/src

    for package in "${packages[@]}"; do
        pushd "${THIS_DIR}"/"${package}" || exit 1
        if [[ ! -f "$STATUS_DIR/build-${package}.done" ]]; then
            ./build.sh 2>&1 | tee "$LOG_DIR/build-${package}.log"
            touch "$STATUS_DIR/build-${package}.done"
            cp ./rpmbuild/RPMS/* ../repo/"${repo_type}"/ -fr
            cp ./rpmbuild/SRPMS/* ../repo/"${repo_type}"/src -fr
        fi
        popd || exit 1
    done
}

move_packages() {
    packages=("${@:3}")
    begin=$1
    dest=$2

    for package in "${packages[@]}"; do
        if ls repo/"${begin}"/x86_64/"${package}"* >/dev/null 2>&1; then
            cp repo/"${begin}"/x86_64/"${package}"* repo/"${dest}"/x86_64/
        fi
    done
}

finalize() {
    repo_type=$1
    pushd "${THIS_DIR}"/repo/"${repo_type}" || exit 1
    createrepo .
    popd || exit 1
}

# Check whether distro is "RHEL 8"
[ -f /etc/redhat-release ] || { echo "Invalid OS" && exit 1; }
[[ $(< /etc/redhat-release) == "Red Hat Enterprise Linux release 8.6 (Ootpa)" ]] || \
[[ $(< /etc/redhat-release) == "Red Hat Enterprise Linux release 8.7 (Ootpa)" ]] || \
    { echo "Invalid OS" && exit 1; }

# Check whether createrepo tool installed
if ! command -v "createrepo"
then
    echo "Did not find createrepo package, please install it by dnf install createrepo"
    exit 1
fi

[[ -d "$LOG_DIR" ]] || mkdir "$LOG_DIR"
[[ -d "$STATUS_DIR" ]] || mkdir "$STATUS_DIR"
if [[ "$1" == clean-build ]]; then
    rm -rf "${STATUS_DIR:?}"/*
fi

# Build host repo
build_repo "host" "${PACKAGES_HOST[@]}"

# Build guest repo
build_repo "guest" "${PACKAGES_GUEST[@]}"

# Move special packages
move_packages "host" "guest" "${PACKAGES_SPECIAL[@]}"

# Finalize
finalize "host"
finalize "guest"
