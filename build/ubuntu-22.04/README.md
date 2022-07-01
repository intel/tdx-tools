
# Ubuntu 22.04 TDX MVP Stack

## Build TDX packages

### Build requirements

```
apt install --no-install-recommends --yes build-essential \
        fakeroot devscripts wget git equivs liblz4-tool sudo python-is-python3 pkg-config unzip
```

### Build all

build-repo.sh builds host packages into host_repo/ and guest packages into guest_repo/.

```
cd tdx-tools/build/ubuntu-22.04
./build-repo.sh
```

## Install TDX host packages

```
cd host_repo
sudo apt -y --allow-downgrades install ./*.deb
```

Please skip the warning message below. It is just a notice that the system could not verify the package it was installing.

`Download is performed unsandboxed as root as file as file ... couldn't be accessed by user '_apt'. - pkgAcquire::Run (13: Permission denied)`

## Setup TDVM

### Generate TD Guest image

This step will generate TD guest image td-guest-ubuntu-22.04.qcow2. It depends on guest_repo/ generated above. 

```
cd guest-image
./tdx-guest-stack.sh
```

### Test Guest image

Use [start-qemu.sh](https://github.com/intel/tdx-tools/blob/main/start-qemu.sh) script to start a TDVM via QEMU.

```
./start-qemu.sh -i td-guest-ubuntu-22.04.qcow2 -b grub
```

### (Optional) Install grub and shim for measured boot in TD guest

```
apt remove --allow-remove-essential shim-signed -y
apt remove grub-pc -y
cd /srv/guest-repo/
dpkg -i shim_*_amd64.deb
dpkg -i grub-efi-amd64_*_amd64.deb grub-efi-amd64-bin_*_amd64.deb
update-grub
reboot
```
