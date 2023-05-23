
# Ubuntu 22.04 TDX Stack

## Build TDX packages

### Build requirements

```
apt install --no-install-recommends --yes build-essential fakeroot \
        devscripts wget git equivs liblz4-tool sudo python-is-python3 python3-dev pkg-config unzip
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

Please skip the warning message below, or eliminate it by installing local packages from /tmp/.

`Download is performed unsandboxed as root as file as file ... couldn't be accessed by user '_apt'. - pkgAcquire::Run (13: Permission denied)`

