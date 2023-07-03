# TD Migration

## 1. Overview

This feature is to meet the CSP who may want to relocate/migrate an executing Trust Domain (TD) from a source Trust Domain Extension (TDX) platform to a destination TDX platform in the cloud environment. Currently, td-migration only works on **TDX 1.5 (kernel-v6.2/tag 2023ww15 and 2023ww27)**. TDX 1.0 releases do not support this feature. It also requires `MigTD` which can be built via build tool in tdx-tools. Please make sure TDX migration package is installed before running migration. The default installation path of `migtd.bin` is `/usr/share/td-migration/migtd.bin`.

In this doc, the TD being migrated is called the source TD, and the TD created as a result of the migration is called the destination TD.

**Prerequisite**: Please install all attestation required components on both source and destination platform because pre-migration includes mutual attestation for MigTD. If pre-migration is successful, it means MigTD attestation pass. Please refer to
[TDX End to End Attestation](https://github.com/intel/tdx-tools/wiki/5.-TDX-End-to-End-Attestation) to setup attestation environment.

## 2. TD migration

TD migration supports several features as below. The scripts described later will help you go through each feature. It supports to run TD migration in single host or cross host scenario with different parameters.

**NOTE**: Post-copy and Multi-stream are not supported to be used at the same time.

### 2.1 Pre-copy migration

#### 2.1.1 Single Host Test Steps

**NOTE**: Each command needs one terminal, so please prepare 5 terminal tabs firstly or use tmux.

- Create Migration TDs

    ```bash
    # create the MigTD_src to bind with src user TD 
    sudo ./mig-td.sh -t src

    # create the MigTD_dst to bind with dst user TD 
    sudo ./mig-td.sh -t dst
    ```

    Use `-m` parameter to set the alternative path of `migtd.bin`.

    ```bash
    sudo ./mig-td.sh -m path/to/migtd.bin -t src
    ```

    If MigTD starts successfully, the console will display the below message.

    ```console
    MigTD Version - 0.2.2
    Loop to wait for request
    ```

- Launch Source and Destination TDs

    You can use direct boot or grub boot to launch TD.

    - Direct Boot

        NOTE: The default ROOT_PARTITION is `/dev/vda1`, which is for ubuntu guest TD. For RHEL, please add parameter `-r /dev/vda3`

        ```bash
        # create the source TD
        sudo ./user-td.sh -t src -i path/to/image -k path/to/kernel

        # create the destiation TD
        sudo ./user-td.sh -t dst -i path/to/image -k path/to/kernel
        ```

    - GRUB Boot

        ```bash
        # create the source TD
        sudo ./user-td.sh -t src -i path/to/image -b grub

        # create the destiation TD
        sudo ./user-td.sh -t dst -i path/to/image -b grub
        ```

    For attestation, you need to enable tdvmcall or vsock for TD to connect with QGS.

    ```bash
    # tdvmcall
    sudo ./user-td.sh -t src -i path/to/image -b grub -q tdvmcall
    sudo ./user-td.sh -t dst -i path/to/image -b grub -q tdvmcall

    # vsock
    sudo ./user-td.sh -t src -i path/to/image -b grub -q vsock
    sudo ./user-td.sh -t dst -i path/to/image -b grub -q vsock
    ```

- Pre-Migration

    Wait a while for source and destination TDs to be ready. Before starting pre-migration, create a channel between source and destination side migration TDs.

    ```bash
    sudo ./connect.sh
    ```

    Check if it creates successfully.

    ```console
    $ ps axu| grep socat
    root      112608  0.0  0.0  27828  3072 pts/5    S    Mar22   0:00 socat TCP4-LISTEN:9009,reuseaddr VSOCK-LISTEN:1234,fork
    root      112609  0.0  0.0  27828  3072 pts/5    S    Mar22   0:00 socat TCP4-CONNECT:127.0.0.1:9009,reuseaddr VSOCK-LISTEN:1235,fork
    ```

    Start pre-migration.

    ```bash
    sudo ./pre-mig.sh
    ```

    Check pre-migrate status.

    ```console
    $ dmesg
    [110722.032798] kvm_intel: Pre-migration is done, userspace pid=368587
    [110722.074132] kvm_intel: Pre-migration is done, userspace pid=368515
    ```

- Start Migration

    Start transferring TD's data from source to destination.

    ```bash
    sudo ./mig-flow.sh
    ```

    After migration is complete, you will see the following message and destination TD is ready.

    ```console
    $ dmesg
    [110983.886989] migration flow is done, userspace pid 397008
    ```

#### 2.1.2 Cross Host Test Steps

**NOTE:** For cross-host live migration, you have to set up NFS server or use other ways to share the image/kernel for source TD and destination TD before starting the migration. (It means source TD and destination TD can access the shared image/kernel together)

- Create Migration TDs

    ```bash
    # create the MigTD_src to bind with src user TD 
    sudo ./mig-td.sh -t src

    # create the MigTD_dst to bind with dst user TD 
    sudo ./mig-td.sh -t dst
    ```

    Use `-m` parameter to set the alternative path of `migtd.bin`.

    ```bash
    sudo ./mig-td.sh -m path/to/migtd.bin -t src
    ```

    If MigTD starts successfully, the console will display the below message.

    ```console
    MigTD Version - 0.2.2
    Loop to wait for request
    ```

- Launch Source and Destination TDs

    You can use direct boot or grub boot to launch TD.

    - Direct Boot

        NOTE: The default ROOT_PARTITION is `/dev/vda1`, which is for ubuntu guest TD. For RHEL, please add parameter `-r /dev/vda3`

        ```bash
        # create the source TD on source platform
        sudo ./user-td.sh -t src -i path/to/image -k path/to/kernel

        # create the destiation TD on destination platform
        sudo ./user-td.sh -t dst -i path/to/image -k path/to/kernel
        ```

    - GRUB Boot

        ```bash
        # create the source TD on source platform
        sudo ./user-td.sh -t src -i path/to/image -b grub

        # create the destiation TD on destination platform
        sudo ./user-td.sh -t dst -i path/to/image -b grub
        ```

- Pre-Migration

    Wait a while for source and destination TDs to be ready. Before starting pre-migration, create a channel between source and destination side migration TDs.

    ```bash
    sudo ./connect.sh -t remote -i <DEST_IP>
    ```

    Start pre-migration.

    ```bash
    sudo ./pre-mig.sh -t remote -i <DEST_IP>
    ```

    Check pre-migrate status on both source and destination platform.

    ```console
    $ dmesg
    [110722.032798] kvm_intel: Pre-migration is done, userspace pid=368587
    ```

- Start Migration

    Start transferring TD's data from source to destination.

    ```bash
    sudo ./mig-flow.sh -i <DEST_IP>
    ```

    After migration is complete, you will see the following message and destination TD is ready.

    ```console
    $ dmesg
    [110983.886989] migration flow is done, userspace pid 397008
    ```

### 2.2 Post-copy migration

It supports to run post-copy migration for TD. The steps are similar with pre-copy migration, except
 for extra parameter when starting migration.

- Start Migration with post-copy

    ```bash
    sudo ./mig-flow.sh -c
    ```

    After migration is complete, you will see the following message and destination TD is ready.

    ```console
    $ dmesg
    [110983.886989] migration flow is done, userspace pid 397008
    ```

### 2.3 Multi-stream migration

It supports to run multi-stream migration for TD. The steps are similar with pre-copy migration, except
 for extra parameter when starting migration.

- Start Migration with multi-stream enabled with specific `multifd_channel` number

    ```bash
    sudo ./mig-flow.sh -m -n <number_of_multifd_channel>
    ```

    After migration is complete, you will see the following message and destination TD is ready.

    ```console
    $ dmesg
    [110983.886989] migration flow is done, userspace pid 397008
    ```

### 2.4 Pre-binding

It supports to pre-binding a user TD with `migtd_hash` in case `migTD` is not created yet. The real binding needs to be done before pre-migration. Please run below command to go through migration using pre-binding. 

- Create Migration TDs, please refer to previous step

- Create source TD and destination TD

    ```bash
    sudo ./user-td.sh -t src -i <path/to>/image -b grub -g -v <migtd_hash>
    sudo ./user-td.sh -t dst -i <path/to>/image -b grub -g -v <migtd_hash>

    ```

- Pre migration

    ```bash
    sudo ./connect.sh
    # Bind migTD PID to user TD before pre-migration starts
    sudo ./pre-mig.sh -b
    ```

- Start Migration

    ```bash
    sudo ./mig-flow.sh
    ```

    After migration is complete, you will see the following message and destination TD is ready.

    ```console
    $ dmesg
    [110983.886989] migration flow is done, userspace pid 397008
    ```

## 3. Related Specification

1. [Intel® TDX Module Architecture Specification: TD
Migration](https://cdrdv2.intel.com/v1/dl/getContent/733578)
2. [Intel® TDX Migration TD Design Guide](https://cdrdv2.intel.com/v1/dl/getContent/733580)
