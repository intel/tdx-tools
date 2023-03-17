
## Developer Guide

This section introduces the steps to build source from scratch on any *linux system
for hacking and developing purpose.

_NOTE:_ For production build in release purpose, please refer:
- Source RPM build [here](../build/rhel-8) for RHEL 8 build
- Debian build [here](../build/ubuntu-22.04) for Ubuntu 22.04 build

### Build and Setup Kernel

This [TDX kernel patchset](../build/common/patches-tdx-kernel-MVP-KERNEL-5.19-v2.2.tar.gz) includes
all patches based on kernel [v5.19](https://github.com/torvalds/linux/releases/tag/v5.19).


1. Ensure you have installed the necessary packages to build Linux kernel. e.g. `libncurses5-dev libssl-dev build-essential openssl zlibc minizip lib libidn11-dev libbidn11 bison flex`
Please install these packages via distro's package manager.

2. Download the kernel source code:

   ```
   $ wget https://github.com/intel/tdx-tools/blob/main/build/common/patches-tdx-kernel-MVP-KERNEL-5.19-v2.2.tar.gz
   $ tar xf patches-tdx-kernel-MVP-KERNEL-5.19-v2.2.tar.gz
   $ git clone --branch v5.19 https://github.com/torvalds/linux.git
   $ cd linux
   $ git am ../patches/*
   $ rm ../patches/ -fr
   ```

3. Kernel config

   - For RHEL
      Please use the common platform's kernel config file [here](../build/rhel-8/intel-mvp-tdx-kernel/tdx-base.config)
      for both TDX guest and host, then merge the detail config [sample](../build/rhel-8/intel-mvp-tdx-kernel/kernel-x86_64-rhel.config)

   - For Ubuntu
      Please use the common config file [here](../build/ubuntu-22.04/intel-mvp-tdx-kernel/debian.master/config/amd64/config.common.amd64)
      , then merge the TDX flavour [here](../build/ubuntu-22.04/intel-mvp-tdx-kernel/debian.master/config/amd64/config.flavour.generic)

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
   $ wget https://github.com/intel/tdx-tools/blob/main/build/common/patches-tdx-qemu-MVP-QEMU-7.0-v1.3.tar.gz
   $ tar xf patches-tdx-qemu-MVP-QEMU-7.0-v1.3.tar.gz
   $ git clone https://github.com/qemu/qemu.git
   $ cd qemu
   $ git checkout ad4c7f529a279685da84297773b4ec8080153c2d
   $ git am ../patches/*
   $ rm ../patches/ -fr
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
   Use [tdx-libvirt-2022.11.17](../build/rhel-8/intel-mvp-tdx-libvirt/build.sh) as example:

   ```
   $ git checkout tdx-libvirt-2022.11.17
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
   $ git clone https://github.com/tianocore/edk2.git
   ```

   Please switch to specific branch or tag for stable release.
   Use [tdvf-2023-ww01](../build/rhel-8/intel-mvp-ovmf/build.sh) as example:

   ```
   $ git checkout edk2-stable202211
   $ git submodule update --init
   ```

3. Build TDVF:

   ```
   $ make -C BaseTools
   $ make -C BaseTools/Source/C
   $ source ./edksetup.sh
   $ build -p OvmfPkg/IntelTdx/IntelTdxX64.dsc \
         -a X64 -b DEBUG \
         -t GCC5 \
         -D DEBUG_ON_SERIAL_PORT=TRUE \
         -D TDX_MEM_PARTIAL_ACCEPT=512 \
         -D TDX_EMULATION_ENABLE=FALSE \
         -D TDX_ACCEPT_PAGE_SIZE=2M
   $ build -p OvmfPkg/IntelTdx/IntelTdxX64.dsc \
         -a X64 -b RELEASE \
         -t GCC5 \
         -D DEBUG_ON_SERIAL_PORT=FALSE \
         -D TDX_MEM_PARTIAL_ACCEPT=512 \
         -D TDX_EMULATION_ENABLE=FALSE \
         -D TDX_ACCEPT_PAGE_SIZE=2M

   $ mkdir -p /opt/tdx/tdvf/
   $ cp Build/IntelTdx/DEBUG_GCC*/FV/OVMF.fd /opt/tdx/tdvf/OVMF.debug.fd
   $ cp Build/IntelTdx/RELEASE_GCC*/FV/OVMF.fd /opt/tdx/tdvf/
   $ cp Build/IntelTdx/DEBUG_GCC*/FV/OVMF_CODE.fd /opt/tdx/tdvf/OVMF_CODE.debug.fd
   $ cp Build/IntelTdx/RELEASE_GCC*/FV/OVMF_CODE.fd /opt/tdx/tdvf/
   $ cp Build/IntelTdx/RELEASE_GCC*/FV/OVMF_VARS.fd /opt/tdx/tdvf/
   ```
