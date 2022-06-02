#!/bin/bash

set -ex

THIS_DIR=$(dirname "$(readlink -f "$0")")
GUEST_REPO="tdx-guest-debs"

pushd $THIS_DIR
mkdir -p $GUEST_REPO

build_shim () {
    cd intel-mvp-tdx-guest-shim
    ./build.sh
    cp shim_*_amd64.deb ../$GUEST_REPO/
    cd ..
}

build_grub () {
    cd intel-mvp-tdx-guest-grub2
    ./build.sh
    cp grub-efi-amd64_*_amd64.deb grub-efi-amd64-bin_*_amd64.deb ../$GUEST_REPO/
    cd ..
}

build_kernel () {
    cd intel-mvp-spr-kernel
    ./build.sh
    cp linux-image-unsigned-5.15.0-*.deb linux-headers-5.15.0-* linux-modules-5.15.0-* ../$GUEST_REPO/
    cd ..
}

build_shim
build_grub
build_kernel

popd
