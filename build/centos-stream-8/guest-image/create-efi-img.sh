#!/usr/bin/bash

ISO="CentOS-Stream-8-x86_64-latest-dvd1.iso"
MIRROR="http://isoredirect.centos.org/centos/8-stream/isos/x86_64/"

# Kickstart scripts
KS_DIR="kickstart"
KS_EFI="base.ks"
KS_OS="centos-stream.ks"

# Guest image size(unit: GB)
IMAGE_SIZE=8
IMAGE_NAME="td-guest-c8s.qcow2"
VIRT_NAME="setup-guest-c8s"

CURR_DIR=$(readlink -f "$(dirname "$0")")
pushd "${CURR_DIR}" || exit 1

if [[ ! -f ${ISO} ]] ; then
    wget ${MIRROR}/${ISO}
fi


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
    --os-variant centos8 \
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

