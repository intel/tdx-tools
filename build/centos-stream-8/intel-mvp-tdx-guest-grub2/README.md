# Build Grub2 for TDX guest

This directory provides the build’s spec and script to generate Grub2 RPMs for TDX guest.
The downstream patches are held at <https://github.com/intel/grub-tdx>.

The build based on CentOS-Stream 8 distro:

- The spec files comes from <https://git.centos.org/rpms/grub2/blob/c8s/f/SPECS/grub2.spec>
- The grub.macros comes from <https://git.centos.org/rpms/grub2/blob/c8s/f/SOURCES/grub.macros>
- Please also setup build environment with CentOS Stream 8 in a development machine or container.

_NOTE:_

- The generated grub2.efi is not signed. Please sign it if you want to enable secure boot.
