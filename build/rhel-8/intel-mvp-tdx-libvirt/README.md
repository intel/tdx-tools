# Build libvirt package for TDX host

This directory provides the build’s spec and script to generate libvirt RPMs.
The downstream patches are held at <https://github.com/intel/libvirt-tdx>.

This build is for the RHEL 8.5 distro. Please setup a build environment with RHEL 8.5
on a development machine or container.

The spec file is based from <https://git.centos.org/rpms/libvirt/tree/c8s-stream-rhel>
