#!/usr/bin/bash

export LIBGUESTFS_BACKEND=direct

IMG_URL=https://cloud-images.ubuntu.com/jammy/current
CLOUD_IMG=jammy-server-cloudimg-amd64.img
TD_IMG=td-guest-ubuntu-22.04.qcow2
REPO_DIR="../tdx-guest-debs"

if ! readlink -f ${REPO_DIR} ; then
    echo "${REPO_DIR} does not exist, please build it via build-repo.sh"
    exit 1
fi

if ! command -v "virt-customize" ; then
    echo "virt-customize not found, please install libguestfs-tools-c"
    exit 1
fi

if [[ ! -f ${CLOUD_IMG} ]] ; then
    wget ${IMG_URL}/${CLOUD_IMG}
fi

# The original image is in qcow2 format already. 
cp $CLOUD_IMG $TD_IMG

virt-customize -a ${TD_IMG} --root-password password:123456
qemu-img resize ${TD_IMG} +5G

ARGS=" -a ${TD_IMG} -v -x"

# Setup guest environments
ARGS+=" --copy-in /etc/environment:/etc"
ARGS+=" --copy-in netplan.yaml:/etc/netplan/"
ARGS+=" --copy-in ${REPO_DIR}:/srv/"
ARGS+=" --edit '/etc/ssh/sshd_config:s/#PermitRootLogin prohibit-password/PermitRootLogin yes/'"
ARGS+=" --edit '/etc/ssh/sshd_config:s/PasswordAuthentication no/PasswordAuthentication yes/'"
ARGS+=" --run-command 'growpart /dev/sda 1'"
ARGS+=" --run-command 'resize2fs /dev/sda1'"
ARGS+=" --run-command 'ssh-keygen -A'"
ARGS+=" --run-command 'dpkg -i /srv/tdx-guest-debs/linux-*.deb'"

echo "${ARGS}"
eval virt-customize "${ARGS}"

