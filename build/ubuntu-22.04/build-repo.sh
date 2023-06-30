#!/bin/bash

THIS_DIR=$(dirname "$(readlink -f "$0")")
GUEST_REPO="guest_repo"
HOST_REPO="host_repo"
STATUS_DIR="${THIS_DIR}/build-status"
LOG_DIR="${THIS_DIR}/build-logs"

export DEBIAN_FRONTEND=noninteractive

build_check() {
    sudo apt update

    [[ -d "$LOG_DIR" ]] || mkdir "$LOG_DIR"
    [[ -d "$STATUS_DIR" ]] || mkdir "$STATUS_DIR"
    if [[ "$1" == clean-build ]]; then
        rm -rf "${STATUS_DIR:?}"/*
    fi
}

build_shim () {
    pushd intel-mvp-tdx-guest-shim
    [[ -f $STATUS_DIR/shim.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/shim.log
    touch "$STATUS_DIR"/shim.done
    cp shim_*_amd64.deb ../$GUEST_REPO/
    popd
}

build_grub () {
    pushd intel-mvp-tdx-guest-grub2
    sudo apt remove libzfslinux-dev -y || true
    [[ -f $STATUS_DIR/grub.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/grub2.log
    touch "$STATUS_DIR"/grub.done
    cp grub-efi-amd64_*_amd64.deb grub-efi-amd64-bin_*_amd64.deb ../$GUEST_REPO/
    popd

    # Uninstall to avoid confilcts with libnvpair-dev
    sudo apt remove grub2-build-deps-depends grub2-unsigned-build-deps-depends -y || true
}

build_kernel () {
    pushd intel-mvp-tdx-kernel
    [[ -f $STATUS_DIR/kernel.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/kernel.log
    touch "$STATUS_DIR"/kernel.done
    cp linux-image-unsigned-6.2.0-*.deb linux-headers-6.2.0-* linux-modules-6.2.0-* ../$GUEST_REPO/
    cp linux-image-unsigned-6.2.0-*.deb linux-headers-6.2.0-* linux-modules-6.2.0-* linux-modules-extra-6.2.0-* ../$HOST_REPO/
    popd
}

build_qemu () {
    pushd intel-mvp-tdx-qemu-kvm
    [[ -f $STATUS_DIR/qemu.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/qemu.log
    touch "$STATUS_DIR"/qemu.done
    cp qemu-system-x86_7.2*.deb qemu-system-common_7.2*.deb qemu-system-data_7.2*.deb ../$HOST_REPO/
    popd
}

build_tdvf () {
    pushd intel-mvp-ovmf
    [[ -f $STATUS_DIR/ovmf.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/ovmf.log
    touch "$STATUS_DIR"/ovmf.done
    cp ovmf_*_all.deb ../$HOST_REPO/
    popd
}

build_libvirt () {
    pushd intel-mvp-tdx-libvirt
    [[ -f $STATUS_DIR/libvirt.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/libvirt.log
    touch "$STATUS_DIR"/libvirt.done
    cp libvirt-clients_*.deb libvirt0_*.deb libvirt-daemon_*.deb libvirt-daemon-system_*.deb libvirt-daemon-system-systemd_*.deb \
            libvirt-daemon-driver-qemu_*.deb libvirt-daemon-config-network_*.deb libvirt-daemon-config-nwfilter_*.deb \
            libvirt-login-shell_*.deb libvirt-daemon-driver-lxc_*.deb ../$HOST_REPO/
    popd
}

build_migtd () {
    cd intel-mvp-tdx-migration
    ./build.sh
    cp td-migration_*_amd64.deb ../$HOST_REPO/
    cd ..
}

build_check "$1"

pushd "$THIS_DIR"
mkdir -p $GUEST_REPO
mkdir -p $HOST_REPO

set -ex

build_shim
build_grub
build_kernel
build_qemu
build_tdvf
build_libvirt
build_migtd

# All build pass, remove build status directory
rm -rf "${STATUS_DIR:?}"/
popd
