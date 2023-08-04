
# Build TDX Stack on Ubuntu 22.04

Please run build script in Docker container via `./pkg-builder` to isolate the
build environment from the linux host. So you can build the TDX ubuntu packages
on any Linux OS. `./pkg-builder -r <build-script>` will automatically create a
Docker image named `pkg-builder-ubuntu-22.04` and start a container to run `<build-script>`

## Setup Docker

1. Follow https://docs.docker.com/engine/install/ to setup Docker.
2. Please add current user into docker group via `sudo usermod -G docker -a $USER`,
then restart docker service, or logout and login current user to take effect.

## Usages

1. Build all packages including host and guest

```
cd tdx-tools/build/ubuntu-22.04

./pkg-builder -r build-repo.sh
```

`build-repo.sh` will build host packages into host_repo/ and guest packages into guest_repo/ .

If the builder container image "pkg-builder-ubuntu-22.04" has been created after first running, using option `-e` to skip the container image building step.
```
./pkg-builder -r build-repo.sh -e
```

2. Build individual package


```
./pkg-builder -s intel-mvp-ovmf/build.sh
```

## Install packages

You can install packages for TDX host by manual via the following steps:

```
cd host_repo
sudo apt -y --allow-downgrades install ./jammy/all/*.deb
sudo apt -y --allow-downgrades install ./jammy/amd64/*.deb
```

_NOTE: Please skip the warning message below, or eliminate it by installing local packages from `/tmp/`._

```
Download is performed unsandboxed as root as file as file ... couldn't be accessed by user '_apt'. - pkgAcquire::Run (13: Permission denied)
```

You can also install packages for TDX guest using similar steps after copying the
whole guest packages into TDX guest VM.

Another way, which supports configuring a local apt repository. Take `host_repo` as an example:

```
cp host_repo /tmp/ -fr
cat > /etc/apt/sources.list.d/tdx-local.list << EOL
deb [trusted=yes] file:///tmp/host_repo / jammy/all/
deb [trusted=yes] file:///tmp/host_repo / jammy/amd64/
EOL
```
