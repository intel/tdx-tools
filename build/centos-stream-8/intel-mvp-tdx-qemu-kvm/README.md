# Build Qemu package for TDX host

This directory provides the build’s spec and script to generate QEMU-KVM RPMs.
The downstream patches are held at <https://github.com/intel/qemu-tdx.git>.

The build based on CentOS-Stream 8 distro:
- The spec files comes from https://git.centos.org/rpms/qemu-kvm/tree/c8s-stream-rhel
- Please also setup build environment with CentOS Stream 8 in a development
machine or container.
