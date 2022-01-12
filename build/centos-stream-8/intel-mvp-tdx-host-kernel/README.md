# Build TDX kernel for host
 
This directory provides the build’s spec, configs, and script to generate TDX
host kernel RPMs.
The downstream patches are held at <https://github.com/intel/tdx/tree/kvm>.

The build is based on CentOS-Stream 8 distro:
- The spec files comes from https://git.centos.org/rpms/kernel/tree/c8s
- Please also setup build environment with CentOS Stream 8 in a development
machine or container.
