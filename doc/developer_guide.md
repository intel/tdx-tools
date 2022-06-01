
## Developer Guide

This section introduces the steps to build source from scratch on any *inux system
for hacking and developing purpose.

_NOTE:_ For production build in release purpose, please refer:
- Source RPM build [here](../build/rhel-8/) for RHEL 8 build
- Source RPM build [here](../build/centos-stream-8/) for CentOS Stream 8 build
- Debian build [here](../build/ubuntu-22.04/) for Ubuntu 22.04 build

### Build and Setup Kernel

TDX MVP stack uses [linux-kernel-dcp](https://github.com/intel/linux-kernel-dcp.git) for both host and guest kernel:

1. Ensure you have installed the necessary packages to build Linux kernel. e.g. `libncurses5-dev libssl-dev build-essential openssl zlibc minizip lib libidn11-dev libbidn11 bison flex`
Please install these packages via distro's package manager.

2. Download the kernel source code:

   ```
   $ git clone https://github.com/intel/linux-kernel-dcp.git
   ```

   Please switch to specific branch or tag for stable release. Use [SPR-BKC-PC-v4.20](https://github.com/intel/tdx-tools/blob/66b8d09600ddebdb8d460c4573cebc59bf099b06/build/rhel-8/intel-mvp-spr-kernel/build.sh#L8) as example:

   ```
   $ git checkout SPR-BKC-PC-v4.20
   ```

3. Kernel config

   Please use the common platform's kernel config file [here](https://github.com/intel/linux-kernel-dcp/tree/main/arch/x86/configs)
   for both TDX guest and host, or enable following specific kernel config on
   any existing kernel config
   ```
   CONFIG_INTEL_TDX_GUEST=y
   CONFIG_INTEL_TDX_ATTESTATION=y
   CONFIG_INTEL_TDX_HOST=y
   ```
   Please refer [TDX kernel documentation](https://github.com/intel/linux-kernel-dcp/blob/main/Documentation/virt/kvm/intel-tdx.rst)
   and [INTEL_TDX_GUEST](https://github.com/intel/linux-kernel-dcp/blob/33c8154984b118d8fb14b7462f264252968b786f/arch/x86/Kconfig#L877)
   and [INTEL_TDX_HOST](https://github.com/intel/linux-kernel-dcp/blob/33c8154984b118d8fb14b7462f264252968b786f/arch/x86/Kconfig#L1384)

4. Build kernel

   ```
   $ make -j 64
   $ make modules_install
   $ make install
   ```

### Build Qemu

1. Install dependent packages
   e.g. libglib2.0-dev libpixman-1-dev. You can check according to the build
   error info.

2. Download QEMU source code:

   ```
   $ git clone https://github.com/intel/qemu-dcp.git
   ```

   Please switch to specific branch or tag for stable release.
   Use [SPR-BKC-QEMU-pub-v1](https://github.com/intel/tdx-tools/blob/66b8d09600ddebdb8d460c4573cebc59bf099b06/build/rhel-8/intel-mvp-spr-qemu-kvm/build.sh#L8) as example:

   ```
   $ git checkout SPR-BKC-QEMU-pub-v1
   ```

3. Build QEMU:

   ```
   $ ./configure --target-list=x86_64-softmmu --prefix=/opt/tdx/qemu --disable-werror
   $ make -j 64
   $ make install
   ```

### Build Libvirt

1. Install dependent packages
   e.g. meson gnutls-devel rpcgen libxml2-devel python3-docutils yajl-devel libtirpc-devel.
   You can check according to the build error info.

2. Download libvirt source code:

   ```
   $ git clone https://github.com/intel/libvirt-tdx.git
   ```

   Please switch to specific branch or tag for stable release.
   Use [tdx-libvirt-2022.03.18](https://github.com/intel/tdx-tools/blob/66b8d09600ddebdb8d460c4573cebc59bf099b06/build/rhel-8/intel-mvp-tdx-libvirt/build.sh#L10) as example:

   ```
   $ git checkout tdx-libvirt-2022.03.18
   ```

3. Build libvirt:

   ```
   $ meson build -Ddriver_qemu=enabled -Ddriver_libvirtd=enabled -Ddriver_remote=enabled -Dqemu_user=qemu -Dqemu_group=qemu  -Dqemu_datadir=/opt/tdx/qemu/share --prefix=/opt/tdx/libvirt
   $ ninja -C build install
   ```

### Build TDVF

1. Install dependent packages
   e.g. libuuid-devel nasm iasl.
   You can check according to the build error info.

2. Download TDVF source code:

   ```
   $ git clone https://github.com/tianocore/edk2-staging.git
   ```

   Please switch to specific branch or tag for stable release.
   Use [tdvf-2022-ww10.2](https://github.com/intel/tdx-tools/blob/66b8d09600ddebdb8d460c4573cebc59bf099b06/build/rhel-8/intel-mvp-tdx-tdvf/build.sh#L7) as example:

   ```
   $ git checkout tdvf-2022-ww10.2
   $ git submodule update --init
   ```

3. Build TDVF:

   ```
   $ make -C BaseTools
   $ make -C BaseTools/Source/C
   $ source ./edksetup.sh
   $ build -p OvmfPkg/OvmfPkgX64.dsc \
      -a X64 -b DEBUG \
      -t GCC5 \
      -D DEBUG_ON_SERIAL_PORT=TRUE \
      -D TDX_MEM_PARTIAL_ACCEPT=512 \
      -D TDX_EMULATION_ENABLE=FALSE \
      -D TDX_ACCEPT_PAGE_SIZE=2M
   $ build -p OvmfPkg/OvmfPkgX64.dsc \
      -a X64 -b RELEASE \
      -t GCC5 \
      -D DEBUG_ON_SERIAL_PORT=FALSE \
      -D TDX_MEM_PARTIAL_ACCEPT=512 \
      -D TDX_EMULATION_ENABLE=FALSE \
      -D TDX_ACCEPT_PAGE_SIZE=2M

   $ mkdir -p /opt/tdx/tdvf/
   $ cp Build/OvmfX64/DEBUG_GCC*/FV/OVMF.fd /opt/tdx/tdvf/OVMF.debug.fd
   $ cp Build/OvmfX64/RELEASE_GCC*/FV/OVMF.fd /opt/tdx/tdvf/
   $ cp Build/OvmfX64/DEBUG_GCC*/FV/OVMF_CODE.fd /opt/tdx/tdvf/OVMF_CODE.debug.fd
   $ cp Build/OvmfX64/RELEASE_GCC*/FV/OVMF_CODE.fd /opt/tdx/tdvf/
   $ cp Build/OvmfX64/RELEASE_GCC*/FV/OVMF_VARS.fd /opt/tdx/tdvf/
   $ cp Build/OvmfX64/RELEASE_GCC*/X64/DumpTdxEventLog.efi /opt/tdx/tdvf/DumpTdxEventLog.efi
   ```
