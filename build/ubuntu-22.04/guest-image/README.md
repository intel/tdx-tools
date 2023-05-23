# Ubuntu 22.04 TDX Guest Image

Customize Ubuntu 22.04 cloud image and install TDX guest kernel.

## Prerequisites

- Install qemu-img and virt-customize via `sudo apt install -y qemu-utils libguestfs-tools` .

## Steps

- Run the script to generate `td-guest-ubuntu-22.04.qcow2`. The local guest repository `../guest_repo` is required.

`./tdx-guest-stack.sh`

### (Optional) Install grub and shim for boot measurement in TD guest

```
apt remove --allow-remove-essential shim-signed -y
apt remove grub-pc -y
dpkg -r --force-all grub-efi-amd64-signed
cd /srv/guest-repo/
dpkg -i shim_*_amd64.deb
dpkg -i grub-efi-amd64_*_amd64.deb grub-efi-amd64-bin_*_amd64.deb
grub-install --target=x86_64-efi --modules "tpm"
reboot
```
