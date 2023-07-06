#!/bin/bash

set -ex
set -o pipefail

THIS_DIR=$(dirname "$(readlink -f "$0")")
GUEST_REPO="guest_repo"
HOST_REPO="host_repo"
STATUS_DIR="${THIS_DIR}/build-status"
LOG_DIR="${THIS_DIR}/build-logs"

export DEBIAN_FRONTEND=noninteractive

GUEST_DEFAULT_PKG=" \
shim_*_amd64.deb \
grub-efi-amd64_*_amd64.deb grub-efi-amd64-bin_*_amd64.deb \
linux-image-unsigned-6.2.16-*.deb linux-headers-6.2.16-* linux-modules-6.2.16-* \
"

HOST_DEFAULT_PKG=" \
linux-image-unsigned-6.2.16-*.deb linux-headers-6.2.16-* linux-modules-6.2.16-* linux-modules-extra-6.2.16-* \
qemu-system-x86_7.2*.deb qemu-system-common_7.2*.deb qemu-system-data_7.2*.deb \
ovmf_*_all.deb \
libvirt-clients_*.deb libvirt0_*.deb libvirt-daemon_*.deb libvirt-daemon-system_*.deb libvirt-daemon-system-systemd_*.deb\
 libvirt-daemon-driver-qemu_*.deb libvirt-daemon-config-network_*.deb libvirt-daemon-config-nwfilter_*.deb\
 libvirt-login-shell_*.deb libvirt-daemon-driver-lxc_*.deb libvirt-dev_*.deb \
td-migration_*_amd64.deb \
vtpm-td_*_amd64.deb \
"

build_check() {
    sudo apt update

    if ! command -v "dpkg-scanpackages"
    then
        sudo apt install dpkg-dev -y
    fi

    [[ -d "$LOG_DIR" ]] || mkdir "$LOG_DIR"
    [[ -d "$STATUS_DIR" ]] || mkdir "$STATUS_DIR"
    if [[ "$1" == clean-build ]]; then
        rm -rf "${STATUS_DIR:?}"/*
    fi

    if [[ ! -z ${rust_mirror} ]]; then
        mkdir -p ~/.cargo
        cat > ~/.cargo/config << EOL
[source.crates-io]
replace-with = 'mirror'

[source.mirror]
registry = "${rust_mirror}"

[registries.mirror]
index = "${rust_mirror}"
EOL
    fi

    if [[ ! -z ${rustup_dist_server} ]]; then
        export RUSTUP_DIST_SERVER="${rustup_dist_server}"
    fi
    if [[ ! -z ${rustup_update_server} ]]; then
        export RUSTUP_UPDATE_SERVER="${rustup_update_server}"
    fi
}

build_shim () {
    pushd intel-mvp-tdx-guest-shim
    [[ -f $STATUS_DIR/shim.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/shim.log
    touch "$STATUS_DIR"/shim.done
    cp shim_*_amd64.deb ../$GUEST_REPO/more/
    popd
}

build_grub () {
    pushd intel-mvp-tdx-guest-grub2
    sudo apt remove libzfslinux-dev -y || true
    [[ -f $STATUS_DIR/grub.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/grub2.log
    touch "$STATUS_DIR"/grub.done
    cp grub-efi-*_amd64.deb  ../$GUEST_REPO/more/
    popd

    # Uninstall to avoid confilcts with libnvpair-dev
    sudo apt remove grub2-build-deps-depends grub2-unsigned-build-deps-depends -y || true
}

build_kernel () {
    pushd intel-mvp-tdx-kernel
    [[ -f $STATUS_DIR/kernel.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/kernel.log
    touch "$STATUS_DIR"/kernel.done
    cp linux-*6.2.16*.deb ../$GUEST_REPO/more/
    cp linux-*6.2.16*.deb ../$HOST_REPO/more/
    popd
}

build_qemu () {
    pushd intel-mvp-tdx-qemu-kvm
    [[ -f $STATUS_DIR/qemu.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/qemu.log
    touch "$STATUS_DIR"/qemu.done
    cp qemu*7.2.0*.deb *.ddeb ../$HOST_REPO/more/
    popd
}

build_tdvf () {
    pushd intel-mvp-ovmf
    [[ -f $STATUS_DIR/ovmf.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/ovmf.log
    touch "$STATUS_DIR"/ovmf.done
    cp ovmf_*_all.deb ../$HOST_REPO/more/
    popd
}

build_libvirt () {
    pushd intel-mvp-tdx-libvirt
    [[ -f $STATUS_DIR/libvirt.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/libvirt.log
    touch "$STATUS_DIR"/libvirt.done
    cp libvirt*8.6.0*.deb libnss*_amd64.deb *.ddeb ../$HOST_REPO/more/
    popd
}

build_migtd () {
    pushd intel-mvp-tdx-migration
    [[ -f $STATUS_DIR/migtd.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/migtd.log
    touch "$STATUS_DIR"/migtd.done
    cp td-migration_*_amd64.deb ../$HOST_REPO/more/
    popd
}

build_vtpm-td () {
    pushd intel-mvp-vtpm-td
    [[ -f $STATUS_DIR/vtpm-td.done ]] || ./build.sh 2>&1 | tee "$LOG_DIR"/vtpm-td.log
    touch "$STATUS_DIR"/vtpm-td.done
    cp vtpm-td_*_amd64.deb ../$HOST_REPO/more/
    popd
}

build_repo () {
    # move necessary packages to repo root directory.
    # so the local file installation keeps same as before.
    pushd $GUEST_REPO/more
    mv $GUEST_DEFAULT_PKG ../
    popd

    pushd $HOST_REPO/more
    mv $HOST_DEFAULT_PKG ../
    popd

    pushd $HOST_REPO && dpkg-scanpackages . > Packages && popd
    pushd $GUEST_REPO && dpkg-scanpackages . > Packages && popd
}

build_check "$1"

pushd "$THIS_DIR"
mkdir -p $GUEST_REPO/more
mkdir -p $HOST_REPO/more

build_shim
build_grub
build_kernel
build_qemu
build_tdvf
build_libvirt
build_migtd
build_vtpm-td
build_repo

popd
