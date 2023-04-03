%global debug_package %{nil}

# This spec file began as CentOS's ovmf spec file, then cut down and modified.

Name:       intel-mvp-ovmf
Version:    mvp8
Release:    stable202302
Summary:    UEFI firmware for 64-bit virtual machines supporting trusted domains
Group:      Applications/Emulators
License:    BSD and OpenSSL and MIT
URL:        http://www.tianocore.org

Source0: edk2.tar.gz

BuildRequires:  python2-devel
BuildRequires:  libuuid-devel
BuildRequires:  /usr/bin/iasl
BuildRequires:  binutils gcc git

# Only OVMF includes 80x86 assembly files (*.nasm*).
BuildRequires:  nasm

# Only OVMF includes the Secure Boot feature, for which we need to separate out
# the UEFI shell.
BuildRequires:  dosfstools
BuildRequires:  mtools
BuildRequires:  genisoimage

# For generating the variable store template with the default certificates
# enrolled, we need qemu-kvm (from base RHEL7) such that it includes basic OVMF
# support (split pflash) -- see RHBZ#1032346.
BuildRequires:  qemu-kvm >= 1.5.3-44

# For verifying SB enablement in the above variable store template, we need a
# trusted guest kernel that prints "Secure boot enabled". See RHBZ#903815.
BuildRequires: kernel >= 3.10.0-52
BuildRequires: rpmdevtools

BuildArch:  noarch

# OVMF includes the Secure Boot feature; it has a builtin OpenSSL library.
Provides:   bundled(openssl) = 1.1.1g

%description
OVMF (Open Virtual Machine Firmware) is a project to enable UEFI support for
Virtual Machines. This package contains a sample 64-bit UEFI firmware for QEMU
and KVM supporting trusted domains.

%prep
%setup -q -n edk2

# Done by %setup, but we do not use it for the auxiliary tarballs
chmod -Rf a+rX,u+w,g-w,o-w .

%build
export PYTHON_COMMAND=python3

make -C BaseTools
source ./edksetup.sh
build -p OvmfPkg/IntelTdx/IntelTdxX64.dsc \
      -a X64 -b DEBUG \
      -t GCC5 \
      -D DEBUG_ON_SERIAL_PORT=TRUE \
      -D TDX_MEM_PARTIAL_ACCEPT=512 \
      -D TDX_EMULATION_ENABLE=FALSE \
      -D SECURE_BOOT_ENABLE=TRUE \
      -D TDX_ACCEPT_PAGE_SIZE=2M

build -p OvmfPkg/IntelTdx/IntelTdxX64.dsc \
      -a X64 -b RELEASE \
      -t GCC5 \
      -D DEBUG_ON_SERIAL_PORT=FALSE \
      -D TDX_MEM_PARTIAL_ACCEPT=512 \
      -D TDX_EMULATION_ENABLE=FALSE \
      -D SECURE_BOOT_ENABLE=TRUE \
      -D TDX_ACCEPT_PAGE_SIZE=2M

%install
mkdir -p %{buildroot}/usr/share/qemu
cp Build/IntelTdx/DEBUG_GCC*/FV/OVMF.fd %{buildroot}/usr/share/qemu/OVMF.debug.fd
cp Build/IntelTdx/RELEASE_GCC*/FV/OVMF.fd %{buildroot}/usr/share/qemu/
cp Build/IntelTdx/DEBUG_GCC*/FV/OVMF_CODE.fd %{buildroot}/usr/share/qemu/OVMF_CODE.debug.fd
cp Build/IntelTdx/RELEASE_GCC*/FV/OVMF_CODE.fd %{buildroot}/usr/share/qemu/
cp Build/IntelTdx/RELEASE_GCC*/FV/OVMF_VARS.fd %{buildroot}/usr/share/qemu/

%files
%license License.txt
/usr/share/qemu/OVMF.debug.fd
/usr/share/qemu/OVMF.fd
/usr/share/qemu/OVMF_CODE.debug.fd
/usr/share/qemu/OVMF_CODE.fd
/usr/share/qemu/OVMF_VARS.fd

