
# Build TDX Stack on Ubuntu 22.04

For Ubuntu it also supports building in Docker container to isolate the build environment from the linux host.
`./pkg-builder -c <build-script>` will create a Docker image named `pkg-builder-ubuntu-22.04` and start a container to run the build script.

## Build requirements

Follow https://docs.docker.com/engine/install/ to setup Docker.

If you'd like to build on bare metal Ubuntu 22.04, install the build dependencies below.

```
apt install --no-install-recommends --yes build-essential fakeroot \
        devscripts wget git equivs liblz4-tool sudo python-is-python3 python3-dev pkg-config unzip
```
The local libraries `/usr/local/lib/x86_64-linux-gnu/` may cause kernel build failure.
Consider removing it to resolve `no dependency information found for /usr/local/lib/x86_64-linux-gnu/*`. Ubuntu distro path `/usr/lib/x86_64-linux-gnu/` will be used instead.

## Build all

build-repo.sh will build host packages into host_repo/ and guest packages into guest_repo/ .
Run it in docker container using `pkg-builder`.

```
cd tdx-tools/build/ubuntu-22.04
./pkg-builder -c "./build-repo.sh"
```

If you need to build some packages separately, run `build.sh` in each subdirectory.

```
./pkg-builder -c "./intel-mvp-ovmf/build.sh"
```

## Install TDX host packages

```
cd host_repo
sudo apt -y --allow-downgrades install ./jammy/amd64/*.deb
sudo apt -y --allow-downgrades install ./jammy/all/*.deb
```

Please skip the warning message below, or eliminate it by installing local packages from `/tmp/` .

`Download is performed unsandboxed as root as file as file ... couldn't be accessed by user '_apt'. - pkgAcquire::Run (13: Permission denied)`

