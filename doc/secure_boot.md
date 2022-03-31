## Secure Boot

### Overview

This section will introduce how to enable the secure boot function for the Linux TDX Software Stack
in the virtual machine environment (QEMU / Libvirt) and verify the secure boot function.

+ Generate secure boot related keys and digital certificates
+ Use Intel's Secure Boot Key Enrolling Tools to enroll the certificates and variables into TDVF
+ Use sbsigntools to sign Shim / Grub / Kernel in the QCOW2 image with private keys generated above
+ Configure QEMU / Libvirt to support secure boot in tdx virtual machine.
+ Verify the enabling of secure boot through the log

The details will be explained in the following document.

### Key Generation

In this step, we will generate the key and digital certificate needed in the secure boot process.
If you already have the key and digital certificate, you can skip this step.

To generate the key, first install `openssl`. We have many ways to install it, such as:

```sh
sudo dnf install openssl -y
```

Then we can use the following script to generate keys and digital certificates:

```sh
#!/bin/bash

NAME="Test"

openssl req -new -x509 -newkey rsa:2048 -subj "/CN=$NAME PK/" -keyout PK.key \
        -out PK.crt -days 3650 -nodes -sha256
openssl req -new -x509 -newkey rsa:2048 -subj "/CN=$NAME KEK/" -keyout KEK.key \
        -out KEK.crt -days 3650 -nodes -sha256
openssl req -new -x509 -newkey rsa:2048 -subj "/CN=$NAME DB/" -keyout DB.key \
        -out DB.crt -days 3650 -nodes -sha256
openssl x509 -in PK.crt -out PK.cer -outform DER
openssl x509 -in KEK.crt -out KEK.cer -outform DER
openssl x509 -in DB.crt -out DB.cer -outform DER

GUID=$(python3 -c 'import uuid; print(str(uuid.uuid1()))')
echo $GUID > myGUID.txt

chmod 0600 *.key
```

Regarding the use of various digital certificates, you can refer to the following materials

+ [Managing EFI Boot Loaders for Linux: Controlling Secure Boot](http://www.rodsbooks.com/efi-bootloaders/controlling-sb.html)
+ [UEFI Specification](https://uefi.org/sites/default/files/resources/UEFI%20Spec%202.8B%20May%202020.pdf)

### Enrolling Keys to TDVF

In this step, we need to enroll the generated key into TDVF using [tdvfkeyenroll](https://github.com/intel/tdx-tools/tree/main/utils/tdvfkeyenroll).

```sh
cd utils/tdvf-key-enroll
make
make install
```

Then execute the following command. Please replace `guid` with content of `myGUID.txt` generated above.

```
tdvf-key-enroll -fd <absolute-path-to-OVMF_VARS.fd> \
-pk <pk-key-guid> <absolute-path-to-PK.cer> \
-kek <kek-guid> <absolute-path-to-KEK.cer> \
-db <db-key-guid> <absolute-path-to-DB.cer>
```

When the following log is displayed, the key enrolling is successful:

```
[Success] Enroll All Variables to /path/to/OVMF_VARS.sb.fd
```

### Sign Shim / Grub / Kernel

In this step, we will digitally sign the shim, grub and guest kernel.

In the signing process, we need to use sbsigntools, we have many ways to install sbsigntools, such as:

+ Build from source: [sbsigntools source code](https://git.kernel.org/pub/scm/linux/kernel/git/jejb/sbsigntools.git)
+ Use rpm or deb packages built by others. For example,

```sh
wget https://download-ib01.fedoraproject.org/pub/fedora/linux/releases/33/Everything/x86_64/os/Packages/s/sbsigntools-0.9.4-2.fc33.x86_64.rpm
sudo rpm -ihvf sbsigntools-0.9.4-2.fc33.x86_64.rpm
```

Next, run the following script to sign shim and grub efi files and kernel vmlinuz file in a guest image.
Please assign the correct values at the beginning of the script if needed:

+ IMG: guest image that have shim, grub and kernel 5.1* installed
+ KEY_DIR: directory that contains DB.key and DB.crt generated above
+ DISTRO: redhat for rhel, centos for centos/centos stream 8

```sh
#!/bin/bash

IMG=/path/to/td-guest.qcow2
KEY_DIR=path/to/key-dir
DISTRO=redhat

sign_db() {
   sudo sbsign --key $KEY_DIR/DB.key --cert $KEY_DIR/DB.crt --output $1 $1
}

mkdir -p efi
mkdir -p rootfs
sudo modprobe nbd max_part=8
sudo qemu-nbd --connect=/dev/nbd0 $IMG
sudo mount /dev/nbd0p2 efi
sudo mount /dev/nbd0p3 rootfs

sign_db efi/EFI/$DISTRO/shimx64.efi
sign_db efi/EFI/$DISTRO/grubx64.efi
sign_db efi/EFI/$DISTRO/mmx64.efi
sign_db efi/EFI/BOOT/BOOTX64.efi
sign_db efi/EFI/BOOT/fbx64.efi
sign_db rootfs/boot/vmlinuz-5.1*
sudo cp efi/EFI/$DISTRO/mmx64.efi efi/EFI/BOOT/
cp rootfs/boot/vmlinuz-5.1* ./

sudo umount /dev/nbd0p2
sudo umount /dev/nbd0p3
sudo qemu-nbd --disconnect /dev/nbd0
```

Now we have successfully edited the QCOW2 image.

### Boot VM

In this step, we will use these files:

+ OVMF_VARS.sb.fd (key-enrolled)
+ td-guest.qcow2 (edited)

Next we can start the TD virtual machine. We have two ways: QEMU and Libvirt.

By QEMU, we can modify [start-qemu.sh](https://github.com/intel/tdx-tools/blob/main/start-qemu.sh):

+ confidential-guest-support=tdx ==> confidential-guest-support=lsec0
+ tdx-guest,id=tdx ==> tdx-guest,id=lsec0

After that, boot vm via

```sh
./start-qemu.sh -i /path/to/td-guest.qcow2 -b grub -a /path/to/OVMF_VARS.sb.fd
```

To boot via libvirt, please update the [xml template](https://github.com/intel/tdx-tools/blob/main/doc/tdx_libvirt_grub.xml.template)
as follows before running the usual virsh commands.

+ Add secure='yes': `<loader type='generic' secure='yes'>/usr/share/qemu/OVMF_CODE.fd</loader>`
+ Use OVMF_VARS.sb.fd: `<nvram>/path/to/OVMF_VARS.sb.fd</nvram>`
+ Use the signed image: `<source file='/path/to/QCOW2-image'/>`

### Verification

After the virtual machine is booted, we can use this command to verify secure boot:

```
dmesg | grep -i secure
```

If we see `Secure Boot Enabled`, it means that we have successfully enabled secure boot.
