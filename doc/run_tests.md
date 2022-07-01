## TDX Tests

TDX tests are used to validate basic functionality of TDX software stack. The tests focus on TDVM lifecycle management
 and environment validation.

### Create Cloud Image

Please refer [Setup TDX Guest Image](/doc/create_guest_image.md) to create guest image, which will be used in tests
running. It uses `CentOS Stream 8` as example distro.

### Prerequisite

- Install required packages:

  If your host distro is RHEL 8.5 or CentOS Stream 8:

    ```
    sudo dnf install python3-virtualenv python3-libvirt-6.0.0 libguestfs-devel libvirt-devel python3-devel
    ```

  If your host distro is Ubuntu 22.04:

    ```
    sudo apt install python3-virtualenv python3-libvirt libguestfs-dev libvirt-dev python3-dev
    ```

- Make sure libvirt service is started. If not, start libvirt service.

     ```
    sudo systemctl status libvirtd
    sudo systemctl start libvirtd
    ```

- Setup environment:

    Run below command to setup the pythone environment

    ```
    cd tdx-tools/tests/
    source setupenv.sh
    ```

- Generate artifacts.yaml

    Please refer to tdx-tools/tests/artifacts.yaml.template and generate tdx-tools/tests/artifacts.yaml. Update "source"
    and "sha256sum" to indicate the location of guest image and guest kernel.

- Generate keys

    Generate a pair of keys that will be used in test running.

    ```
    ssh-keygen
    ```

    The keys should be named "vm_ssh_test_key" and "vm_ssh_test_key.pub" and located under tdx-tools/tests/tests/

### Run Tests

- Run all tests:

  ```
  sudo ./run.sh -s all
  ```

- Run some case modules: `./run.sh -c <test_module1> -c <test_module2>`

  For example,

  ```
  ./run.sh -c tests/test_tdvm_lifecycle.py
  ```

- Run specific cases: `./run.sh -c <test_module1> -c <test_module1>::<test_name>`

  For example,

  ```
  ./run.sh -c tests/test_tdvm_lifecycle.py::test_tdvm_lifecycle_virsh_suspend_resume
  ```

  _NOTE:_
  Before running test tdx-tools/tests/tests/test_workload_redis.py, please make sure

  - The guest image has docker/podman installed.
  - The guest image contains docker image redis:latest.

- User can specify guest image OS with `-g`. Currently it supports `rhel`, `centosstream`
and `ubuntu`. RHEL guest image is used by default if `-g` is not specified:

    ```
    sudo ./run.sh -g centosstream -s all
    ```
