
# TDX Tests

## 1. Overview

TDX tests are designed to cover basic acceptance tests, functionality, workload
and environment tests for TDX. It also provides tests for interoperability tests
with TDX and AMX. The tests implementation depends on PyCloudStack framework.
The tests execution should be on TDX enabled Linux platform with TDX-enabled kernel,
Qemu, Libvirt installed.

The tests can be categorized as following.

| Category  |        Tests         | Prerequisite |
| ----------| -------------------- |--------------|
|    BAT    | test_vm_coexist      |              |
|    BAT    | test_tdx_guest_status|              |
|    BAT    | test_tdx_host_status |              |
|    BAT    | test_tdvm_lifecycle  |              |
|    BAT    | test_multiple_tdvms  |              |
|Environment| test_tdvm_tsc        |              |
|Environment| test_tdvm_network    |              |
|Environment| test_max_cpu         |              |
| Lifecycle | test_vm_shutdown_mode|              |
| Lifecycle | test_vm_shutdown_qga |       1      |
| Lifecycle | test_vm_reboot_qga   |       1      |
| Lifecycle | test_acpi_reboot     |              |
| Lifecycle | test_acpi_shutdown   |              |
| Interop   | test_amx_docker_tf   |      2,4     |
| Interop   | test_amx_vm_tf       |       5      |
| Workload  | test_workload_nginx  |      2,3     |
| Workload  | test_workload_redis  |      2,3     |
|           |                      |              |

- Prerequisite: Please refer to corresponding items in section `Prerequisite of tests` below.

## 2. Prerequisite

### Enable TDX

Please make sure your Linux host has TDX enabled.

### Create Guest Image

Please refer to [Setup TDX Guest Image](/doc/create_guest_image.md) to create guest image, which will be used in tests
running. It uses `RHEL` as an example distro.

### Prepare Environment

- Install required packages:

  If your host distro is RHEL 8:

    ```
    sudo dnf install python3-virtualenv python3-libvirt libguestfs-devel libvirt-devel python3-devel gcc gcc-c++
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

### Prerequisite of tests

Basic guest image is required for all the tests. Additional requirement to guest image exsits for part of the tests.
Please check prerequisite of each test and take corresponding action as following.

- Prerequisite:
    1. Install Qemu guest agent in guest image
    2. Install docker in guest image
    3. For workload tests, make sure the latest docker image is in guest image
       test_workload_nginx - it needs docker image nginx:latest
       test_workload_redis - it needs docker image redis:latest
    4. Make sure docker image intel/tf-nightly:2.8.0 is in guest image
    5. Install intel-tensorflow-avx512 in guest image. Download DIEN_bf16 model and put it under /root in guest image.
       For ubuntu guest image
       
       ```
       pip3 install intel-tensorflow-avx512==2.11.0
       wget https://storage.googleapis.com/intel-optimized-tensorflow/models/v2_5_0/dien_bf16_pretrained_opt_model.pb
       ```
       
       For rhel guest image, please upgrade python to python 3.8 first.
       
       ```

       pip3 install intel-tensorflow-avx512==2.11.0
       wget https://storage.googleapis.com/intel-optimized-tensorflow/models/v2_5_0/dien_bf16_pretrained_opt_model.pb
       ```

## Run Tests

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
  ./run.sh -c tests/test_tdvm_lifecycle.py -c tests/test_vm_coexist.py
  ```

- User can specify guest image OS with `-g`. Currently it supports `rhel`, and `ubuntu`. RHEL guest image is used by default if `-g` is not specified:

    ```
    sudo ./run.sh -g ubuntu -s all
    ```
