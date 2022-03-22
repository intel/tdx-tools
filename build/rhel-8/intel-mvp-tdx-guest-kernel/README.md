# Build TDX kernel for guest
 
This directory provides the build’s spec, configs, and script to generate TDX
guest kernel RPMs.
The downstream patches are held at <https://github.com/intel/tdx/tree/guest>.

This build is for the RHEL 8.5 distro. Please setup a build environment with RHEL 8.5
on a development machine or container.

The spec file is based from https://git.centos.org/rpms/kernel/tree/c8s
