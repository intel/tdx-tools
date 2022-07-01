#!/bin/bash

set -ex

THIS_DIR=$(dirname "$(readlink -f "$0")")
GUEST_REPO="guest_repo"
HOST_REPO="host_repo"

pushd $THIS_DIR
mkdir -p $GUEST_REPO
mkdir -p $HOST_REPO

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
    cp linux-image-unsigned-5.15.0-*.deb linux-headers-5.15.0-* linux-modules-5.15.0-* linux-modules-extra-5.15.0-* ../$HOST_REPO/
    cd ..
}

build_qemu () {
    cd intel-mvp-spr-qemu
    ./build.sh
    cp qemu-system-x86_6.2*.deb qemu-system-common_6.2*.deb qemu-system-data_6.2*.deb ../$HOST_REPO/
    cd ..
}

build_tdvf () {
    cd intel-mvp-tdx-tdvf
    ./build.sh
    cp tdx-tdvf_*_all.deb ../$HOST_REPO/
    cd ..
}

build_libvirt () {
    cd intel-mvp-tdx-libvirt
    ./build.sh

    cp libvirt-clients_*.deb libvirt0_*.deb libvirt-daemon_*.deb libvirt-daemon-system_*.deb libvirt-daemon-system-systemd_*.deb \
	    libvirt-daemon-driver-qemu_*.deb libvirt-daemon-config-network_*.deb libvirt-daemon-config-nwfilter_*.deb \
	    libvirt-login-shell_*.deb libvirt-daemon-driver-lxc_*.deb ../$HOST_REPO/
    cd ..
}

build_shim
build_grub
build_kernel
build_qemu
build_tdvf
build_libvirt

popd
