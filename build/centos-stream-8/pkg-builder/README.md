# Package builder

This utility help to build the package in distro format like RPM or DEBIAN. The
build process is running within docker container in any Linux distro or github
action environment.

## Build package by manual

1. Prerequisties

- A latest Linux distro like Ubuntu 20.04, CentOS Stream 8, etc
- Install docker container tool
- If environment is behind of firewall, please configure the `http_proxy`,
`https_proxy`, `no_proxy` for:
  - docker service at /etc/systemd/docker.service.d/proxy.conf
  - docker environment at ~/.docker/config.json
- Make sure current user in docker group like: `sudo usermod -aG docker <current>`,
otherwise you need sudo to run docker every time.

2. Build pkg-builder container

```
cd build\centos-stream-8\pkg-builder\
docker build -t pkg-builder-centos-stream-8 .
```

**_NOTE_:** By default, it use Aliyun mirror to accelerate, please change to any
other mirror for your favorite.

3. Build package

```
cd build\centos-stream-8\<any package for build>
docker run -v $PWD:/repo --entrypoint /repo/build.sh pkg-builder-centos-stream-8
```

## Build package from github action

Please refer following example:

```
- name: Build tdvf
  uses: ./build/centos-stream-8/pkg-builder
  with:
    package: intel-mvp-tdx-tdvf
```

Please provides the package name via `package` parameter.
