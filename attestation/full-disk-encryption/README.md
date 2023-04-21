# Intel&reg; TDX Full Disk Encryption

Full disk encryption (FDE) is a security method for protecting sensitive
data by encrypting all data on a disk partition. FDE shall encrypt data
automatically to prevent unauthorized access.
This project is a FDE solution based on [Intel&reg; Trust Domain 
Extensions(Intel TDX)](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-trust-domain-extensions.html).

## Architecture

![](./docs/fde-arch.png)

### The workflow of fde-agent

In the early-boot stage, the `fde-agent` which resides in the `initramfs`, is invoked by `init` to mount an encrypted rootfs. The workflow of `fde-agent` is composed of four steps:

1. Retrieve variables from OVMF via `efivarfs`.
    - Variables are enrolled in the OVMF before tdvm being launched.
    - The variables can be customized. For example, there are three variables: `url`, user token and certification, which will be used to retrieve the key from remote KBS (Key Broker Service).
    - The user token contains a `keyid`.
    - The `src/ovmf_var.rs` shows how to read variables from the OVMF.

2. Retrieve the `quote`.
    - The quote is the evidence that proves the TEE is secured from the TDX.
    - The `src/td_report.rs` and `src/quote.rs` show how to get the quote.

3. Retrieve the `key` that encrypts the rootfs from the KBS.
    - The demo follows the [Remote Attestation Procedures Architecture](https://www.ietf.org/archive/id/draft-ietf-rats-architecture-22.html). The fde-agent sends the `${quote}` and `{keyid}` to the KBS to prove that it is in a TEE, then receives the `key`. The query uri is dependent on the KBS provider, it may look like: `https://${url}/key/${keyid}`.
    - The `${url}` and `${keyid}` are retrieved in the step 1.
    - The `src/key_broker.rs` show an example to connect to the KBS.

4. Decrypt the encrypted rootfs by `${key}` and mount it.
    - the `${key}` is retrieve in the step 3.
    - The `src/disk.rs` shows the detail.

## Fde-agent Build

**Warning: The default fde-agent implementation will panic because it connects to a dummy KBS. Consult your KBS provider to create a concrete fde-agent.**

The fde-agent depends on dynamic libraries `libtdx-attest` and `libtdx-attest-dev` in `DCAP 1.16`. The `DCAP 1.16` can be downloaded from [official website](https://download.01.org/intel-sgx/sgx-dcap/1.16/) or built from the source [SGXDataCenterAttestationPrimitives](https://github.com/intel/SGXDataCenterAttestationPrimitives.git) with tag `DCAP_1.16`. 
Install [Rust-lang](https://www.rust-lang.org/), then build the fde-agent:

```
cd attestation/full-disk-encryption
cargo build --release
```

Optionally, strip for small-size application

```
strip --strip-all target/release/fde-agent
```

## Image Build

### 1. Create an empty image file.

```
truncate --size ${IMAGE_SIZE}M ${OUTPUT_IMAGE}
```

The empty image file `OUTPUT_IMAGE` whose size is `IMAGE_SIZE` M contains
- root filesystem partition, whose size is `ROOTFS_SIZE` M,
- boot components, whose size is `BOOT_SIZE` M,
- reserved partition for EFI and BIOS boot, whose size can be `101` M.

### 2. Partition the image file

The partition 1 is used to save root filesystem, the partition 16 is used to save boot components and partition 15 is used to save EFI components.

```
sgdisk --clear \
    --new 14::+1M --typecode=14:ef02 --change-name=14:'bios' \
    --new 15::+100M --typecode=15:ef00 --change-name=15:'uefi' \
    --new 16::+$BOOT_SIZE --typecode=16:8300 --change-name=16:'boot' \
    --new 1::-0 --typecode=1:8300 --change-name=1:'rootfs' \
    $OUTPUT_IMAGE
```

Associate a loop device with the image file and expose partitions for rootfs, boot and efi.

```
LOOPDEV=$(losetup --find --show $OUTPUT_IMAGE)
partprobe ${LOOPDEV}
ROOT=${LOOPDEV}p1
EFI=${LOOPDEV}p15
BOOT=${LOOPDEV}p16
```

### 3. Encrypt the rootfs partition

We use cryptsetup to encrypt a LUKS encrypted volume and label it as `rootfs-enc`. The `KEY=key` is retrieved in step 1.

```
echo ${KEY} | cryptsetup -v -q luksFormat --encrypt --type luks2 \
    --cipher aes-gcm-random --integrity aead --key-size 256 ${ROOT}

cryptsetup -v config --label rootfs-enc ${ROOT}
```
 
For convenience, open the encrypted volume by cryptsetup, which maps the `ROOT` to device `/dev/mapper/rootfs-enc-dev`

```
echo $KEY | cryptsetup open --key-size 256 $ROOT rootfs-enc-dev
ROOT_ENC=/dev/mapper/rootfs-enc-dev
```

### 4. Format partitions

```
mkfs.fat -F32 $EFI
mkfs.ext4 -F -L "boot" $BOOT
mkfs.ext4 -F $ROOT_ENC
```

### 5. Install rootfs

Mount partitions to some places as you like.

```
mkdir -p /tmp/mnt/root
mount $ROOT_ENC /tmp/mnt/root
mkdir -p /tmp/mnt/root/boot
mount $BOOT /tmp/mnt/root/boot/
mkdir -p /tmp/mnt/root/boot/efi
mount $EFI /tmp/mnt/root/boot/efi
```

We need download a tarball of a valid rootf and extract it to the rootfs partition.

```
wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64-root.tar.xz

ROOTFS_TAR=jammy-server-cloudimg-amd64-root.tar.xz

tar -xf $ROOTFS_TAR -C /tmp/mnt/root/
```

Install package repositories to rootfs. The guest `TDX_REPO` is built by tools from `build`, usually named by `guest_repo`. And DCAP repo is downloaded from `DCAP_URL`.

```
mkdir -p /tmp/mnt/root/opt/intel

cp -r ${TDX_REPO} /tmp/mnt/root/opt/intel/

# customize it if your repo has different file hierarchy
echo "deb [trusted=yes arch=amd64] file:/opt/intel/guest_repo jammy main" |\
    tee /tmp/mnt/root/etc/apt/sources.list.d/intel-tdx.list

DCAP_URL=https://download.01.org/intel-sgx/sgx-dcap/1.16/linux/distro/ubuntu22.04-server/sgx_debian_local_repo.tgz

wget $DCAP_URL

tar zxf sgx_debian_local_repo.tgz -C /tmp/mnt/root/opt/intel/ 

echo "deb [trusted=yes arch=amd64] file:/opt/intel/sgx_debian_local_repo jammy main" |\
    tee /tmp/mnt/root/etc/apt/sources.list.d/sgx_debian_local_repo.list

```

Copy the fde-agent and related config to the rootfs

```
cp ${FDE_DIR}/target/release/fde-agent /tmp/mnt/root/sbin/

cp ${FDE_DIR}/tools/initramfs/scripts/init-premount/fde-agent /tmp/mnt/root/usr/share/initramfs-tools/scripts/init-premount/

cp ${FDE_DIR}/tools/initramfs/modules /tmp/mnt/root/etc/initramfs-tools/

cp -r ${FDE_DIR}/tools/initramfs/hooks/* /tmp/mnt/root/usr/share/initramfs-tools/hooks/

cp -r ${FDE_DIR}/tools/image/netplan.yaml /tmp/mnt/root/etc/netplan
```

Currently, we need update rootfs with special root directory by using command `chroot`. Firstly, mount other necessary filesystems.

```
mount -t proc none /tmp/mnt/root/proc
mount -t sysfs none /tmp/mnt/root/sys
mount -t tmpfs none /tmp/mnt/root/tmp
mount --bind /run /tmp/mnt/root/run
mount --bind /dev /tmp/mnt/root/dev
mount --bind /dev/pts /tmp/mnt/root/dev/pts
```

Copy the script `install` and execute it.

```
cp ${FDE_DIR}/tools/image/install /tmp/mnt/root/tmp/
chroot /tmp/mnt/root/ /bin/bash tmp/install $ROOT $ROOT_PASS
rm /tmp/mnt/root/tmp/install
```

The script `install` is placed in `${FDE_DIR}/tools/image/install`. It is responsible for installing software dependencies and updating config in runtime.

Unmount filesystems.

```
umount /tmp/mnt/root/dev/pts
umount /tmp/mnt/root/dev
umount /tmp/mnt/root/run
umount /tmp/mnt/root/tmp
umount /tmp/mnt/root/sys
umount /tmp/mnt/root/proc
umount /tmp/mnt/root/boot/efi
umount /tmp/mnt/root/boot
umount /tmp/mnt/root/
```

### 6. Close devices

Last but not least, we need to close all devices.

```
cryptsetup close rootfs-enc
losetup -d $LOOPDEV
```

