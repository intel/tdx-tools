
# Full Stack build for RHEL 8

- Packaging project for following components

  - [TDX kernel](./intel-mvp-tdx-kernel/): Sapphire Rapids kernel for both host and guest
  - [TDX qemu](./intel-mvp-tdx-qemu-kvm/): QEMU KVM for Sapphire Rapids features
  - [TDX Libvirt](./intel-mvp-tdx-libvirt/): Libvirt with TDX modification
  - [TDX TDVF](./intel-mvp-tdx-tdvf/): TDVF firmware for TD guest
  - [TDX Guest Grub2](./intel-mvp-tdx-guest-grub2/): Grub2 for TD guest
  - [TDX Guest Shim](./intel-mvp-tdx-guest-shim/): SHIM for TD guest

- Guest image tool

  Create TD guest image via kickstart tool, refer [create guest image](../../doc/create_guest_image.md)

**NOTE:**

  To build packages, please setup a RHEL development machine with Red Hat
  subscription, and run

  ```
  cd build/rhel-8
  ./build-repo.sh
  ```

  There is no [package builder docker](../centos-stream-8/README.md) provided
  like CentOS Stream 8.
