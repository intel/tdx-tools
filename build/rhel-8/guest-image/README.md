# RHEL 8.7 TDX Guest Image

Create a TDX guest image in EFI schema with customized bootloader (grub/shim) and guest kernel.

## Prerequisites

- RHEL 8.7 base ISO image. You can download it from https://access.redhat.com/downloads .

- virt-manager and libvirt. Please install them via `sudo dnf install -y virt-manager libguestfs-tools-c` .

## Steps

- Before running, modify the ISO path in create-efi-img.sh, for example `ISO="RHEL-8.7.0-20221013.1-x86_64-dvd1.iso"` .

`./create-efi-img.sh`

- Install tdx-guest-kernel, tdx-guest-grub2 and tdx-guest-shim. The local guest repository `../repo/guest` is required.

`./tdx-guest-stack.sh`
