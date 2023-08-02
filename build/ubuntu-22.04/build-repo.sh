#!/bin/bash

set -ex
set -o pipefail

THIS_DIR=$(dirname "$(readlink -f "$0")")
GUEST_REPO="guest_repo"
HOST_REPO="host_repo"
STATUS_DIR="${THIS_DIR}/build-status"
LOG_DIR="${THIS_DIR}/build-logs"
GUEST_ONLY=false

export DEBIAN_FRONTEND=noninteractive

build_check() {
    sudo apt update

    [[ -d "$LOG_DIR" ]] || mkdir "$LOG_DIR"
    [[ -d "$STATUS_DIR" ]] || mkdir "$STATUS_DIR"
    if [[ "$1" == clean-build ]]; then
        rm -rf "${STATUS_DIR:?}"/*
    fi
    if [[ "$1" == guest ]]; then
        GUEST_ONLY=true
    fi
}

build_kernel () {
    pushd intel-mvp-tdx-kernel
    [[ -f $STATUS_DIR/kernel.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/kernel.log
    touch "$STATUS_DIR"/kernel.done
    cp linux-image-unsigned-5.19.17-*.deb linux-headers-5.19.17-* linux-modules-5.19.17-* ../$GUEST_REPO/
    cp linux-image-unsigned-5.19.17-*.deb linux-headers-5.19.17-* linux-modules-5.19.17-* linux-modules-extra-5.19.17-* ../$HOST_REPO/
    popd
}

build_qemu () {
    pushd intel-mvp-tdx-qemu-kvm
    [[ -f $STATUS_DIR/qemu.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/qemu.log
    touch "$STATUS_DIR"/qemu.done
    cp qemu-system-x86_7.0*.deb qemu-system-common_7.0*.deb qemu-system-data_7.0*.deb ../$HOST_REPO/
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

build_amber-cli () {
    pushd intel-mvp-amber-cli
    [[ -f $STATUS_DIR/amber-cli.done ]] || ./build.sh
    touch $STATUS_DIR/amber-cli.done
    cp sgx_debian_local_repo/pool/main/libt/libtdx-attest/libtdx-attest-dev_*_amd64.deb \
            sgx_debian_local_repo/pool/main/libt/libtdx-attest/libtdx-attest_*_amd64.deb \
            amber-cli_*_amd64.deb ../$GUEST_REPO/
    popd
}

build_check "$1"

pushd "$THIS_DIR"
mkdir -p $GUEST_REPO
mkdir -p $HOST_REPO

build_kernel
$GUEST_ONLY || build_qemu
$GUEST_ONLY || build_tdvf
$GUEST_ONLY || build_libvirt
build_amber-cli

popd
