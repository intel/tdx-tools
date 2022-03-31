# Build Shim for TDX guest

This directory provides the build’s spec and script to generate shim RPMs for TDX guest.
The downstream patches are held at <https://github.com/intel/shim-tdx>.

This build is for the RHEL 8.5 distro. Please setup a build environment with RHEL 8.5
on a development machine or container.

The spec file is based from <https://git.centos.org/rpms/shim-unsigned-x64/blob/c8s/f/SPECS/shim-unsigned-x64.spec>

_NOTE:_

- The generated shimx64.efi, mmx64.efi and fbx64.efi are not signed. Please sign them if you want to enable secure boot.
