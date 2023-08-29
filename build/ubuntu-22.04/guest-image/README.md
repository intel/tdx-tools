# Ubuntu 22.04 TDX Guest Image

Customize Ubuntu 22.04 cloud image and install TDX guest kernel.

## Prerequisites

- The script will install TDX guest packages from `../guest_repo/`. If not present, please build the guest repo in the upper build directory:

`./pkg-builder -c "./build-repo.sh guest"`

- Install `yq`

` wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq && chmod +x /usr/bin/yq`

- Install qemu-img and virt-customize. For Ubuntu:

`sudo apt install -y qemu-utils qemu-utils libguestfs-tools virtinst genisoimage cloud-init`

- Install qemu-img and virt-customize. For RHEL:

`sudo apt install -y libguestfs-tools-c qemu-img virt-install genisoimage cloud-init`

## Steps

The section describe how to build a guest image with the helper script `create-ubuntu-image.sh`. 

```
sudo ./create-ubuntu-image.sh -h
```
Show more help info.

1. Build a default disk image
  
  ```
  sudo ./create-ubuntu-image.sh -r $GUEST_REPO -f
  ```
  The script will build a 20G disk image at /tmp/tdx-guest-ubuntu-22.04.qcow2. It has a `root` user with password `xxxx`. The option `-f` indicate that the existing image will be overwritten forcibly.

  The `GUEST_REPO` is the path to a guest repo, which has the following file hierarchy.

  ```
    guest_repo/jammy
    |- all/
    |- amd64/
  ```

  The guest repo can be a local repo, such as the repo built by `build_repo.sh`. If you build a local repo previously, you can run the command simply.

  ```
  sudo ./create-ubuntu-image.sh -f -r ../guest_repo/
  ```

  
  If the guest repo is a remote repo, such as "https://host/guest_repo", an option `-v` should be appended to specify the version of the guest kernel.

  ```
  sudo ./create-ubuntu-image.sh -r $GUEST_REPO -f -v 5.19.17-mvp29v4+4-generic
  ```

  Furthermore, if the remote repo requires user authentication, you can provide a config file, which will be placed in `/etc/apt/auth.conf.d` of the vm. The option `-a` will help copy the config file.

  ```
  sudo ./create-ubuntu-image.sh -r $GUEST_REPO -f -v 5.19.17-mvp29v4+4-generic -a $AUTH_FILE
  ```

  NOTE:
  - `sudo` is not required if current user is in libvirt (RHEL style) or libvirt-qemu (Ubuntu style)
  - By default, the output file will be put at /tmp/tdx-guest-ubuntu-22.04.qcow2


2. Specify the size of disk image

  ```
  sudo ./create-ubuntu-image.sh -r ../guest_repo/ -f -s 50G
  ```



3. Specify the output file name

  ```
  sudo ./create-ubuntu-image.sh -r ../guest_repo/ -f -o mytest.qcow2
  ```
  NOTE:
  - Please make sure the output file name is ends with `*.qcow2`


4. Specify the `user name`, `password` and `hostname`

  ```
  sudo ./create-ubuntu-image.sh -r ../guest_repo/ -f -o mytest.qcow2 -u tdx -p changeme -n tdx-guest
  ```

5. Build image with test suite

  ```
  sudo ./create-ubuntu-image.sh -f -r ../guest_repo/ -t
  ```
  The option `-t` helps to install test suite in the guest image. The option `-e` helps to specify a host repo to install `qemu-guest-agent`. The option `-d` opens the debug mode, if you use `root` user of guest, the option must be added.

6. Build image with amber-cli
  
  ```
  sudo ./create-ubuntu-image.sh -f -r ../guest_repo/ -x ./cloud-init-data/init-scripts/install-amber-cli.sh
  ```


7. Customize guest image

7.1 Customize user-data for cloud-init

The cloud-init is the center of own guest building, therefore we provides two options to extend the basic guest image or the testing guest image. The option `-g` appends the customized cloud-config to user-data, and the option `-x` appends a script to it. Remember the first of the cloud-config must be `#cloud-config` and the first line of the scripts must be `#!`. 

For example, create anther cloud-config and modify it to install a binary `tree` in the guest image.

```
cp ./cloud-init-data/user-data-basic/cloud-config-base-template.yaml ./cloud-init-data/cloud-config-example.yaml

echo -e "packages:\n  - tree" >>  ./cloud-init-data/cloud-config-example.yaml

sudo ./create-ubuntu-image.sh -f -r ${GUEST_REPO} -g ./cloud-init-data/cloud-config-example.yaml
```


The note we must mention is that, the `runcmd` of the cloud-config and script in the user-data are running in the context without environment variables, if your commands depend on some of them, such a network proxy, please declare them manually. For example, exporting environment variables at the beginning of your scripts.

```
#!/bin/bash

while read env_var; do
  export "$env_var"
done < /etc/environment

...
```

For example, install amber-cli during the cloud-init.

```
sudo ./create-ubuntu-image.sh -f -r ${GUEST_REPO} -x ./cloud-init-data/init-scripts/install-amber-cli.sh
```

7.2 Customize scripts before or after cloud-init

Given that some works can be executed before cloud-init or after cloud-init, the option `-i` and the option `-d` provide hooks there respectively. The scripts you provide via `-i` and `-d` will be executed by the tool `virt-customize` with shell interpreter `/bin/sh`. Unfortunately, the bash syntax is not compatible with sh completely, make sure your scripts can be explained by the sh. 

For example, you can install amber-cli before cloud-init by the command, 

```
sudo ./create-ubuntu-image.sh -f -r ${GUEST_REPO} -i ./cloud-init-data/init-scripts/install-amber-cli.sh
```

or install amber-cli after cloud-init by the command.

```
sudo ./create-ubuntu-image.sh -f -r ${GUEST_REPO} -d ./cloud-init-data/init-scripts/install-amber-cli.sh
```

The `virt-customize` is a powerful tool, but it does not launch a real vm, therefore daemon services are inaccessible, some commands, such `docker pull` can not be executed. Such commands should be appended in user-data as above mentioned.

Please refer [cloud-init](https://cloudinit.readthedocs.io/en/latest/), [user-data](https://cloudinit.readthedocs.io/en/latest/explanation/format.html#) and [cloud-config](https://cloudinit.readthedocs.io/en/latest/reference/modules.html) to get more info about `cloud-init`. Besides, two templates [cloud-config-base-template.yaml](build/ubuntu-22.04/guest-image/cloud-init-data/user-data-basic/cloud-config-base-template.yaml) and [cloud-config-test-suite-template.yaml](build/ubuntu-22.04/guest-image/cloud-init-data/user-data-customized/cloud-config-test-suite-template.yaml) are direct examples.

Refer [virt-customize](https://www.libguestfs.org/virt-customize.1.html) to learn more about it. 



