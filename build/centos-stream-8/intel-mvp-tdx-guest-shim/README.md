# Build Shim for TDX guest

This directory provides the build’s spec and script to generate shim RPMs for TDX guest.
The downstream patches are held at <https://github.com/intel/shim-tdx>.

The build based on CentOS-Stream 8 distro:

- The spec files comes from <https://git.centos.org/rpms/shim-unsigned-x64/blob/c8s/f/SPECS/shim-unsigned-x64.spec>
- Please also setup build environment with CentOS Stream 8 in a development machine or container.

_NOTE:_

- The generated shimx64.efi, mmx64.efi and fbx64.efi are not signed. Please sign them if you want to enable secure boot.
