## TDX Tests

TDX tests are used to validate basic functionality of TDX software stack. The tests focus on TDVM lifecycle management
 and environment validation.

### Create Cloud Image

Please refer to [Setup TDX Guest Image](/doc/create_guest_image.md) to create guest image, which will be used in tests
running. It uses `RHEL 8.6` as an example distro.

### Prerequisite

1. Install required packages:

    - If your host distro is RHEL 8.6:

        ```
        sudo dnf install python3-virtualenv python3-libvirt libguestfs-devel libvirt-devel python3-devel gcc gcc-c++
        ```

    - If your host distro is Ubuntu 22.04:

        ```
        sudo apt install python3-virtualenv python3-libvirt libguestfs-dev libvirt-dev python3-dev
        ```

2. Make sure libvirt service is started.

    ```
    sudo systemctl status libvirtd
    sudo systemctl start libvirtd
    ```

3. Setup test environment.

    ```
    cd tdx-tools/tests/
    source setupenv.sh
    ```

4. Generate artifacts.yaml.

    Please refer to tdx-tools/tests/artifacts.yaml.template and generate tdx-tools/tests/artifacts.yaml. Update "source"
    and `sha256sum` to indicate the location of guest image and guest kernel. The following content is an example of using Ubuntu guest image and guest kernel.

    ```
    latest-guest-image-ubuntu:
      source: </path/to/>td-guest-ubuntu-22.04-test.qcow2.tar.xz

    latest-guest-kernel-ubuntu:
      source: </path/to/>vmlinuz-jammy
    ```

5. Generate a pair of keys that will be used in test running.

    ```
    ssh-keygen
    ```

    The keys should be named `vm_ssh_test_key` and `vm_ssh_test_key.pub` and located under tdx-tools/tests/tests/

### Run Tests

1. Run all tests:

    ```
    sudo ./run.sh -s all
    ```

2. Run some case modules: `./run.sh -c <test_module1> -c <test_module2>`

    ```
    ./run.sh -c tests/test_tdvm_lifecycle.py
    ```

3. Run specific cases: `./run.sh -c <test_module1> -c <test_module1>::<test_name>`

    ```
    ./run.sh -c tests/test_tdvm_lifecycle.py::test_tdvm_lifecycle_virsh_suspend_resume
    ```

    **NOTE**:
    Before running test `tdx-tools/tests/tests/test_workload_redis.py`, please make sure

    - The guest image has docker/podman installed.
    - The guest image contains docker image redis:latest. You can pull the latest
    redis docker image from [docker hub](https://hub.docker.com/_/redis)

4. User can specify guest image OS with `-g`. It supports `ubuntu` and `rhel`.
RHEL guest image is used by default if `-g` is not specified:

    - For example, running tests using `ubuntu` guest image:

        ```
        sudo ./run.sh -g ubuntu -s all
        ```
