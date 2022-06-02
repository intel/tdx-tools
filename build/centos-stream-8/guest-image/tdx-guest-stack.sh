#!/usr/bin/bash

export LIBGUESTFS_BACKEND=direct

CURR_DIR=$(readlink -f "$(dirname "$0")")
REPO_DIR="../repo/guest/"
IMAGE="td-guest-c8s.qcow2"

pushd "${CURR_DIR}" || exit 1

if ! readlink -f ${REPO_DIR} ; then
    echo "${REPO_DIR} does not exist, please build it via build-repo.sh"
    exit 1
fi

if ! command -v "virt-customize" ; then
    echo "virt-customize not found, please install libguestfs-tools-c"
    exit 1
fi

# virt-customize initial parameters
ARGS=" -a ${IMAGE} -x"

# Setup guest environments
ARGS+=" --copy-in /etc/environment:/etc"
ARGS+=" --copy-in /etc/chrony.conf:/etc"

# Setup TDX guest repo
ARGS+=" --copy-in ${REPO_DIR}:/srv/"
ARGS+=" --copy-in config/srv_guest.repo:/etc/yum.repos.d/"

# Install TDX guest packages
GRUB="intel-mvp-tdx-guest-grub2-efi-x64 intel-mvp-tdx-guest-grub2-pc"
SHIM="intel-mvp-tdx-guest-shim"
KERNEL="intel-mvp-spr-kernel-guest"
REPO="srv_guest"
ARGS+=" --run-command 'dnf install ${GRUB} ${SHIM} ${KERNEL} -y --repo ${REPO}'"

# Setup grub
ARGS+=" --copy-in config/grub:/etc/default/"
ARGS+=" --run-command 'grub2-editenv /boot/efi/EFI/centos/grubenv create'"
ARGS+=" --run-command 'grub2-mkconfig -o /boot/efi/EFI/centos/grub.cfg'"

echo "${ARGS}"
eval virt-customize "${ARGS}"

popd || exit 1

