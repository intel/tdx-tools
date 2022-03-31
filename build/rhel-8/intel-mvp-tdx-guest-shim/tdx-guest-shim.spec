# # This file began as a copy of CentOS's shim-unsigned-x64.spec, then modified.

%global pesign_vre 0.106-1
%global openssl_vre 1.0.2j

%global efidir %(eval echo $(grep ^ID= /etc/os-release | sed -e 's/^ID=//' -e 's/rhel/redhat/'))
%global shimrootdir %{_datadir}/shim/
%global shimversiondir %{shimrootdir}/%{version}-%{release}
%global efiarch x64
%global efiarchlc X64
%global shimdir %{shimversiondir}/%{efiarch}
%global efialtarch ia32
%global shimaltdir %{shimversiondir}/%{efialtarch}

%global debug_package %{nil}
%global __debug_package 1
%global _binaries_in_noarch_packages_terminate_build 0
%global __debug_install_post %{SOURCE100} %{efiarch}
%undefine _debuginfo_subpackages

# currently here's what's in our dbx: nothing
%global dbxfile %{nil}

Name:		intel-mvp-tdx-guest-shim
Version:	15.4
Release:	10.mvp5%{?dist}
Summary:	First-stage UEFI bootloader
ExclusiveArch:	x86_64
License:	BSD
URL:		https://github.com/rhboot/shim

%define source_url_prefix https://git.centos.org/rpms/shim-unsigned-x64/raw/4a1067f5a14cb741a9b3575ab980ce168e3fbcd3/f/SOURCES/

Source0:	%{version}/shim-%{version}.tar.gz
Source1:	%{source_url_prefix}/redhatsecurebootca5.cer
%if 0%{?dbxfile}
Source2:	%{dbxfile}
%endif
Source3:	%{source_url_prefix}/sbat.redhat.csv

Source10:	patches-tdx-shim-%{version}.tar.gz

Source100:	%{source_url_prefix}/shim-find-debuginfo.sh

Patch0001:	%{source_url_prefix}/0001-Fix-a-broken-file-header-on-ia32.patch

BuildRequires:	gcc make
BuildRequires:	elfutils-libelf-devel
BuildRequires:	openssl-devel openssl
BuildRequires:	pesign >= %{pesign_vre}
BuildRequires:	dos2unix findutils

# Shim uses OpenSSL, but cannot use the system copy as the UEFI ABI is not
# compatible with SysV (there's no red zone under UEFI) and there isn't a
# POSIX-style C library.
# BuildRequires:	OpenSSL
Provides:	bundled(openssl) = %{openssl_vre}
Obsoletes:	shim-%{efiarch}
Provides:	shim-%{efiarch}

%global desc \
Initial UEFI bootloader that handles chaining to a trusted full \
bootloader under secure boot environments.
%global debug_desc \
This package provides debug information for package %{expand:%%{name}} \
Debug information is useful when developing applications that \
use this package or when debugging this package.

%description
%desc

%package debuginfo
Summary:	Debug information for shim-%{efiarch}
Group:		Development/Debug
AutoReqProv:	0
BuildArch:	noarch
Obsoletes:	shim-%{efiarch}-debuginfo
Provides:	shim-%{efiarch}-debuginfo

%description debuginfo
%debug_desc

%package debugsource
Summary:	Debug Source for shim-unsigned
Group:		Development/Debug
AutoReqProv:	0
BuildArch:	noarch
Obsoletes:	shim-%{efiarch}-debugsource
Provides:	shim-%{efiarch}-debugsource

%description debugsource
%debug_desc

%prep

%autosetup -n shim-%{version}

# PATCHSETBEGIN
ExtractPatches()
{
	local patchtarball=$1

	if [ ! -f $patchtarball ]; then
		echo "ExtractPatches"
		exit 1
	fi
	tar xf $patchtarball
}
ExtractPatches %{SOURCE10}
for p in *.patch; do
	patch -p1 -F1 -s < $p
done
# PATCHSETEND

mkdir build-%{efiarch}
cp %{SOURCE3} data/

%build
MAKEFLAGS="TOPDIR=.. -f ../Makefile "
MAKEFLAGS+="EFIDIR=%{efidir} PKGNAME=shim RELEASE=%{release} "
MAKEFLAGS+="ENABLE_SHIM_HASH=true "
MAKEFLAGS+="%{_smp_mflags}"
if [ -f "%{SOURCE1}" ]; then
	MAKEFLAGS="$MAKEFLAGS VENDOR_CERT_FILE=%{SOURCE1}"
fi
%if 0%{?dbxfile}
if [ -f "%{SOURCE2}" ]; then
	MAKEFLAGS="$MAKEFLAGS VENDOR_DBX_FILE=%{SOURCE2}"
fi
%endif

cd build-%{efiarch}
make ${MAKEFLAGS} \
	DEFAULT_LOADER='\\\\grub%{efiarch}.efi' \
	all
cd ..

%install
MAKEFLAGS="TOPDIR=.. -f ../Makefile "
MAKEFLAGS+="EFIDIR=%{efidir} PKGNAME=shim RELEASE=%{release} "
MAKEFLAGS+="ENABLE_SHIM_HASH=true "
if [ -f "%{SOURCE1}" ]; then
	MAKEFLAGS="$MAKEFLAGS VENDOR_CERT_FILE=%{SOURCE1}"
fi
%if 0%{?dbxfile}
if [ -f "%{SOURCE2}" ]; then
	MAKEFLAGS="$MAKEFLAGS VENDOR_DBX_FILE=%{SOURCE2}"
fi
%endif

cd build-%{efiarch}
make ${MAKEFLAGS} \
	DEFAULT_LOADER='\\\\grub%{efiarch}.efi' \
	DESTDIR=${RPM_BUILD_ROOT} \
	install-as-data install-debuginfo install-debugsource

install -D -d -m 0700 $RPM_BUILD_ROOT/boot/efi/EFI/%{efidir}/
install -m 0700 shim%{efiarch}.efi $RPM_BUILD_ROOT/boot/efi/EFI/%{efidir}/shim%{efiarch}.efi
install -m 0700 mm%{efiarch}.efi $RPM_BUILD_ROOT/boot/efi/EFI/%{efidir}/mm%{efiarch}.efi
install -m 0700 BOOT%{efiarchlc}.CSV $RPM_BUILD_ROOT/boot/efi/EFI/%{efidir}/BOOT%{efiarchlc}.CSV

install -D -d -m 0700 $RPM_BUILD_ROOT/boot/efi/EFI/BOOT/
install -m 0700 shim%{efiarch}.efi $RPM_BUILD_ROOT/boot/efi/EFI/BOOT/BOOT%{efiarchlc}.EFI
install -m 0700 fb%{efiarch}.efi $RPM_BUILD_ROOT/boot/efi/EFI/BOOT/fb%{efiarch}.efi

chmod +x %{SOURCE100}
cd ..

%files
%license COPYRIGHT
%dir %{shimrootdir}
%dir %{shimversiondir}
%dir %{shimdir}
%{shimdir}/*.efi
%{shimdir}/*.hash
%{shimdir}/*.CSV
%defattr(0700,root,root,-)
%verify(not mtime) /boot/efi/EFI/%{efidir}/shim%{efiarch}.efi
%verify(not mtime) /boot/efi/EFI/%{efidir}/mm%{efiarch}.efi
%verify(not mtime) /boot/efi/EFI/BOOT/BOOT%{efiarchlc}.EFI
%verify(not mtime) /boot/efi/EFI/BOOT/fb%{efiarch}.efi
%verify(not mtime) /boot/efi/EFI/%{efidir}/BOOT%{efiarchlc}.CSV

%files debuginfo -f build-%{efiarch}/debugfiles.list

%files debugsource -f build-%{efiarch}/debugsource.list

%changelog
* Thu Apr 01 2021 Peter Jones <pjones@redhat.com> - 15.4-4
- Fix the sbat data to actually match /this/ product.
  Resolves: CVE-2020-14372
  Resolves: CVE-2020-25632
  Resolves: CVE-2020-25647
  Resolves: CVE-2020-27749
  Resolves: CVE-2020-27779
  Resolves: CVE-2021-20225
  Resolves: CVE-2021-20233

* Wed Mar 31 2021 Peter Jones <pjones@redhat.com> - 15.4-3
- Build with the correct certificate trust list for this OS.
  Resolves: CVE-2020-14372
  Resolves: CVE-2020-25632
  Resolves: CVE-2020-25647
  Resolves: CVE-2020-27749
  Resolves: CVE-2020-27779
  Resolves: CVE-2021-20225
  Resolves: CVE-2021-20233

* Wed Mar 31 2021 Peter Jones <pjones@redhat.com> - 15.4-2
- Fix the ia32 build.
  Resolves: CVE-2020-14372
  Resolves: CVE-2020-25632
  Resolves: CVE-2020-25647
  Resolves: CVE-2020-27749
  Resolves: CVE-2020-27779
  Resolves: CVE-2021-20225
  Resolves: CVE-2021-20233

* Tue Mar 30 2021 Peter Jones <pjones@redhat.com> - 15.4-1
- Update to shim 15.4
  - Support for revocations via the ".sbat" section and SBAT EFI variable
  - A new unit test framework and a bunch of unit tests
  - No external gnu-efi dependency
  - Better CI
  Resolves: CVE-2020-14372
  Resolves: CVE-2020-25632
  Resolves: CVE-2020-25647
  Resolves: CVE-2020-27749
  Resolves: CVE-2020-27779
  Resolves: CVE-2021-20225
  Resolves: CVE-2021-20233

* Wed Mar 24 2021 Peter Jones <pjones@redhat.com> - 15.3-0~1
- Update to shim 15.3
  - Support for revocations via the ".sbat" section and SBAT EFI variable
  - A new unit test framework and a bunch of unit tests
  - No external gnu-efi dependency
  - Better CI
  Resolves: CVE-2020-14372
  Resolves: CVE-2020-25632
  Resolves: CVE-2020-25647
  Resolves: CVE-2020-27749
  Resolves: CVE-2020-27779
  Resolves: CVE-2021-20225
  Resolves: CVE-2021-20233

* Wed Jun 05 2019 Javier Martinez Canillas <javierm@redhat.com> - 15-3
- Make EFI variable copying fatal only on secureboot enabled systems
  Resolves: rhbz#1715878
- Fix booting shim from an EFI shell using a relative path
  Resolves: rhbz#1717064

* Tue Feb 12 2019 Peter Jones <pjones@redhat.com> - 15-2
- Fix MoK mirroring issue which breaks kdump without intervention
  Related: rhbz#1668966

* Fri Jul 20 2018 Peter Jones <pjones@redhat.com> - 15-1
- Update to shim 15

* Tue Sep 19 2017 Peter Jones <pjones@redhat.com> - 13-3
- Actually update to the *real* 13 final.
  Related: rhbz#1489604

* Thu Aug 31 2017 Peter Jones <pjones@redhat.com> - 13-2
- Actually update to 13 final.

* Fri Aug 18 2017 Peter Jones <pjones@redhat.com> - 13-1
- Make a new shim-unsigned-x64 package like the shim-unsigned-aarch64 one.
- This will (eventually) supersede what's in the "shim" package so we can
  make "shim" hold the signed one, which will confuse fewer people.
