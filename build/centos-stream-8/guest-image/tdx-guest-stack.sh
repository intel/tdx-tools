#!/usr/bin/bash

CURR_DIR=$(readlink -f "$(dirname "$0")")
REPO_DIR="../repo/guest/"
IMAGE="td-guest-c8s.qcow2"

pushd "${CURR_DIR}" || exit 1

if ! readlink -f ${REPO_DIR} ; then
    echo "${REPO_DIR} does not exist"
    exit 1
fi

if ! command -v "virt-customize" ; then
    echo "virt-customize not found, please install libguestfs-tools-c"
    exit 1
fi

# virt-customize parameters
ARGS=" -a ${IMAGE} -x"

# Setup guest environments
ARGS+=" --copy-in /etc/environment:/etc"
ARGS+=" --copy-in /etc/resolv.conf:/etc"
ARGS+=" --copy-in /etc/chrony.conf:/etc"

# Setup TDX guest repo
ARGS+=" --copy-in ${REPO_DIR}:/srv/"
ARGS+=" --copy-in config/srv_guest.repo:/etc/yum.repos.d/"

# Install TDX guest packages
ARGS+=" --install intel-mvp-tdx-guest-grub2-efi-x64,intel-mvp-tdx-guest-grub2-pc,intel-mvp-tdx-guest-shim,intel-mvp-tdx-guest-kernel"

# Setup grub
ARGS+=" --copy-in config/grub:/etc/default/"
ARGS+=' --run-command "grub2-editenv /boot/efi/EFI/centos/grubenv create"'
ARGS+=' --run-command "grub2-mkconfig -o /boot/efi/EFI/centos/grub.cfg"'

echo "${ARGS}"
eval virt-customize "${ARGS}"

popd || exit 1

