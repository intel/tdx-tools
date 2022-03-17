# # This file began as a copy of CentOS's grub2.spec, then modified.

%undefine _hardened_build

%global tarversion 2.02
%undefine _missing_build_ids_terminate_build
%global _configure_gnuconfig_hack 0

%define generic_name grub2
%define source_url_prefix https://git.centos.org/rpms/grub2/raw/6160bcdff98b660191b5c78ab698827e30c5362f/f/SOURCES

Name:		intel-mvp-tdx-guest-grub2
Epoch:		1
Version:	2.02
Release:	106.mvp5%{?dist}
Summary:	Bootloader with support for Linux, Multiboot and more
Group:		System Environment/Base
License:	GPLv3+
URL:		http://www.gnu.org/software/grub/
Obsoletes:	grub < 1:0.98
Source0:	grub-2.02.tar.gz
Source1:	grub.macros
Source4:	https://src.fedoraproject.org/repo/pkgs/grub2/unifont-5.1.20080820.pcf.gz/8c28087c5fcb3188f1244b390efffdbe/unifont-5.1.20080820.pcf.gz
Source6:	%{source_url_prefix}/gitignore
Source8:	%{source_url_prefix}/strtoull_test.c
Source9:	%{source_url_prefix}/20-grub.install
Source12:	%{source_url_prefix}/99-grub-mkconfig.install
Source13:	%{source_url_prefix}/centos-ca-secureboot.der
Source14:	%{source_url_prefix}/centossecureboot001.der
Source15:	%{source_url_prefix}/centossecurebootca2.der
Source16:	%{source_url_prefix}/centossecureboot202.der
Source19:	%{source_url_prefix}/sbat.csv.in

Source20:	patches-tdx-grub-2.02.tar.gz
	
Patch0007:	%{source_url_prefix}/0007-re-write-.gitignore.patch

%include %{SOURCE1}

%if 0%{with_efi_arch}
%define old_sb_ca	%{SOURCE13}
%define old_sb_cer	%{SOURCE14}
%define old_sb_key	centossecureboot001
%define sb_ca		%{SOURCE15}
%define sb_cer		%{SOURCE16}
%define sb_key		centossecureboot202
%endif

BuildRequires:	gcc efi-srpm-macros
BuildRequires:	flex bison binutils python3-devel
BuildRequires:	ncurses-devel xz-devel bzip2-devel
BuildRequires:	freetype-devel libusb-devel
BuildRequires:	rpm-devel
BuildRequires:	rpm-devel rpm-libs
BuildRequires:	autoconf automake autogen device-mapper-devel
BuildRequires:	freetype-devel gettext-devel git
BuildRequires:	texinfo
BuildRequires:	dejavu-sans-fonts
BuildRequires:	help2man
# For %%_userunitdir macro
BuildRequires:	systemd
%ifarch %{efi_arch}
BuildRequires:	pesign >= 0.99-8
%endif
%if %{?_with_ccache: 1}%{?!_with_ccache: 0}
BuildRequires:	ccache
%endif

ExcludeArch:	s390 s390x %{arm}
Obsoletes:	%{generic_name}

%if 0%{with_legacy_arch}
Requires:	%{name}-%{legacy_package_arch} = %{evr}
%else
Requires:	%{name}-%{package_arch} = %{evr}
%endif

%if 0%{?centos}
%global efidir centos
%endif

%global desc \
The GRand Unified Bootloader (GRUB) is a highly configurable and \
customizable bootloader with modular architecture.  It supports a rich \
variety of kernel formats, file systems, computer architectures and \
hardware devices.\
%{nil}

%description
%{desc}

%package common
Summary:	grub2 common layout
Group:		System Environment/Base
BuildArch:	noarch
Conflicts:	grubby < 8.40-13
Provides:	%{generic_name}-common
Obsoletes:	%{generic_name}-common

%description common
This package provides some directories which are required by various grub2
subpackages.

%package tools
Summary:	Support tools for GRUB.
Group:		System Environment/Base
Obsoletes:	%{generic_name}-tools
Provides:	%{generic_name}-tools
Requires:	%{name}-common = %{epoch}:%{version}-%{release}
Requires:	gettext os-prober which file
Requires(pre):	dracut
Requires(post):	dracut

%description tools
%{desc}
This subpackage provides tools for support of all platforms.

%ifarch x86_64
%package tools-efi
Summary:	Support tools for GRUB.
Group:		System Environment/Base
Requires:	gettext os-prober which file
Requires:	%{name}-common = %{epoch}:%{version}-%{release}
Obsoletes:	%{generic_name}-efi

%description tools-efi
%{desc}
This subpackage provides tools for support of EFI platforms.
%endif

%package tools-minimal
Summary:	Support tools for GRUB.
Group:		System Environment/Base
Requires:	gettext
Requires:	%{name}-common = %{epoch}:%{version}-%{release}
Obsoletes:	%{generic_name}-tools-minimal
Provides:	%{generic_name}-tools-minimal

%description tools-minimal
%{desc}
This subpackage provides tools for support of all platforms.

%package tools-extra
Summary:	Support tools for GRUB.
Group:		System Environment/Base
Requires:	gettext os-prober which file
Requires:	%{name}-tools-minimal = %{epoch}:%{version}-%{release}
Requires:	%{name}-common = %{epoch}:%{version}-%{release}
Obsoletes:	%{generic_name}-tools-extra
Provides:	%{generic_name}-tools-extra

%description tools-extra
%{desc}
This subpackage provides tools for support of all platforms.

%if 0%{with_efi_arch}
%{expand:%define_efi_variant %%{package_arch} -o}
%endif
%if 0%{with_alt_efi_arch}
%{expand:%define_efi_variant %%{alt_package_arch}}
%endif
%if 0%{with_legacy_arch}
%{expand:%define_legacy_variant %%{legacy_package_arch}}
%endif

%prep
%do_common_setup

#PATCHSETBEGIN
ExtractPatches()
{
    local patchtarball=$1

    if [ ! -f $patchtarball ]; then
        echo "ExtractPatches"
        exit 1
    fi
    tar vxf $patchtarball
}
ExtractPatches %{SOURCE20}
for p in *.patch; do
     echo "Applying TDX patch: "$p
     patch -p1 -F1 -s < $p
done
#PATCHSETEND

%if 0%{with_efi_arch}
mkdir grub-%{grubefiarch}-%{tarversion}
grep -A100000 '# stuff "make" creates' .gitignore > grub-%{grubefiarch}-%{tarversion}/.gitignore
cp %{SOURCE4} grub-%{grubefiarch}-%{tarversion}/unifont.pcf.gz
sed -e "s,@@VERSION@@,%{evr},g" %{SOURCE19} \
	> grub-%{grubefiarch}-%{tarversion}/sbat.csv
git add grub-%{grubefiarch}-%{tarversion}
%endif
%if 0%{with_alt_efi_arch}
mkdir grub-%{grubaltefiarch}-%{tarversion}
grep -A100000 '# stuff "make" creates' .gitignore > grub-%{grubaltefiarch}-%{tarversion}/.gitignore
cp %{SOURCE4} grub-%{grubaltefiarch}-%{tarversion}/unifont.pcf.gz
git add grub-%{grubaltefiarch}-%{tarversion}
%endif
%if 0%{with_legacy_arch}
mkdir grub-%{grublegacyarch}-%{tarversion}
grep -A100000 '# stuff "make" creates' .gitignore > grub-%{grublegacyarch}-%{tarversion}/.gitignore
cp %{SOURCE4} grub-%{grublegacyarch}-%{tarversion}/unifont.pcf.gz
git add grub-%{grublegacyarch}-%{tarversion}
%endif
git commit -m "After making subdirs"

%build
%if 0%{with_efi_arch}
%{expand:%do_primary_efi_build %%{grubefiarch} %%{grubefiname} %%{grubeficdname} %%{_target_platform} %%{efi_target_cflags} %%{efi_host_cflags} %{old_sb_ca} %{old_sb_cer} %{old_sb_key} %{sb_ca} %{sb_cer} %{sb_key}}
%endif
%if 0%{with_alt_efi_arch}
%{expand:%do_alt_efi_build %%{grubaltefiarch} %%{grubaltefiname} %%{grubalteficdname} %%{_alt_target_platform} %%{alt_efi_target_cflags} %%{alt_efi_host_cflags} %{old_sb_ca} %{old_sb_cer} %{old_sb_key} %{sb_ca} %{sb_cer} %{sb_key}}
%endif
%if 0%{with_legacy_arch}
%{expand:%do_legacy_build %%{grublegacyarch}}
%endif
makeinfo --info --no-split -I docs -o docs/grub-dev.info \
	docs/grub-dev.texi
makeinfo --info --no-split -I docs -o docs/grub.info \
	docs/grub.texi
makeinfo --html --no-split -I docs -o docs/grub-dev.html \
	docs/grub-dev.texi
makeinfo --html --no-split -I docs -o docs/grub.html \
	docs/grub.texi

%install
set -e
rm -fr $RPM_BUILD_ROOT

%do_common_install
%if 0%{with_efi_arch}
%{expand:%do_efi_install %%{grubefiarch} %%{grubefiname} %%{grubeficdname}}
%endif
%if 0%{with_alt_efi_arch}
%{expand:%do_alt_efi_install %%{grubaltefiarch} %%{grubaltefiname} %%{grubalteficdname}}
%endif
%if 0%{with_legacy_arch}
%{expand:%do_legacy_install %%{grublegacyarch} %%{alt_grub_target_name} 0%{with_efi_arch}}
%endif

rm -f $RPM_BUILD_ROOT%{_infodir}/dir
ln -s %{generic_name}-set-password ${RPM_BUILD_ROOT}/%{_sbindir}/%{generic_name}-setpassword
echo '.so man8/%{generic_name}-set-password.8' > ${RPM_BUILD_ROOT}/%{_datadir}/man/man8/%{generic_name}-setpassword.8
%ifnarch x86_64
rm -vf ${RPM_BUILD_ROOT}/%{_bindir}/%{generic_name}-render-label
rm -vf ${RPM_BUILD_ROOT}/%{_sbindir}/%{generic_name}-bios-setup
rm -vf ${RPM_BUILD_ROOT}/%{_sbindir}/%{generic_name}-macbless
%endif

# TODO: find_lang introduce build broken so remove it temporary
#%find_lang grub

# Make selinux happy with exec stack binaries.
mkdir ${RPM_BUILD_ROOT}%{_sysconfdir}/prelink.conf.d/
cat << EOF > ${RPM_BUILD_ROOT}%{_sysconfdir}/prelink.conf.d/grub2.conf
# these have execstack, and break under selinux
-b /usr/bin/grub2-script-check
-b /usr/bin/grub2-mkrelpath
-b /usr/bin/grub2-fstest
-b /usr/sbin/grub2-bios-setup
-b /usr/sbin/grub2-probe
-b /usr/sbin/grub2-sparc64-setup
EOF

# Install kernel-install scripts
install -d -m 0755 %{buildroot}%{_prefix}/lib/kernel/install.d/
install -D -m 0755 -t %{buildroot}%{_prefix}/lib/kernel/install.d/ %{SOURCE9}
install -D -m 0755 -t %{buildroot}%{_prefix}/lib/kernel/install.d/ %{SOURCE12}
install -d -m 0755 %{buildroot}%{_sysconfdir}/kernel/install.d/
install -m 0644 /dev/null %{buildroot}%{_sysconfdir}/kernel/install.d/20-grubby.install
install -m 0644 /dev/null %{buildroot}%{_sysconfdir}/kernel/install.d/90-loaderentry.install
# Install systemd user service to set the boot_success flag
install -D -m 0755 -t %{buildroot}%{_userunitdir} \
	docs/grub-boot-success.{timer,service}
install -d -m 0755 %{buildroot}%{_userunitdir}/timers.target.wants
ln -s ../grub-boot-success.timer \
	%{buildroot}%{_userunitdir}/timers.target.wants
# Install systemd system-update unit to set boot_indeterminate for offline-upd
install -D -m 0755 -t %{buildroot}%{_unitdir} docs/grub-boot-indeterminate.service
install -d -m 0755 %{buildroot}%{_unitdir}/system-update.target.wants
ln -s ../grub-boot-indeterminate.service \
	%{buildroot}%{_unitdir}/system-update.target.wants

# Don't run debuginfo on all the grub modules and whatnot; it just
# rejects them, complains, and slows down extraction.
%global finddebugroot "%{_builddir}/%{?buildsubdir}/debug"

%global dip RPM_BUILD_ROOT=%{finddebugroot} %{__debug_install_post}
%define __debug_install_post (						\
	mkdir -p %{finddebugroot}/usr					\
	mv ${RPM_BUILD_ROOT}/usr/bin %{finddebugroot}/usr/bin		\
	mv ${RPM_BUILD_ROOT}/usr/sbin %{finddebugroot}/usr/sbin		\
	%{dip}								\
	install -m 0755 -d %{buildroot}/usr/lib/ %{buildroot}/usr/src/	\
	cp -al %{finddebugroot}/usr/lib/debug/				\\\
		%{buildroot}/usr/lib/debug/				\
	cp -al %{finddebugroot}/usr/src/debug/				\\\
		%{buildroot}/usr/src/debug/ )				\
	mv %{finddebugroot}/usr/bin %{buildroot}/usr/bin		\
	mv %{finddebugroot}/usr/sbin %{buildroot}/usr/sbin		\
	%{nil}

%undefine buildsubdir

%pre tools
if [ -f /boot/grub2/user.cfg ]; then
    if grep -q '^GRUB_PASSWORD=' /boot/grub2/user.cfg ; then
	sed -i 's/^GRUB_PASSWORD=/GRUB2_PASSWORD=/' /boot/grub2/user.cfg
    fi
elif [ -f %{efi_esp_dir}/user.cfg ]; then
    if grep -q '^GRUB_PASSWORD=' %{efi_esp_dir}/user.cfg ; then
	sed -i 's/^GRUB_PASSWORD=/GRUB2_PASSWORD=/' \
	    %{efi_esp_dir}/user.cfg
    fi
elif [ -f /etc/grub.d/01_users ] && \
	grep -q '^password_pbkdf2 root' /etc/grub.d/01_users ; then
    if [ -f %{efi_esp_dir}/grub.cfg ]; then
	# on EFI we don't get permissions on the file, but
	# the directory is protected.
	grep '^password_pbkdf2 root' /etc/grub.d/01_users | \
		sed 's/^password_pbkdf2 root \(.*\)$/GRUB2_PASSWORD=\1/' \
	    > %{efi_esp_dir}/user.cfg
    fi
    if [ -f /boot/grub2/grub.cfg ]; then
	install -m 0600 /dev/null /boot/grub2/user.cfg
	chmod 0600 /boot/grub2/user.cfg
	grep '^password_pbkdf2 root' /etc/grub.d/01_users | \
		sed 's/^password_pbkdf2 root \(.*\)$/GRUB2_PASSWORD=\1/' \
	    > /boot/grub2/user.cfg
    fi
fi

%post tools
if [ "$1" = 1 ]; then
	/sbin/install-info --info-dir=%{_infodir} %{_infodir}/%{generic_name}.info.gz || :
	/sbin/install-info --info-dir=%{_infodir} %{_infodir}/%{generic_name}-dev.info.gz || :
fi

if [ "$1" = 2 ]; then
	/sbin/grub2-switch-to-blscfg --backup-suffix=.rpmsave &>/dev/null || :
fi

%triggerun -- grub2 < 1:1.99-4
# grub2 < 1.99-4 removed a number of essential files in postun. To fix upgrades
# from the affected grub2 packages, we first back up the files in triggerun and
# later restore them in triggerpostun.
# https://bugzilla.redhat.com/show_bug.cgi?id=735259

# Back up the files before uninstalling old grub2
mkdir -p /boot/grub2.tmp &&
mv -f /boot/grub2/*.mod \
      /boot/grub2/*.img \
      /boot/grub2/*.lst \
      /boot/grub2/device.map \
      /boot/grub2.tmp/ || :

%triggerpostun -- grub2 < 1:1.99-4
# ... and restore the files.
test ! -f /boot/grub2/device.map &&
test -d /boot/grub2.tmp &&
mv -f /boot/grub2.tmp/*.mod \
      /boot/grub2.tmp/*.img \
      /boot/grub2.tmp/*.lst \
      /boot/grub2.tmp/device.map \
      /boot/grub2/ &&
rm -r /boot/grub2.tmp/ || :

%preun tools
if [ "$1" = 0 ]; then
	/sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/%{generic_name}.info.gz || :
	/sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/%{generic_name}-dev.info.gz || :
fi

# TODO: find_lang introduce build broken so remove it temporary
#%files common -f grub.lang
%files common
%dir %{_libdir}/grub/
%dir %{_datarootdir}/grub/
%dir %{_datarootdir}/grub/themes/
%exclude %{_datarootdir}/grub/themes/*
%attr(0700,root,root) %dir %{_sysconfdir}/grub.d
%{_prefix}/lib/kernel/install.d/20-grub.install
%{_sysconfdir}/kernel/install.d/20-grubby.install
%{_sysconfdir}/kernel/install.d/90-loaderentry.install
%{_prefix}/lib/kernel/install.d/99-grub-mkconfig.install
%dir %{_datarootdir}/grub
%exclude %{_datarootdir}/grub/*
%dir /boot/%{generic_name}
%dir /boot/%{generic_name}/themes/
%dir /boot/%{generic_name}/themes/system
%exclude /boot/%{generic_name}/themes/system/*
%attr(0700,root,root) %dir /boot/grub2
%exclude /boot/grub2/*
%dir %attr(0700,root,root) %{efi_esp_dir}
%exclude %{efi_esp_dir}/*
%license COPYING
%ghost %config(noreplace) %verify(not size mode md5 mtime) /boot/grub2/grubenv
%doc INSTALL
%doc NEWS
%doc README
%doc THANKS
%doc TODO
%doc docs/grub.html
%doc docs/grub-dev.html
%doc docs/font_char_metrics.png

%files tools-minimal
%{_sysconfdir}/prelink.conf.d/grub2.conf
%{_sbindir}/%{generic_name}-get-kernel-settings
%attr(4755, root, root) %{_sbindir}/%{generic_name}-set-bootflag
%{_sbindir}/%{generic_name}-set-default
%{_sbindir}/%{generic_name}-set*password
%{_bindir}/%{generic_name}-editenv
%{_bindir}/%{generic_name}-mkpasswd-pbkdf2

%{_datadir}/man/man3/%{generic_name}-get-kernel-settings*
%{_datadir}/man/man8/%{generic_name}-set-default*
%{_datadir}/man/man8/%{generic_name}-set*password*
%{_datadir}/man/man1/%{generic_name}-editenv*
%{_datadir}/man/man1/%{generic_name}-mkpasswd-*

%ifarch x86_64
%files tools-efi
%{_sbindir}/%{generic_name}-macbless
%{_bindir}/%{generic_name}-render-label
%{_datadir}/man/man8/%{generic_name}-macbless*
%{_datadir}/man/man1/%{generic_name}-render-label*
%endif

%files tools
%attr(0644,root,root) %ghost %config(noreplace) %{_sysconfdir}/default/grub
%config %{_sysconfdir}/grub.d/??_*
%ifarch ppc64 ppc64le
%exclude %{_sysconfdir}/grub.d/10_linux
%else
%exclude %{_sysconfdir}/grub.d/10_linux_bls
%endif
%{_sysconfdir}/grub.d/README
%{_userunitdir}/grub-boot-success.timer
%{_userunitdir}/grub-boot-success.service
%{_userunitdir}/timers.target.wants
%{_unitdir}/grub-boot-indeterminate.service
%{_unitdir}/system-update.target.wants
%{_infodir}/%{generic_name}*
%{_datarootdir}/grub/*
%{_sbindir}/%{generic_name}-install
%exclude %{_datarootdir}/grub/themes
%exclude %{_datarootdir}/grub/*.h
%{_datarootdir}/bash-completion/completions/grub
%{_sbindir}/%{generic_name}-mkconfig
%{_sbindir}/%{generic_name}-switch-to-blscfg
%{_sbindir}/%{generic_name}-probe
%{_sbindir}/%{generic_name}-rpm-sort
%{_sbindir}/%{generic_name}-reboot
%{_bindir}/%{generic_name}-file
%{_bindir}/%{generic_name}-menulst2cfg
%{_bindir}/%{generic_name}-mkimage
%{_bindir}/%{generic_name}-mkrelpath
%{_bindir}/%{generic_name}-script-check
%{_datadir}/man/man?/*

# exclude man pages from tools-extra
%exclude %{_datadir}/man/man8/%{generic_name}-sparc64-setup*
%exclude %{_datadir}/man/man8/%{generic_name}-install*
%exclude %{_datadir}/man/man1/%{generic_name}-fstest*
%exclude %{_datadir}/man/man1/%{generic_name}-glue-efi*
%exclude %{_datadir}/man/man1/%{generic_name}-kbdcomp*
%exclude %{_datadir}/man/man1/%{generic_name}-mkfont*
%exclude %{_datadir}/man/man1/%{generic_name}-mklayout*
%exclude %{_datadir}/man/man1/%{generic_name}-mknetdir*
%exclude %{_datadir}/man/man1/%{generic_name}-mkrescue*
%exclude %{_datadir}/man/man1/%{generic_name}-mkstandalone*
%exclude %{_datadir}/man/man1/%{generic_name}-syslinux2cfg*

# exclude man pages from tools-minimal
%exclude %{_datadir}/man/man3/%{generic_name}-get-kernel-settings*
%exclude %{_datadir}/man/man8/%{generic_name}-set-default*
%exclude %{_datadir}/man/man8/%{generic_name}-set*password*
%exclude %{_datadir}/man/man1/%{generic_name}-editenv*
%exclude %{_datadir}/man/man1/%{generic_name}-mkpasswd-*
%exclude %{_datadir}/man/man8/%{generic_name}-macbless*
%exclude %{_datadir}/man/man1/%{generic_name}-render-label*

%if %{with_legacy_arch}
%{_sbindir}/%{generic_name}-install
%ifarch x86_64
%{_sbindir}/%{generic_name}-bios-setup
%else
%exclude %{_sbindir}/%{generic_name}-bios-setup
%exclude %{_datadir}/man/man8/%{generic_name}-bios-setup*
%endif
%ifarch %{sparc}
%{_sbindir}/%{generic_name}-sparc64-setup
%else
%exclude %{_sbindir}/%{generic_name}-sparc64-setup
%exclude %{_datadir}/man/man8/%{generic_name}-sparc64-setup*
%endif
%ifarch %{sparc} ppc ppc64 ppc64le
%{_sbindir}/%{generic_name}-ofpathname
%else
%exclude %{_sbindir}/%{generic_name}-ofpathname
%exclude %{_datadir}/man/man8/%{generic_name}-ofpathname*
%endif
%endif

%files tools-extra
%{_sbindir}/%{generic_name}-sparc64-setup
%{_sbindir}/%{generic_name}-ofpathname
%{_bindir}/%{generic_name}-fstest
%{_bindir}/%{generic_name}-glue-efi
%{_bindir}/%{generic_name}-kbdcomp
%{_bindir}/%{generic_name}-mkfont
%{_bindir}/%{generic_name}-mklayout
%{_bindir}/%{generic_name}-mknetdir
%ifnarch %{sparc}
%{_bindir}/%{generic_name}-mkrescue
%endif
%{_bindir}/%{generic_name}-mkstandalone
%{_bindir}/%{generic_name}-syslinux2cfg
%{_sysconfdir}/sysconfig/grub
%{_datadir}/man/man8/%{generic_name}-sparc64-setup*
%{_datadir}/man/man8/%{generic_name}-install*
%{_datadir}/man/man1/%{generic_name}-fstest*
%{_datadir}/man/man1/%{generic_name}-glue-efi*
%{_datadir}/man/man1/%{generic_name}-kbdcomp*
%{_datadir}/man/man1/%{generic_name}-mkfont*
%{_datadir}/man/man1/%{generic_name}-mklayout*
%{_datadir}/man/man1/%{generic_name}-mknetdir*
%{_datadir}/man/man1/%{generic_name}-mkrescue*
%{_datadir}/man/man1/%{generic_name}-mkstandalone*
%{_datadir}/man/man8/%{generic_name}-ofpathname*
%{_datadir}/man/man1/%{generic_name}-syslinux2cfg*
%exclude %{_datarootdir}/grub/themes/starfield

%if 0%{with_efi_arch}
%{expand:%define_efi_variant_files %%{package_arch} %%{grubefiname} %%{grubeficdname} %%{grubefiarch} %%{target_cpu_name} %%{grub_target_name}}
%endif
%if 0%{with_alt_efi_arch}
%{expand:%define_efi_variant_files %%{alt_package_arch} %%{grubaltefiname} %%{grubalteficdname} %%{grubaltefiarch} %%{alt_target_cpu_name} %%{alt_grub_target_name}}
%endif
%if 0%{with_legacy_arch}
%{expand:%define_legacy_variant_files %%{legacy_package_arch} %%{grublegacyarch}}
%endif

%changelog
* Thu Aug 19 2021 Javier Martinez Canillas <javierm@redhat.com> - 2.02-106
- Fix device discoverability on PowerVM when the prefix is not set (dja)
  Related: rhbz#1899864

* Thu Jul 22 2021 Javier Martinez Canillas <javierm@redhat.com> - 2.02-105
- Discover the device to read the config from as a fallback
  Related: rhbz#1899864

* Mon Jun 21 2021 Javier Martinez Canillas <javierm@redhat.com> - 2.02-104
- 20-grub-install: Create a symvers.gz symbolic link
  Resolves: rhbz#1919125

* Mon May 17 2021 Javier Martinez Canillas <javierm@redhat.com> - 2.02-103
- Fix boot failures in ppc64le caused by storage race condition (diegodo)
  Resolves: rhbz#1942152

* Tue May 11 2021 Javier Martinez Canillas <javierm@redhat.com> - 2.02-102
- Build and sign powerpc-ieee1275 images
  Related: rhbz#1899864

* Fri Apr 23 2021 Javier Martinez Canillas <javierm@redhat.com> - 2.02-101
- Find and claim more memory for ieee1275 (dja)
  Related: rhbz#1853410

* Fri Apr 23 2021 Javier Martinez Canillas <javierm@redhat.com> - 2.02-100
- Sync with the latest content of the rhel-8.4.0 branch
  Resolves: rhbz#1952840

* Thu Feb 25 2021 Javier Martinez Canillas <javierm@redhat.com> - 2.02-99
- Fix bug of grub2-install not checking for the SBAT option
  Resolves: CVE-2020-14372
  Resolves: CVE-2020-25632
  Resolves: CVE-2020-25647
  Resolves: CVE-2020-27749
  Resolves: CVE-2020-27779
  Resolves: CVE-2021-20225
  Resolves: CVE-2021-20233

* Thu Feb 25 2021 Javier Martinez Canillas <javierm@redhat.com> - 2.02-98
- Fix another batch of CVEs
  Resolves: CVE-2020-14372
  Resolves: CVE-2020-25632
  Resolves: CVE-2020-25647
  Resolves: CVE-2020-27749
  Resolves: CVE-2020-27779
  Resolves: CVE-2021-20225
  Resolves: CVE-2021-20233

* Tue Feb 23 2021 Javier Martinez Canillas <javierm@redhat.com> - 2.02-97
- Fix keylayouts module listed twice in GRUB_MODULES variable

* Tue Feb 23 2021 Javier Martinez Canillas <javierm@redhat.com> - 2.02-96
- Fix "Add 'at_keyboard_fallback_set' var to force the set manually"
- Fix a boot failure due patch "ieee1275: claim up to 256MB memory"

* Tue Jan 26 2021 Javier Martinez Canillas <javierm@redhat.com> - 2.02-95
- Add appended signatures support for ppc64le LPAR Secure Boot (daxtens)
  Resolves: rhbz#1853410

* Wed Jan 20 2021 Renaud Métrich <rmetrich@redhat.com> - 2.02-94
- Add 'at_keyboard_fallback_set' var to force the set manually
- Related: rhbz#1897587

* Mon Dec 14 2020 Javier Martinez Canillas <javierm@redhat.com> - 2.02-93
- add keylayouts and at_keyboard modules to UEFI Grub2 (rmetrich)
  Related: rhbz#1897587
- at_keyboard: use set 1 when keyboard is in Translate mode (rmetrich)
  Resolves: rhbz#1897587
- add GRUB enhanced debugging features (rmetrich)
  Resolves: rhbz#1776249
- ieee1275: Avoiding many unecessary open/close (diegodo)
  Resolves: rhbz#1862632
- ieee1275: device mapper and fibre channel discovery support (diegodo)
  Resolves: rhbz#1873724

* Mon Nov 23 2020 Jan Hlavac <jhlavac@redhat.com> - 2.02-92
- grub2-install: disable support for EFI platforms
  Resolves: rhbz#1737444
- Include a few more modules to EFI build needed for LUKS support (javierm)
  Related: rhbz#1873725

* Mon Nov 16 2020 Javier Martinez Canillas <javierm@redhat.com> - 2.02-91
- Fix tps-rpmtest failing due /boot/grub2/grubenv attributes mismatch
  Resolves: rhbz#1813959
- Include in EFI build the modules needed for LUKS support
  Resolves: rhbz#1873725
- Fix keyboards that report IBM PC AT scan codes
  Resolves: rhbz#1897587

* Mon Aug 31 2020 Javier Martinez Canillas <javierm@redhat.com> - 2.02-90
- Roll over TFTP block counter to prevent timeouts with data packets
  Resolves: rhbz#1871034

* Fri Aug 21 2020 Javier Martinez Canillas <javierm@redhat.com> - 2.02-89
- Fix TFTP timeouts when trying to fetch files larger than 65535 KiB
  Resolves: rhbz#1871034

* Tue Aug 11 2020 Javier Martinez Canillas <javierm@redhat.com> - 2.02-88
- Fix a legacy BIOS boot issue when a using config file shared with EFI
  Resolves: rhbz#1850193

* Mon Jul 27 2020 Peter Jones <pjones@redhat.com> - 2.02-87
- Couple more late fixes.
  Resolves: CVE-2020-15705

* Sun Jul 26 2020 Peter Jones <pjones@redhat.com> - 2.02-86
- Couple more late fixes.
  Resolves: CVE-2020-10713
  Resolves: CVE-2020-14308
  Resolves: CVE-2020-14309
  Resolves: CVE-2020-14310
  Resolves: CVE-2020-14311

* Mon Jul 20 2020 Peter Jones <pjones@redhat.com> - 2.02-85
- Fix several CVEs
  Resolves: CVE-2020-10713
  Resolves: CVE-2020-14308
  Resolves: CVE-2020-14309
  Resolves: CVE-2020-14310
  Resolves: CVE-2020-14311

* Tue May 19 2020 Javier Martinez Canillas <javierm@redhat.com> - 2.02-84
- Add fixes for greenboot support
  Resolves: rhbz#1832336

* Mon May 18 2020 Javier Martinez Canillas <javierm@redhat.com> - 2.02-83
- Fix a segfault in grub2-editenv when attempting to shrink a variable
  Resolves: rhbz#1761496

* Mon Apr 27 2020 Javier Martinez Canillas <javierm@redhat.com> - 2.02-82
- Drop "Disable multiboot, multiboot2, and linux16 modules on EFI builds"
  Resolves: rhbz#1779480
- efi/http: Export {fw,http}_path variables to make them global
  Resolves: rhbz#1811561
- efi/http: Enclose literal IPv6 addresses in square brackets
- efi/net: Allow to specify a port number in addresses
- efi/ip4_config: Improve check to detect literal IPv6 addresses
- efi/net: Print a debug message if parsing the address fails
  Resolves: rhbz#1811560
- Set image base address before jumping to the PE/COFF entry point
  Resolves: rhbz#1819624

* Thu Dec 05 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-81
- Another fix for blscfg variable expansion support
  Related: rhbz#1669252

* Thu Nov 28 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-80
- Fix PRIxGRUB_EFI_STATUS definition
  Related: rhbz#1761811
- TPM: Print messages if measuraments fail as debug instead of error
  Resolves: rhbz#1761811
- unix/platform: Initialize variable to fix grub-install on UEFI system
  Resolves: rhbz#1768689
- blscfg: add a space char when appending fields for variable expansion
  Resolves: rhbz#1669252

* Fri Nov 22 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-79
- grub-set-bootflag: Write new env to tmpfile and then rename (hdegoede)
  Resolves: CVE-2019-14865

* Thu Sep 26 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-77
- 10_linux_bls: don't add --users option to generated menu entries
  Resolves: rhbz#1755815

* Fri Aug 09 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-76
- Include regexp module in EFI builds
  Resolves: rhbz#1737670

* Wed Jun 19 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-75
- Fix setting default entry on ppc64le when using OPAL
  Resolves: rhbz#1721815

* Tue Jun 04 2019 Sergio Durigan Junior <sergiodj@redhat.com> - 2.02-74
- Use '-g' instead of '-g3' when compiling grub2.
  Related: rhbz#1653961

* Wed May 29 2019 Peter Jones <pjones@redhat.com> - 2.02-73
- Rebuild once again to try to get rpmdiff happy.
  Related: rhbz#1653961

* Mon May 27 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-72
- Build with the correct target
  Related: rhbz#1653961

* Fri May 24 2019 Peter Jones <pjones@redhat.com> - 2.02-71
- Fix (a fourth time, due to a typo) how LDFLAGS works on non-efi platforms.
  Related: rhbz#1653961

* Thu May 23 2019 Peter Jones <pjones@redhat.com> - 2.02-70
- Fix (once again) how CFLAGS and LDFLAGS propogate the settings for hardened
  builds, because rpmdiff doesn't like the current way failing.
  Related: rhbz#1653961

* Tue May 21 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-69
- Enable package gating
  Resolves: rhbz#1653961

* Mon May 20 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-68
- Avoid grub2-efi package to overwrite existing /boot/grub2/grubenv file
  Resolves: rhbz#1680572
- Try to set -fPIE and friends on libgnu.a (pjones)
- blscfg: fallback to default_kernelopts if BLS option field isn't set
  Related: rhbz#1680572
- Remove bogus load_env after blscfg command in 10_linux

* Mon Apr 29 2019 Javier Martinez Canillas <javierm@redhat.com> - 2.02-67
- Fix failure to request grub.cfg over HTTP
  Resolves: rhbz#1490991

* Wed Dec 19 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-66
- Fix grub.cfg-XXX look up when booting over TFTP
  Resolves: rhbz#1658500

* Mon Dec 17 2018 Peter Jones <pjones@redhat.com> - 2.02-65
- Don't build the grub2-efi-ia32-* packages on i686; it causes multilib
  errors and we don't ship the result anyway.
  Related: rhbz#1637875

* Tue Dec 11 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-64
- Make grub2-mkconfig to honour GRUB_CMDLINE_LINUX in /etc/default/grub
  Resolves: rhbz#1637875
- docs: Stop using polkit / pkexec for grub-boot-success.timer / service
  Resolves: rhbz#1655687

* Tue Dec 04 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-63
- BLS files should only be copied by grub-switch-to-blscfg if BLS isn't set
  Related: rhbz#1638117
- Fix get_entry_number() wrongly dereferencing the tail pointer
  Resolves: rhbz#1654936

* Fri Nov 30 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-62
- Drop "Be more aggro about actually using the *configured* network device."
  Resolves: rhbz#1654388
- Fix menu entry selection based on title
  Resolves: rhbz#1654936

* Tue Nov 27 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-61
- Drop buggy downstream patch "efinet: retransmit if our device is busy"
  Resolves: rhbz#1649048
- Make the menu entry users option argument to be optional
  Related: rhbz#1652434
- 10_linux_bls: add missing menu entries options
  Resolves: rhbz#1652434

* Wed Nov 21 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-60
- Remove quotes when reading ID value from /etc/os-release
  Related: rhbz#1650706
- blscfg: expand grub_users before passing to grub_normal_add_menu_entry()
  Resolves: rhbz#1650706

* Thu Nov 08 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-59
- Remove installkernel-bls script
  Related: rhbz#1647721

* Wed Oct 24 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-58
- Don't unconditionally set default entry when installing debug kernels
  Resolves: rhbz#1636346

* Fri Oct 19 2018 Peter Jones <pjones@redhat.com> - 2.02-57
- Fix menu entry selection based on ID and title
  Resolves: rhbz#1640979

* Fri Oct 19 2018 Javier Martinez Canillas <javierm@redhat.com>
- don't set saved_entry on grub2-mkconfig
  Resolves: rhbz#1636466

* Tue Oct 16 2018 Peter Jones <pjones@redhat.com> - 2.02-56
- Rebuild for signing
  Resolves: rhbz#1625565
- blscfg: Make 10_linux_bls sort the same way as well
  Related: rhbz#1638103

* Mon Oct 15 2018 Peter Jones <pjones@redhat.com> - 2.02-55
- blscfg: sort everything with rpm *package* comparison
  Related: rhbz#1638103

* Thu Oct 11 2018 Peter Jones <pjones@redhat.com> - 2.02-54
- kernel-install: Remove existing initramfs if it's older than the kernel
  Resolves: rhbz#1638405
- Update the saved entry correctly after a kernel install
  Resolves: rhbz#1638117

* Fri Oct 05 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-53
- Only set kernelopts in grubenv if it wasn't set before
  Resolves: rhbz#1636466

* Thu Oct 04 2018 Peter Jones <pjones@redhat.com> - 2.02-52
- Remove 01_fallback_counting entirely until we can sort its issues out.
  Resolves: rhbz#1615954

* Thu Oct 04 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-51
- add 10_linux_bls grub.d snippet to generate menu entries from BLS files
  Resolves: rhbz#1636013
- Fix syntax issues in 01_fallback_counting.in
  Resolves: rhbz#1615954

* Mon Oct 01 2018 pjones <pjones@redhat.com> - 1:2.02-50
- Disable TPM (again) on BIOS; it really does not work reliably.
  Resolves: rhbz#1579835
- Make blscfg module loadable on other grub2 builds
  Resolves: rhbz#1633646
- Include blscfg module on ppc builds
  Related: rhbz#1633646
- Fix rpmdiff complaints about execstack
  Related: rhbz#1633646

* Mon Sep 24 2018 Peter Jones <pjones@redhat.com> - 2.02-49
- Add an installkernel script for BLS configurations
  Related: rhbz#1619344

* Fri Sep 14 2018 Peter Jones <pjones@redhat.com> - 2.02-48
- Go back to forcing all allocations on x86_64 to be 32-bit, as many UEFI
  implementations seem to have drivers with DMA issues for addresses
  above 4GB.
  Resolves: rhbz#1628346

* Wed Sep 12 2018 Peter Jones <pjones@redhat.com> - 2.02-47
- BLS fixes from the F29 tree
  - Use /boot/loader/entries as BLS dir also on EFI systems
  - Make 20-grub.install to exit if there is no machine ID set
  - More fixes for BLS
  Resolves: rhbz#1620954

* Mon Aug 27 2018 Peter Jones <pjones@redhat.com> - 2.02-46
- Better memory allocation for kernel/initramfs on aarch64
  Resolves: rhbz#1620954

* Tue Aug 14 2018 Peter Jones <pjones@redhat.com> - 2.02-45
- Fix a typo in /etc/grub.d/01_fallback_counting
  Resolves: rhbz#1615954

* Thu Aug 09 2018 Peter Jones <pjones@redhat.com> - 2.02-44
- Rebased to newer upstream for fedora-29

* Thu Aug 09 2018 pjones <pjones@redhat.com> - 1:2.02-43
- Rebased to newer upstream for fedora-29

* Tue Jul 17 2018 Peter Jones <pjones@redhat.com> - 2.02-42
- Fix some minor BLS issues
- Rework the FDT module linking to make aarch64 build and boot right
  Resolves: rhbz#1601835

* Mon Jul 16 2018 pjones <pjones@redhat.com> - 2.02-41
- Pull in newer sb patches that do a better job with config file writing

* Mon Jul 16 2018 Hans de Goede <hdegoede@redhat.com>
- Make the user session automatically set the boot_success grubenv flag
- Make offline-updates increment the boot_indeterminate grubenv variable

* Fri Jul 13 2018 Peter Jones <pjones@redhat.com> - 2.02-40
- Revert broken moduledir fix in this tree as well.

* Tue Jul 10 2018 pjones <pjones@redhat.com> - 2.02-39
- Fix our linuxefi/linux command reunion.

* Tue Jul 10 2018 pjones <pjones@redhat.com> - 2.02-38
- Rebased to newer upstream for RHEL-8

* Wed May 16 2018 Peter Jones <pjones@redhat.com> - 2.02-37
- Fixups to work with gcc 8
- Experimental https boot support on UEFI
- XFS fixes for sparse inode support
  Resolves: rhbz#1575797

* Thu May 10 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-36
- Use version field to sort BLS entries if id field isn't defined
- Add version field to BLS fragments generated by 20-grub.install

* Tue Apr 24 2018 Peter Jones <pjones@redhat.com> - 2.02-35
- A couple of fixes needed by Fedora Atomic - javierm

* Mon Apr 23 2018 Peter Jones <pjones@redhat.com> - 2.02-34
- Put the os-prober dep back in - we need to change test plans and criteria
  before it can go.
  Resolves: rhbz#1569411

* Wed Apr 11 2018 Peter Jones <pjones@redhat.com> - 2.02-33
- Work around some issues with older automake found in CentOS.
- Make multiple initramfs images work in BLS.

* Wed Apr 11 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-32
- Make 20-grub.install to generate debug BLS when MAKEDEBUG is set.

* Fri Apr 06 2018 Peter Jones <pjones@redhat.com> - 2.02-31
- Pull in some TPM fixes I missed.

* Fri Apr 06 2018 Peter Jones <pjones@redhat.com> - 2.02-30
- Enable TPM measurements
- Set the default boot entry to the first entry when we're using BLS.

* Tue Apr 03 2018 Peter Jones <pjones@redhat.com> - 2.02-29
- Add grub2-switch-to-blscfg
- Fix for BLS paths on BIOS / non-UEFI (javierm)

* Fri Mar 09 2018 Javier Martinez Canillas <javierm@redhat.com> - 2.02-28
- Install kernel-install scripts.

* Tue Mar 06 2018 Peter Jones <pjones@redhat.com> - 2.02-27
- Build the blscfg module in on EFI builds.

* Wed Feb 28 2018 Peter Jones <pjones@redhat.com> - 2.02-26
- Try to fix things for new compiler madness.
  I really don't know why gcc decided __attribute__((packed)) on a "typedef
  struct" should imply __attribute__((align (1))) and that it should have a
  warning that it does so.  The obvious behavior would be to keep the alignment
  of the first element unless it's used in another object or type that /also/
  hask the packed attribute.  Why should it change the default alignment at
  all?
- Merge in the BLS patches Javier and I wrote.
- Attempt to fix pmtimer initialization failures to not be super duper slow.

* Fri Feb 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org>
- Escape macros in %%changelog

* Tue Jan 23 2018 Peter Jones <pjones@redhat.com> - 2.02-24
- Fix a merge error from 2.02-21 that affected kernel loading on Aarch64.
  Related: rhbz#1519311
  Related: rhbz#1506704
  Related: rhbz#1502312

* Fri Jan 19 2018 Peter Jones <pjones@redhat.com> - 2.02-23
- Only nerf annobin, not -fstack-crash-protection.
- Fix a conflict on /boot/efi directory permissions between -cdboot and the
  normal bootloader.

* Thu Jan 18 2018 Peter Jones <pjones@redhat.com> - 2.02-22
- Nerf some gcc 7.2.1-6 'features' that cause grub to crash on start.

* Thu Jan 18 2018 Peter Jones <pjones@redhat.com> - 2.02-21
- Fix grub2-efi-modules provides/obsoletes generation
  Resolves: rhbz#1506704
- *Also* build grub-efi-ia32{,-*,!-modules} packages for i686 builds
  Resolves: rhbz#1502312
- Make everything under /boot/efi be mode 0700, since that's what FAT will
  show anyway.

* Wed Jan 17 2018 Peter Jones <pjones@redhat.com> - 2.02-20
- Update to newer upstream for F28
- Pull in patches for Apollo Lake hardware
  Resolves: rhbz#1519311

* Tue Oct 24 2017 Peter Jones <pjones@redhat.com> - 2.02-19
- Handle xen module loading (somewhat) better
  Resolves: rhbz#1486002

* Wed Sep 20 2017 Peter Jones <pjones@redhat.com> - 2.02-18
- Make grub2-efi-aa64 provide grub2
  Resolves: rhbz#1491045

* Mon Sep 11 2017 Dennis Gilmore <dennis@ausil.us> - 2.02-17
- bump for Obsoletes again

* Wed Sep 06 2017 Peter Jones <pjones@redhat.com> - 2.02-16
- Fix Obsoletes on grub2-pc

* Wed Aug 30 2017 Petr Šabata <contyk@redhat.com> - 2.02-15
- Limit the pattern matching in do_alt_efi_install to files to
  unbreak module builds

* Fri Aug 25 2017 Peter Jones <pjones@redhat.com> - 2.02-14
- Revert the /usr/lib/.build-id/ change:
  https://fedoraproject.org/wiki/Changes/ParallelInstallableDebuginfo
  says (without any particularly convincing reasoning):
    The main build-id file should not be in the debuginfo file, but in the
    main package (this was always a problem since the package and debuginfo
    package installed might not match). If we want to make usr/lib/debug/ a
    network resource then we will need to move the symlink to another
    location (maybe /usr/lib/.build-id).
  So do it that way.  Of course it doesn't matter, because exclude gets
  ignored due to implementation details.

* Fri Aug 25 2017 Peter Jones <pjones@redhat.com> - 2.02-13
- Add some unconditional Provides:
  grub2-efi on grub2-efi-${arch}
  grub2-efi-cdboot on grub2-efi-${arch}-cdboot
  grub2 on all grub2-${arch} pacakges
- Something is somehow adding /usr/lib/.build-id/... to all the -tools
  subpackages, so exclude all that.

* Thu Aug 24 2017 Peter Jones <pjones@redhat.com> - 2.02-12
- Fix arm kernel command line allocation
  Resolves: rhbz#1484609
- Get rid of the temporary extra efi packages hack.

* Wed Aug 23 2017 Peter Jones <pjones@redhat.com> - 2.02-11
- Put grub2-mkimage in -tools, not -tools-extra.
- Fix i686 building
- Fix ppc HFS+ usage due to /boot/efi's presence.

* Fri Aug 18 2017 Peter Jones <pjones@redhat.com> - 2.02-10
- Add the .img files into grub2-pc-modules (and all legacy variants)

* Wed Aug 16 2017 Peter Jones <pjones@redhat.com> - 2.02-9
- Re-work for ia32-efi.

* Wed Aug 16 2017 pjones <pjones@redhat.com> - 2.02-8
- Rebased to newer upstream for fedora-27

* Tue Aug 15 2017 Peter Jones <pjones@redhat.com> - 2.02-7
- Rebuild again with new fixed rpm. (bug #1480407)

* Fri Aug 11 2017 Kevin Fenzi <kevin@scrye.com> - 2.02-6
- Rebuild again with new fixed rpm. (bug #1480407)

* Thu Aug 10 2017 Kevin Fenzi <kevin@scrye.com> - 2.02-5
- Rebuild for rpm soname bump again.

* Thu Aug 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 2.02-4
- Rebuilt for RPM soname bump

* Thu Aug 03 2017 Peter Jones <pjones@redhat.com> - 2.02-3
- Rebuild so it gets SB signed correctly.
  Related: rhbz#1335533
- Enable lsefi

* Mon Jul 24 2017 Michael Cronenworth <mike@cchtml.com> - 2.02-2
- Fix symlink to work on both EFI and BIOS machines
  Resolves: rhbz#1335533

* Mon Jul 10 2017 Peter Jones <pjones@redhat.com> - 2.02-1
- Rebased to newer upstream for fedora-27

* Wed Feb 01 2017 Stephen Gallagher <sgallagh@redhat.com> - 2.02-0.39
- Add missing %%license macro
- Fix deps that should have moved to -tools but didn't.

* Thu Dec 08 2016 Peter Jones <pjones@redhat.com> - 2.02-0.38
- Fix regexp in power compile flags, and synchronize release number with
  other branches.

* Fri Dec 02 2016 pjones <pjones@redhat.com> - 1:2.02-0.37
- Rebased to newer upstream for fedora-26

* Thu Dec 01 2016 Peter Jones <pjones@redhat.com> - 2.02-0.36
- Update version to .36 because I already built an f25 one named 0.35

* Thu Dec 01 2016 pjones <pjones@redhat.com> - 1:2.02-0.35
- Rebased to newer upstream for fedora-26

* Thu Dec 01 2016 Peter Jones <pjones@redhat.com> - 2.02-0.34
- Fix power6 makefile bits for newer autoconf defaults.
- efi/chainloader: fix wrong sanity check in relocate_coff() (Laszlo Ersek)
  Resolves: rhbz#1347291

* Thu Aug 25 2016 Peter Jones <pjones@redhat.com> - 2.02-0.34
- Update to be newer than f24's branch.
- Add grub2-get-kernel-settings
  Related: rhbz#1226325

* Thu Apr 07 2016 pjones <pjones@redhat.com> - 1:2.02-0.30
- Revert 27e66193, which was replaced by upstream's 49426e9fd
  Resolves: rhbz#1251600

* Thu Apr 07 2016 Peter Jones <pjones@redhat.com> - 2.02-0.29
- Fix ppc64 build failure and rebase to newer f24 code.

* Tue Apr 05 2016 pjones <pjones@redhat.com> - 1:2.02-0.27
- Pull TPM updates from mjg59.
  Resolves: rhbz#1318067

* Tue Mar 08 2016 pjones <pjones@redhat.com> - 1:2.02-0.27
- Fix aarch64 build problem.

* Fri Mar 04 2016 Peter Jones <pjones@redhat.com> - 2.02-0.26
- Rebased to newer upstream (grub-2.02-beta3) for fedora-24

* Thu Dec 10 2015 Peter Jones <pjones@redhat.com> - 2.02-0.25
- Fix security issue when reading username and password
  Related: CVE-2015-8370
- Do a better job of handling GRUB2_PASSWORD
  Related: rhbz#1284370

* Fri Nov 20 2015 Peter Jones <pjones@redhat.com> - 2.02-0.24
- Rebuild without multiboot* modules in the EFI image.
  Related: rhbz#1264103

* Sat Sep 05 2015 Kalev Lember <klember@redhat.com> - 2.02-0.23
- Rebuilt for librpm soname bump

* Wed Aug 05 2015 Peter Jones <pjones@redhat.com> - 2.02-0.21
- Back out one of the debuginfo generation patches; it doesn't work right on
  aarch64 yet.
  Resolves: rhbz#1250197

* Mon Aug 03 2015 Peter Jones <pjones@redhat.com> - 2.02-0.20
- The previous fix was completely not right, so fix it a different way.
  Resolves: rhbz#1249668

* Fri Jul 31 2015 Peter Jones <pjones@redhat.com> - 2.02-0.19
- Fix grub2-mkconfig's sort to put kernels in the right order.
  Related: rhbz#1124074

* Thu Jul 30 2015 Peter Jones <pjones@redhat.com> - 2.02-0.18
- Fix a build failure on aarch64

* Wed Jul 22 2015 Peter Jones <pjones@redhat.com> - 2.02-0.17
- Don't build hardened (fixes FTBFS) (pbrobinson)
- Reconcile with the current upstream
- Fixes for gcc 5

* Tue Apr 28 2015 Peter Jones <pjones@redhat.com> - 2.02-0.16
- Make grub2-mkconfig produce the kernel titles we actually want.
  Resolves: rhbz#1215839

* Sat Feb 21 2015 Till Maas <opensource@till.name>
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Mon Jan 05 2015 Peter Jones <pjones@redhat.com> - 2.02-0.15
- Bump release to rebuild with Ralf Corsépius's fixes.

* Sun Jan 04 2015 Ralf Corsépius <corsepiu@fedoraproject.org> - 2.02-0.14
- Move grub2.info/grub2-dev.info install-info scriptlets into *-tools package.
- Use sub-shell in %%__debug_install_post (RHBZ#1168732).
- Cleanup grub2-starfield-theme packaging.

* Thu Dec 04 2014 Peter Jones <pjones@redhat.com> - 2.02-0.13
- Update minilzo to 2.08 for CVE-2014-4607
  Resolves: rhbz#1131793

* Thu Nov 13 2014 Peter Jones <pjones@redhat.com> - 2.02-0.12
- Make backtrace and usb conditional on !arm
- Make sure gcdaa64.efi is packaged.
  Resolves: rhbz#1163481

* Fri Nov 07 2014 Peter Jones <pjones@redhat.com> - 2.02-0.11
- fix a copy-paste error in patch 0154.
  Resolves: rhbz#964828

* Mon Oct 27 2014 Peter Jones <pjones@redhat.com> - 2.02-0.10
- Try to emit linux16/initrd16 and linuxefi/initrdefi when appropriate
  in 30_os-prober.
  Resolves: rhbz#1108296
- If $fw_path doesn't work to find the config file, try $prefix as well
  Resolves: rhbz#1148652

* Mon Sep 29 2014 Peter Jones <pjones@redhat.com> - 2.02-0.9
- Clean up the build a bit to make it faster
- Make grubenv work right on UEFI machines
  Related: rhbz#1119943
- Sort debug and rescue kernels later than normal ones
  Related: rhbz#1065360
- Allow "fallback" to include entries by title as well as number.
  Related: rhbz#1026084
- Fix a segfault on aarch64.
- Load arm with SB enabled if available.
- Add some serial port options to GRUB_MODULES.

* Tue Aug 19 2014 Peter Jones <pjones@redhat.com> - 2.02-0.8
- Add ppc64le support.
  Resolves: rhbz#1125540

* Thu Jul 24 2014 Peter Jones <pjones@redhat.com> - 2.02-0.7
- Enabled syslinuxcfg module.

* Wed Jul 02 2014 Peter Jones <pjones@redhat.com> - 2.02-0.6
- Re-merge RHEL 7 changes and ARM works in progress.

* Mon Jun 30 2014 Peter Jones <pjones@redhat.com> - 2.02-0.5
- Avoid munging raw spaces when we're escaping command line arguments.
  Resolves: rhbz#923374

* Tue Jun 24 2014 Peter Jones <pjones@redhat.com> - 2.02-0.4
- Update to latest upstream.

* Thu Mar 13 2014 Peter Jones <pjones@redhat.com> - 2.02-0.3
- Merge in RHEL 7 changes and ARM works in progress.

* Mon Jan 06 2014 Peter Jones <pjones@redhat.com> - 2.02-0.2
- Update to grub-2.02~beta2

* Sat Aug 10 2013 Peter Jones <pjones@redhat.com> - 2.00-25
- Last build failed because of a hardware error on the builder.

* Mon Aug 05 2013 Peter Jones <pjones@redhat.com> - 2.00-24
- Fix compiler flags to deal with -fstack-protector-strong

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2.00-24
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 02 2013 Dennis Gilmore <dennis@ausil.us> - 2.00-23
- add epoch to obsoletes

* Fri Jun 21 2013 Peter Jones <pjones@redhat.com> - 2.00-22
- Fix linewrapping in edit menu.
  Resolves: rhbz #976643

* Thu Jun 20 2013 Peter Jones <pjones@redhat.com> - 2.00-21
- Fix obsoletes to pull in -starfield-theme subpackage when it should.

* Fri Jun 14 2013 Peter Jones <pjones@redhat.com> - 2.00-20
- Put the theme entirely ento the subpackage where it belongs (#974667)

* Wed Jun 12 2013 Peter Jones <pjones@redhat.com> - 2.00-19
- Rebase to upstream snapshot.
- Fix PPC build error (#967862)
- Fix crash on net_bootp command (#960624)
- Reset colors on ppc when appropriate (#908519)
- Left align "Loading..." messages (#908492)
- Fix probing of SAS disks on PPC (#953954)
- Add support for UEFI OSes returned by os-prober
- Disable "video" mode on PPC for now (#973205)
- Make grub fit better into the boot sequence, visually (#966719)

* Fri May 10 2013 Matthias Clasen <mclasen@redhat.com> - 2.00-18
- Move the starfield theme to a subpackage (#962004)
- Don't allow SSE or MMX on UEFI builds (#949761)

* Wed Apr 24 2013 Peter Jones <pjones@redhat.com> - 2.00-17.pj0
- Rebase to upstream snapshot.

* Thu Apr 04 2013 Peter Jones <pjones@redhat.com> - 2.00-17
- Fix booting from drives with 4k sectors on UEFI.
- Move bash completion to new location (#922997)
- Include lvm support for /boot (#906203)

* Thu Feb 14 2013 Peter Jones <pjones@redhat.com> - 2.00-16
- Allow the user to disable submenu generation
- (partially) support BLS-style configuration stanzas.

* Tue Feb 12 2013 Peter Jones <pjones@redhat.com> - 2.00-15.pj0
- Add various config file related changes.

* Thu Dec 20 2012 Dennis Gilmore <dennis@ausil.us> - 2.00-15
- bump nvr

* Mon Dec 17 2012 Karsten Hopp <karsten@redhat.com> 2.00-14
- add bootpath device to the device list (pfsmorigo, #886685)

* Tue Nov 27 2012 Peter Jones <pjones@redhat.com> - 2.00-13
- Add vlan tag support (pfsmorigo, #871563)
- Follow symlinks during PReP installation in grub2-install (pfsmorigo, #874234)
- Improve search paths for config files on network boot (pfsmorigo, #873406)

* Tue Oct 23 2012 Peter Jones <pjones@redhat.com> - 2.00-12
- Don't load modules when grub transitions to "normal" mode on UEFI.

* Mon Oct 22 2012 Peter Jones <pjones@redhat.com> - 2.00-11
- Rebuild with newer pesign so we'll get signed with the final signing keys.

* Thu Oct 18 2012 Peter Jones <pjones@redhat.com> - 2.00-10
- Various PPC fixes.
- Fix crash fetching from http (gustavold, #860834)
- Issue separate dns queries for ipv4 and ipv6 (gustavold, #860829)
- Support IBM CAS reboot (pfsmorigo, #859223)
- Include all modules in the core image on ppc (pfsmorigo, #866559)

* Mon Oct 01 2012 Peter Jones <pjones@redhat.com> - 1:2.00-9
- Work around bug with using "\x20" in linux command line.
  Related: rhbz#855849

* Thu Sep 20 2012 Peter Jones <pjones@redhat.com> - 2.00-8
- Don't error on insmod on UEFI/SB, but also don't do any insmodding.
- Increase device path size for ieee1275
  Resolves: rhbz#857936
- Make network booting work on ieee1275 machines.
  Resolves: rhbz#857936

* Wed Sep 05 2012 Matthew Garrett <mjg@redhat.com> - 2.00-7
- Add Apple partition map support for EFI

* Thu Aug 23 2012 David Cantrell <dcantrell@redhat.com> - 2.00-6
- Only require pesign on EFI architectures (#851215)

* Tue Aug 14 2012 Peter Jones <pjones@redhat.com> - 2.00-5
- Work around AHCI firmware bug in efidisk driver.
- Move to newer pesign macros
- Don't allow insmod if we're in secure-boot mode.

* Wed Aug 08 2012 Peter Jones <pjones@redhat.com>
- Split module lists for UEFI boot vs UEFI cd images.
- Add raid modules for UEFI image (related: #750794)
- Include a prelink whitelist for binaries that need execstack (#839813)
- Include fix efi memory map fix from upstream (#839363)

* Wed Aug 08 2012 Peter Jones <pjones@redhat.com> - 2.00-4
- Correct grub-mkimage invocation to use efidir RPM macro (jwb)
- Sign with test keys on UEFI systems.
- PPC - Handle device paths with commas correctly.
  Related: rhbz#828740

* Wed Jul 25 2012 Peter Jones <pjones@redhat.com> - 2.00-3
- Add some more code to support Secure Boot, and temporarily disable
  some other bits that don't work well enough yet.
  Resolves: rhbz#836695

* Wed Jul 11 2012 Matthew Garrett <mjg@redhat.com> - 2.00-2
- Set a prefix for the image - needed for installer work
- Provide the font in the EFI directory for the same reason

* Thu Jun 28 2012 Peter Jones <pjones@redhat.com> - 2.00-1
- Rebase to grub-2.00 release.

* Mon Jun 18 2012 Peter Jones <pjones@redhat.com> - 2.0-0.37.beta6
- Fix double-free in grub-probe.

* Wed Jun 06 2012 Peter Jones <pjones@redhat.com> - 2.0-0.36.beta6
- Build with patch19 applied.

* Wed Jun 06 2012 Peter Jones <pjones@redhat.com> - 2.0-0.35.beta6
- More ppc fixes.

* Wed Jun 06 2012 Peter Jones <pjones@redhat.com> - 2.0-0.34.beta6
- Add IBM PPC fixes.

* Mon Jun 04 2012 Peter Jones <pjones@redhat.com> - 2.0-0.33.beta6
- Update to beta6.
- Various fixes from mads.

* Fri May 25 2012 Peter Jones <pjones@redhat.com> - 2.0-0.32.beta5
- Revert builddep change for crt1.o; it breaks ppc build.

* Fri May 25 2012 Peter Jones <pjones@redhat.com> - 2.0-0.31.beta5
- Add fwsetup command (pjones)
- More ppc fixes (IBM)

* Tue May 22 2012 Peter Jones <pjones@redhat.com> - 2.0-0.30.beta5
- Fix the /other/ grub2-tools require to include epoch.

* Mon May 21 2012 Peter Jones <pjones@redhat.com> - 2.0-0.29.beta5
- Get rid of efi_uga and efi_gop, favoring all_video instead.

* Mon May 21 2012 Peter Jones <pjones@redhat.com> - 2.0-0.28.beta5
- Name grub.efi something that's arch-appropriate (kiilerix, pjones)
- use EFI/$SOMETHING_DISTRO_BASED/ not always EFI/redhat/grub2-efi/ .
- move common stuff to -tools (kiilerix)
- spec file cleanups (kiilerix)

* Mon May 14 2012 Peter Jones <pjones@redhat.com> - 2.0-0.27.beta5
- Fix module trampolining on ppc (benh)

* Thu May 10 2012 Peter Jones <pjones@redhat.com> - 2.0-0.27.beta5
- Fix license of theme (mizmo)
  Resolves: rhbz#820713
- Fix some PPC bootloader detection IBM problem
  Resolves: rhbz#820722

* Thu May 10 2012 Peter Jones <pjones@redhat.com> - 2.0-0.26.beta5
- Update to beta5.
- Update how efi building works (kiilerix)
- Fix theme support to bring in fonts correctly (kiilerix, pjones)

* Wed May 09 2012 Peter Jones <pjones@redhat.com> - 2.0-0.25.beta4
- Include theme support (mizmo)
- Include locale support (kiilerix)
- Include html docs (kiilerix)

* Thu Apr 26 2012 Peter Jones <pjones@redhat.com> - 2.0-0.24
- Various fixes from Mads Kiilerich

* Thu Apr 19 2012 Peter Jones <pjones@redhat.com> - 2.0-0.23
- Update to 2.00~beta4
- Make fonts work so we can do graphics reasonably

* Thu Mar 29 2012 David Aquilina <dwa@redhat.com> - 2.0-0.22
- Fix ieee1275 platform define for ppc

* Thu Mar 29 2012 Peter Jones <pjones@redhat.com> - 2.0-0.21
- Remove ppc excludearch lines (dwa)
- Update ppc terminfo patch (hamzy)

* Wed Mar 28 2012 Peter Jones <pjones@redhat.com> - 2.0-0.20
- Fix ppc64 vs ppc exclude according to what dwa tells me they need
- Fix version number to better match policy.

* Tue Mar 27 2012 Dan Horák <dan[at]danny.cz> - 1.99-19.2
- Add support for serial terminal consoles on PPC by Mark Hamzy

* Sun Mar 25 2012 Dan Horák <dan[at]danny.cz> - 1.99-19.1
- Use Fix-tests-of-zeroed-partition patch by Mark Hamzy

* Thu Mar 15 2012 Peter Jones <pjones@redhat.com> - 1.99-19
- Use --with-grubdir= on configure to make it behave like -17 did.

* Wed Mar 14 2012 Peter Jones <pjones@redhat.com> - 1.99-18
- Rebase from 1.99 to 2.00~beta2

* Wed Mar 07 2012 Peter Jones <pjones@redhat.com> - 1.99-17
- Update for newer autotools and gcc 4.7.0
  Related: rhbz#782144
- Add /etc/sysconfig/grub link to /etc/default/grub
  Resolves: rhbz#800152
- ExcludeArch s390*, which is not supported by this package.
  Resolves: rhbz#758333

* Fri Feb 17 2012 Orion Poplawski <orion@cora.nwra.com> - 1:1.99-16
- Build with -Os (bug 782144)

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.99-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Dec 14 2011 Matthew Garrett <mjg@redhat.com> - 1.99-14
- fix up various grub2-efi issues

* Thu Dec 08 2011 Adam Williamson <awilliam@redhat.com> - 1.99-13
- fix hardwired call to grub-probe in 30_os-prober (rhbz#737203)

* Mon Nov 07 2011 Peter Jones <pjones@redhat.com> - 1.99-12
- Lots of .spec fixes from Mads Kiilerich:
  Remove comment about update-grub - it isn't run in any scriptlets
  patch info pages so they can be installed and removed correctly when renamed
  fix references to grub/grub2 renames in info pages (#743964)
  update README.Fedora (#734090)
  fix comments for the hack for upgrading from grub2 < 1.99-4
  fix sed syntax error preventing use of $RPM_OPT_FLAGS (#704820)
  make /etc/grub2*.cfg %%config(noreplace)
  make grub.cfg %%ghost - an empty file is of no use anyway
  create /etc/default/grub more like anaconda would create it (#678453)
  don't create rescue entries by default - grubby will not maintain them anyway
  set GRUB_SAVEDEFAULT=true so saved defaults works (rbhz#732058)
  grub2-efi should have its own bash completion
  don't set gfxpayload in efi mode - backport upstream r3402
- Handle dmraid better. Resolves: rhbz#742226

* Wed Oct 26 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.99-11
- Rebuilt for glibc bug#747377

* Wed Oct 19 2011 Adam Williamson <awilliam@redhat.com> - 1.99-10
- /etc/default/grub is explicitly intended for user customization, so
  mark it as config(noreplace)

* Tue Oct 11 2011 Peter Jones <pjones@redhat.com> - 1.99-9
- grub has an epoch, so we need that expressed in the obsolete as well.
  Today isn't my day.

* Tue Oct 11 2011 Peter Jones <pjones@redhat.com> - 1.99-8
- Fix my bad obsoletes syntax.

* Thu Oct 06 2011 Peter Jones <pjones@redhat.com> - 1.99-7
- Obsolete grub
  Resolves: rhbz#743381

* Wed Sep 14 2011 Peter Jones <pjones@redhat.com> - 1.99-6
- Use mv not cp to try to avoid moving disk blocks around for -5 fix
  Related: rhbz#735259
- handle initramfs on xen better (patch from Marko Ristola)
  Resolves: rhbz#728775

* Sat Sep 03 2011 Kalev Lember <kalevlember@gmail.com> - 1.99-5
- Fix upgrades from grub2 < 1.99-4 (#735259)

* Fri Sep 02 2011 Peter Jones <pjones@redhat.com> - 1.99-4
- Don't do sysadminny things in %%preun or %%post ever. (#735259)
- Actually include the changelog in this build (sorry about -3)

* Thu Sep 01 2011 Peter Jones <pjones@redhat.com> - 1.99-2
- Require os-prober (#678456) (patch from Elad Alfassa)
- Require which (#734959) (patch from Elad Alfassa)

* Thu Sep 01 2011 Peter Jones <pjones@redhat.com> - 1.99-1
- Update to grub-1.99 final.
- Fix crt1.o require on x86-64 (fix from Mads Kiilerich)
- Various CFLAGS fixes (from Mads Kiilerich)
  - -fexceptions and -m64
- Temporarily ignore translations (from Mads Kiilerich)

* Thu Jul 21 2011 Peter Jones <pjones@redhat.com> - 1.99-0.3
- Use /sbin not /usr/sbin .

* Thu Jun 23 2011 Peter Lemenkov <lemenkov@gmail.com> - 1:1.99-0.2
- Fixes for ppc and ppc64

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.98-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild
