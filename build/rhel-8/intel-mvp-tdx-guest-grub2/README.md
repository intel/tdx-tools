# Build Grub2 for TDX guest

This directory provides the build’s spec and script to generate Grub2 RPMs for TDX guest.
The downstream patches are held at <https://github.com/intel/grub-tdx>.

This build is for the RHEL 8.5 distro. Please setup a build environment with RHEL 8.5
on a development machine or container.

The some build sources are based on the following:

- The spec files comes from <https://git.centos.org/rpms/grub2/blob/c8s/f/SPECS/grub2.spec>
- The grub.macros comes from <https://git.centos.org/rpms/grub2/blob/c8s/f/SOURCES/grub.macros>

_NOTE:_

- The generated grub2.efi is not signed. Please sign it if you want to enable secure boot.
