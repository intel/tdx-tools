# Build libvirt package for TDX host

This directory provides the build’s spec and script to generate libvirt RPMs.
The downstream patches are held at <https://github.com/intel/libvirt-tdx>.

The build based on CentOS-Stream 8 distro:

- The spec files comes from <https://git.centos.org/rpms/libvirt/tree/c8s-stream-rhel>
- Please also setup build environment with CentOS Stream 8 in a development
machine or container.
