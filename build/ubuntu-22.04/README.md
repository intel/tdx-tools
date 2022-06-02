
# TDX Guest build for Ubuntu 22.04

- Build guest debian packages for TDX

```
cd tdx-tools/build/ubuntu-22.04
./build-repo.sh
```

- Generate TDX Guest image

```
cd guest-image
./tdx-guest-stack.sh
```

- Test Guest image

```
./start-qemu.sh -i td-guest-ubuntu-22.04.qcow2 -b grub
```

- (Optional) Install grub and shim for measured boot in TDX guest

```
apt remove --allow-remove-essential shim-signed -y
apt remove grub-pc -y
cd /srv/tdx-guest-debs/
dpkg -i shim_*_amd64.deb
dpkg -i grub-efi-amd64_*_amd64.deb grub-efi-amd64-bin_*_amd64.deb
update-grub
reboot
```
