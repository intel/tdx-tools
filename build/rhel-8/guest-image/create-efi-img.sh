#!/usr/bin/bash

ISO="RHEL-8.6.0-20220420.3-x86_64-dvd1.iso"

# Kickstart scripts
KS_DIR="kickstart"
KS_EFI="base.ks"
KS_OS="rhel-8.ks"

# Guest image size(unit: GB)
IMAGE_SIZE=8
IMAGE_NAME="td-guest-rhel-8.6.qcow2"
VIRT_NAME="setup-guest-rhel-8.6"

CURR_DIR=$(readlink -f "$(dirname "$0")")
pushd "${CURR_DIR}" || exit 1

if ! command -v "virt-install" ; then
    echo "virt-install not found, please install package virt-install"
    exit 1
fi

eval virt-install \
    --name ${VIRT_NAME} \
    --cpu host \
    --virt-type=kvm \
    --ram 16384 \
    --vcpus 8 \
    --os-type linux \
    --os-variant rhel8-unknown \
    --network bridge=virbr0 \
    --nographics \
    --disk=${IMAGE_NAME},bus=virtio,format=qcow2,size=${IMAGE_SIZE} \
    --location="${ISO}" \
    --initrd-inject ${KS_DIR}/${KS_EFI} \
    --initrd-inject ${KS_DIR}/${KS_OS} \
    --extra-args="\"inst.ks=file:/${KS_EFI} console=ttyS0,115200\"" \
    --destroy-on-exit \
    --transient

if [[ -f ${IMAGE_NAME} ]] ; then
    echo "[  OK  ] EFI image created: ${IMAGE_NAME}"
else
    echo "[FAILED] EFI image failed: ${IMAGE_NAME}"
fi

popd || exit 1
