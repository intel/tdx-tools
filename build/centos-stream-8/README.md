
# Full Stack build for CentOS Stream 8

- Packaging project for following components

  - [TDX kernel](./intel-mvp-tdx-kernel/): TDX kernel for both host and guest
  - [TDX qemu](./intel-mvp-tdx-qemu-kvm/): QEMU KVM for TDX features
  - [TDX Libvirt](./intel-mvp-tdx-libvirt/): Libvirt with TDX modification
  - [TDX TDVF](./intel-mvp-tdx-tdvf/): TDVF firmware for TD guest
  - [TDX Guest Grub2](./intel-mvp-tdx-guest-grub2/): Grub2 for TD guest
  - [TDX Guest Shim](./intel-mvp-tdx-guest-shim/): SHIM for TD guest

- Package Builder Docker

  Run `./build-repo.sh` within CentOS Stream Docker, so package can be built on a Linux
  machine installed any other distros like Ubuntu, Debian etc

  Please refer [using pkg-builder](./pkg-builder/README.md)

  For the native build on a CentOS stream development machine, just run:

  ```
  cd build/centos-stream-8
  ./build-repo.sh
  ```

- Guest image tool

  Create TD guest image via kickstart tool, refer [create guest image](../../doc/create_guest_image.md)
