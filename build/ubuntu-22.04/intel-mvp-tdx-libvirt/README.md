# Build libvirt package for TDX host

This directory provides the build scripts to generate libvirt Debian packages.
The downstream patches are held at <https://github.com/intel/libvirt-tdx>.

The build based on Ubuntu 22.04 distro:

- The Ubuntu control files come from <http://archive.ubuntu.com/ubuntu/pool/main/libv/libvirt/libvirt_8.0.0-1ubuntu7.debian.tar.xz>
- Please also setup build environment with Ubuntu 22.04 in a development
machine or container.
