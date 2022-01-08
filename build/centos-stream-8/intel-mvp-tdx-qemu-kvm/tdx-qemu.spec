%global SLOF_gittagdate 20170724
%global SLOF_gittagcommit 89f519f

%global have_usbredir 1
%global have_spice    1
%global have_opengl   1
%global have_fdt      0
%global have_gluster  1
%global have_kvm_setup 0
%global have_memlock_limits 0

%ifnarch %{ix86} x86_64
    %global have_usbredir 0
%endif

%ifnarch s390x
    %global have_librdma 1
%else
    %global have_librdma 0
%endif

%ifarch %{ix86}
    %global kvm_target    i386
%endif
%ifarch x86_64
    %global kvm_target    x86_64
%else
    %global have_spice   0
    %global have_opengl  0
    %global have_gluster 0
%endif
%ifarch %{power64}
    %global kvm_target    ppc64
    %global have_fdt     1
    %global have_kvm_setup 1
    %global have_memlock_limits 1
%endif
%ifarch s390x
    %global kvm_target    s390x
    %global have_kvm_setup 1
%endif
%ifarch ppc
    %global kvm_target    ppc
    %global have_fdt     1
%endif
%ifarch aarch64
    %global kvm_target    aarch64
    %global have_fdt     1
%endif

#Versions of various parts:

%global requires_all_modules                                     \
Requires: %{name}-block-curl = %{epoch}:%{version}-%{release}    \
%if %{have_gluster}                                              \
Requires: %{name}-block-gluster = %{epoch}:%{version}-%{release} \
%endif                                                           \
Requires: %{name}-block-iscsi = %{epoch}:%{version}-%{release}   \
Requires: %{name}-block-rbd = %{epoch}:%{version}-%{release}     \
Requires: %{name}-block-ssh = %{epoch}:%{version}-%{release}

# Macro to properly setup RHEL/RHEV conflict handling
%define rhev_ma_conflicts()                                      \
Obsoletes: %1-ma                                                 \
Obsoletes: %1-rhev

Summary: QEMU is a machine emulator and virtualizer
Name: intel-mvp-tdx-qemu-kvm
Version: 6.0.0
%define rcver 1
%define source_tag 2021.11.29
%define patch_number mvp20
Release: %{source_tag}.%{patch_number}%{?dist}

Provides: qemu-kvm
Obsoletes: qemu-kvm

# Epoch because we pushed a qemu-1.0 package. AIUI this can't ever be dropped
Epoch: 15
License: GPLv2 and GPLv2+ and CC-BY
Group: Development/Tools
URL: http://www.qemu.org/
ExclusiveArch: x86_64 %{power64} aarch64 s390x
%define source_url_prefix https://git.centos.org/rpms/qemu-kvm/raw/1072c8b30f152643d36a85e4980db1370e002c68/f/SOURCES

Source0: https://download.qemu.org/qemu-6.0.0-rc1.tar.bz2
%if %{rcver}
Source1: patches-tdx-qemu-%{version}-rc%{rcver}-%{source_tag}.tar.gz
%else
Source1: patches-tdx-qemu-%{version}-%{source_tag}.tar.gz
%endif

# KSM control scripts
Source4: %{source_url_prefix}/ksm.service
Source5: %{source_url_prefix}/ksm.sysconfig
Source6: %{source_url_prefix}/ksmctl.c
Source7: %{source_url_prefix}/ksmtuned.service
Source8: %{source_url_prefix}/ksmtuned
Source9: %{source_url_prefix}/ksmtuned.conf
Source10: %{source_url_prefix}/qemu-guest-agent.service
Source11: %{source_url_prefix}/99-qemu-guest-agent.rules
Source12: %{source_url_prefix}/bridge.conf
Source13: %{source_url_prefix}/qemu-ga.sysconfig
Source21: %{source_url_prefix}/kvm-setup
Source22: %{source_url_prefix}/kvm-setup.service
Source23: %{source_url_prefix}/85-kvm.preset
Source26: %{source_url_prefix}/vhost.conf
Source27: %{source_url_prefix}/kvm.conf
Source28: %{source_url_prefix}/95-kvm-memlock.conf
Source30: %{source_url_prefix}/kvm-s390x.conf
Source31: %{source_url_prefix}/kvm-x86.conf
Source32: %{source_url_prefix}/qemu-pr-helper.service
Source33: %{source_url_prefix}/qemu-pr-helper.socket
Source34: %{source_url_prefix}/81-kvm-rhel.rules
Source35: %{source_url_prefix}/udev-kvm-check.c
Source36: %{source_url_prefix}/README.tests

BuildRequires: zlib-devel
BuildRequires: glib2-devel
BuildRequires: which
BuildRequires: gnutls-devel
BuildRequires: cyrus-sasl-devel
BuildRequires: libtool
BuildRequires: libaio-devel
BuildRequires: rsync
BuildRequires: python3-devel
BuildRequires: pciutils-devel
BuildRequires: libiscsi-devel
BuildRequires: ncurses-devel
BuildRequires: libattr-devel
BuildRequires: libcap-ng-devel
BuildRequires: libusbx-devel >= 1.0.22
%if %{have_usbredir}
BuildRequires: usbredir-devel >= 0.7.1
%endif
BuildRequires: texinfo
%if %{have_spice}
BuildRequires: spice-protocol >= 0.12.12
BuildRequires: spice-server-devel >= 0.12.8
BuildRequires: libcacard-devel
# For smartcard NSS support
BuildRequires: nss-devel
%endif
BuildRequires: libseccomp-devel >= 2.4.0
# For network block driver
BuildRequires: libcurl-devel
BuildRequires: libssh-devel
BuildRequires: librados-devel
BuildRequires: librbd-devel
%if %{have_gluster}
# For gluster block driver
BuildRequires: glusterfs-api-devel >= 3.6.0
BuildRequires: glusterfs-devel
%endif
# We need both because the 'stap' binary is probed for by configure
BuildRequires: systemtap
BuildRequires: systemtap-sdt-devel
# For VNC PNG support
BuildRequires: libpng-devel
# For uuid generation
BuildRequires: libuuid-devel
# For BlueZ device support
BuildRequires: bluez-libs-devel
# For Braille device support
BuildRequires: brlapi-devel
# For test suite
BuildRequires: check-devel
# For virtfs
BuildRequires: libcap-devel
# Hard requirement for version >= 1.3
BuildRequires: pixman-devel
BuildRequires: ninja-build
BuildRequires: meson
# Documentation requirement
BuildRequires: perl-podlators
BuildRequires: texinfo
BuildRequires: python3-sphinx
# For rdma
%if 0%{?have_librdma}
BuildRequires: rdma-core-devel
%endif
%if %{have_fdt}
BuildRequires: libfdt-devel >= 1.4.3
%endif
# iasl and cpp for acpi generation (not a hard requirement as we can use
# pre-compiled files, but it's better to use this)
%ifarch %{ix86} x86_64
BuildRequires: iasl
BuildRequires: cpp
%endif
# For compressed guest memory dumps
BuildRequires: lzo-devel snappy-devel
# For NUMA memory binding
%ifnarch s390x
BuildRequires: numactl-devel
%endif
BuildRequires: libgcrypt-devel
# qemu-pr-helper multipath support (requires libudev too)
BuildRequires: device-mapper-multipath-devel
BuildRequires: systemd-devel
# used by qemu-bridge-helper and qemu-pr-helper
BuildRequires: libcap-ng-devel

BuildRequires: diffutils
%ifarch x86_64
BuildRequires: libpmem-devel
Requires: libpmem
%endif

# qemu-keymap
BuildRequires: pkgconfig(xkbcommon)

# For s390-pgste flag
%ifarch s390x
BuildRequires: binutils >= 2.27-16
%endif

%if %{have_opengl}
BuildRequires: pkgconfig(epoxy)
BuildRequires: pkgconfig(libdrm)
BuildRequires: pkgconfig(gbm)
Requires:      mesa-libGL
Requires:      mesa-libEGL
Requires:      mesa-dri-drivers
%endif

Requires: intel-mvp-tdx-qemu-kvm-core = %{epoch}:%{version}-%{release}
%rhev_ma_conflicts qemu-kvm

%{requires_all_modules}

%define qemudocdir %{_docdir}/qemu-kvm

%description
qemu-kvm is an open source virtualizer that provides hardware
emulation for the KVM hypervisor. qemu-kvm acts as a virtual
machine monitor together with the KVM kernel modules, and emulates the
hardware for a full system such as a PC and its associated peripherals.


%package -n intel-mvp-tdx-qemu-kvm-core
Summary: qemu-kvm core components

Obsoletes: qemu-kvm-core
Provides: qemu-kvm-core

Requires: intel-mvp-tdx-qemu-img = %{epoch}:%{version}-%{release}
%ifarch %{ix86} x86_64
Requires: seabios-bin >= 1.10.2-1
Requires: sgabios-bin
Requires: edk2-ovmf
%endif
%ifarch aarch64
Requires: edk2-aarch64
%endif

%ifnarch aarch64 s390x
Requires: seavgabios-bin >= 1.10.2-1
Requires: ipxe-roms-qemu >= 20170123-1
%endif
%ifarch %{power64}
Requires: SLOF >= %{SLOF_gittagdate}-1.git%{SLOF_gittagcommit}
%endif
Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: libseccomp >= 2.4.0
# For compressed guest memory dumps
Requires: lzo snappy
%if %{have_gluster}
Requires: glusterfs-api >= 3.6.0
%endif
%if %{have_kvm_setup}
Requires(post): systemd-units
Requires(preun): systemd-units
    %ifarch %{power64}
Requires: powerpc-utils
    %endif
%endif
Requires: libusbx >= 1.0.19
%if %{have_usbredir}
Requires: usbredir >= 0.7.1
%endif

%rhev_ma_conflicts qemu-kvm

%description -n intel-mvp-tdx-qemu-kvm-core
qemu-kvm is an open source virtualizer that provides hardware
emulation for the KVM hypervisor. qemu-kvm acts as a virtual
machine monitor together with the KVM kernel modules, and emulates the
hardware for a full system such as a PC and its associated peripherals.


%package -n intel-mvp-tdx-qemu-img
Summary: QEMU command line tool for manipulating disk images
Group: Development/Tools

Obsoletes: qemu-img
Provides: qemu-img

%rhev_ma_conflicts qemu-img

%description -n intel-mvp-tdx-qemu-img
This package provides a command line tool for manipulating disk images.

%package -n intel-mvp-tdx-qemu-kvm-common
Summary: QEMU common files needed by all QEMU targets
Group: Development/Tools

Obsoletes: qemu-kvm-common
Provides: qemu-kvm-common

Requires(post): /usr/bin/getent
Requires(post): /usr/sbin/groupadd
Requires(post): /usr/sbin/useradd
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%rhev_ma_conflicts qemu-kvm-common

%description -n intel-mvp-tdx-qemu-kvm-common
qemu-kvm is an open source virtualizer that provides hardware emulation for
the KVM hypervisor.

This package provides documentation and auxiliary programs used with qemu-kvm.


%package -n intel-mvp-tdx-qemu-guest-agent
Summary: QEMU guest agent

Obsoletes: qemu-guest-agent
Provides: qemu-guest-agent

Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description -n intel-mvp-tdx-qemu-guest-agent
qemu-kvm is an open source virtualizer that provides hardware emulation for
the KVM hypervisor.

This package provides an agent to run inside guests, which communicates
with the host over a virtio-serial channel named "org.qemu.guest_agent.0"

This package does not need to be installed on the host OS.

%package tests
Summary: tests for the qemu-kvm package

Obsoletes: qemu-kvm-tests
Provides: qemu-kvm-tests

Requires: %{name} = %{epoch}:%{version}-%{release}

%define testsdir %{_libdir}/qemu-kvm/tests-src

%description tests
The qemu-kvm-tests rpm contains tests that can be used to verify
the functionality of the installed qemu-kvm package

Install this package if you want access to the avocado_qemu
tests, or qemu-iotests.

%package  block-curl
Summary: QEMU CURL block driver

Obsoletes: qemu-kvm-block-curl
Provides: qemu-kvm-block-curl

Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}

%description block-curl
This package provides the additional CURL block driver for QEMU.

Install this package if you want to access remote disks over
http, https, ftp and other transports provided by the CURL library.


%if %{have_gluster}
%package  block-gluster
Summary: QEMU Gluster block driver

Obsoletes: qemu-kvm-block-gluster
Provides: qemu-kvm-block-gluster

Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}
%description block-gluster
This package provides the additional Gluster block driver for QEMU.

Install this package if you want to access remote Gluster storage.
%endif


%package  block-iscsi
Summary: QEMU iSCSI block driver

Obsoletes: qemu-kvm-block-iscsi
Provides: qemu-kvm-block-iscsi

Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}

%description block-iscsi
This package provides the additional iSCSI block driver for QEMU.

Install this package if you want to access iSCSI volumes.


%package  block-rbd
Summary: QEMU Ceph/RBD block driver

Obsoletes: qemu-kvm-block-rbd
Provides: qemu-kvm-block-rbd

Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}

%description block-rbd
This package provides the additional Ceph/RBD block driver for QEMU.

Install this package if you want to access remote Ceph volumes
using the rbd protocol.


%package  block-ssh
Summary: QEMU SSH block driver

Obsoletes: qemu-kvm-block-ssh
Provides: qemu-kvm-block-ssh

Requires: %{name}-common%{?_isa} = %{epoch}:%{version}-%{release}

%description block-ssh
This package provides the additional SSH block driver for QEMU.

Install this package if you want to access remote disks using
the Secure Shell (SSH) protocol.

%package spice
Summary: QEMU spice application

Obsoletes: qemu-kvm-spice
Provides: qemu-kvm-spice

%description spice
This package provide an additional spice application library

%package hw-display
Summary: Provides hw-display libraries.

%description hw-display
Provides hw-display libraries.

%package hw-usb
Summary: Provides hw-usb libraries.

%description hw-usb
Provides hw-usb libraries.

%package ui
Summary: Provides ui libraries.

%description ui
Provides ui libraries.


%prep
ExtractPatches()
{
    local patchtarball=$1

    if [ ! -f $patchtarball ]; then
        echo "ExtractPatches"
        exit 1
    fi
    tar xf $patchtarball
}
ExtractPatches %{SOURCE1}

%setup -q -n qemu-6.0.0-rc1

%autopatch -p1
for p in ../patches/*.patch; do
     patch -p1 -F1 -s < $p
done

%build
%global buildarch %{kvm_target}-softmmu

# --build-id option is used for giving info to the debug packages.
buildldflags="VL_LDFLAGS=-Wl,--build-id"

%global block_drivers_list qcow2,raw,file,host_device,nbd,iscsi,rbd,blkdebug,luks,null-co,nvme,copy-on-read,throttle

%if 0%{have_gluster}
    %global block_drivers_list %{block_drivers_list},gluster
%endif

mkdir build
cd build

../configure  \
 --prefix="%{_prefix}" \
 --libdir="%{_libdir}" \
 --sysconfdir="%{_sysconfdir}" \
 --interp-prefix=%{_prefix}/qemu-%M \
 --localstatedir="%{_localstatedir}" \
 --libexecdir="%{_libexecdir}" \
 --extra-ldflags="-Wl,--build-id -Wl,-z,relro -Wl,-z,now -Wl,-z,ibt -Wl,-z,shstk -Wl,-z,cet-report=error" \
 --extra-cflags="%{optflags} -Wno-error=maybe-uninitialized -fcf-protection=full" \
 --with-pkgversion="%{name}-%{version}-%{release}" \
 --with-suffix="qemu-kvm" \
 --firmwarepath=%{_prefix}/share/qemu-firmware \
%if 0%{have_fdt}
  --enable-fdt \
%else
  --disable-fdt \
 %endif
%if 0%{have_gluster}
  --enable-glusterfs \
%else
  --disable-glusterfs \
%endif
  --enable-guest-agent \
%ifnarch s390x
  --enable-numa \
%else
  --disable-numa \
%endif
  --enable-rbd \
%if 0%{have_librdma}
  --enable-rdma \
%else
  --disable-rdma \
%endif
  --enable-seccomp \
%if 0%{have_spice}
  --enable-spice \
  --enable-smartcard \
%else
  --disable-spice \
  --disable-smartcard \
%endif
%if 0%{have_opengl}
  --enable-opengl \
%else
  --disable-opengl \
%endif
%if 0%{have_usbredir}
  --enable-usb-redir \
%else
  --disable-usb-redir \
%endif
  --disable-tcmalloc \
%ifarch x86_64
  --enable-libpmem \
%else
  --disable-libpmem \
%endif
  --enable-vhost-user \
  --python=%{__python3} \
  --target-list="%{buildarch}" \
  --block-drv-rw-whitelist=%{block_drivers_list} \
  --audio-drv-list= \
  --block-drv-ro-whitelist=vmdk,vhdx,vpc,https,ssh \
  --with-coroutine=ucontext \
  --tls-priority=NORMAL \
  --disable-brlapi \
  --enable-cap-ng \
  --enable-coroutine-pool \
  --enable-curl \
  --disable-curses \
  --disable-debug-tcg \
  --enable-docs \
  --disable-gtk \
  --enable-kvm \
  --enable-libiscsi \
  --disable-libnfs \
  --enable-libssh \
  --enable-libusb \
  --disable-bzip2 \
  --enable-linux-aio \
  --disable-live-block-migration \
  --enable-lzo \
  --enable-pie \
  --disable-qom-cast-debug \
  --disable-sdl \
  --enable-snappy \
  --disable-sparse \
  --disable-strip \
  --enable-tpm \
  --enable-trace-backend=dtrace \
  --disable-vde \
  --disable-vhost-scsi \
  --enable-virtfs \
  --disable-vnc-jpeg \
  --disable-vte \
  --enable-vnc-png \
  --enable-vnc-sasl \
  --enable-werror \
  --disable-xen \
  --disable-xfsctl \
  --enable-gnutls \
  --enable-gcrypt \
  --disable-nettle \
  --enable-attr \
  --disable-bsd-user \
  --disable-cocoa \
  --enable-debug-info \
  --disable-guest-agent-msi \
  --disable-hax \
  --disable-jemalloc \
  --disable-linux-user \
  --enable-modules \
  --disable-netmap \
  --disable-replication \
  --enable-system \
  --enable-tools \
  --disable-user \
  --enable-vhost-net \
  --enable-vhost-vsock \
  --enable-vnc \
  --enable-mpath \
  --disable-virglrenderer \
  --disable-xen-pci-passthrough \
  --enable-tcg \
  --with-git=git \
  --disable-sanitizers \
  --disable-hvf \
  --disable-whpx \
  --enable-malloc-trim \
  --disable-membarrier \
  --disable-vhost-crypto \
  --disable-libxml2 \
  --enable-capstone \
  --with-git-submodules=ignore \
  --disable-crypto-afalg \
  --disable-bochs \
  --disable-cloop \
  --disable-dmg \
  --disable-qcow1 \
  --disable-vdi \
  --disable-vvfat \
  --disable-qed \
  --disable-parallels \
  --disable-sheepdog


echo "config-host.mak contents:"
echo "==="
cat config-host.mak
echo "==="

make V=1 %{?_smp_mflags} $buildldflags
make V=1 %{?_smp_mflags} $buildldflags qemu-ga

# Setup back compat qemu-kvm binary
%{__python3} scripts/tracetool.py --backends=dtrace --format=stap --group=all \
  --binary %{_libexecdir}/qemu-kvm --target-name %{kvm_target} \
  --target-type system --probe-prefix qemu.kvm trace/trace-events-all qemu-kvm.stp

%{__python3} scripts/tracetool.py --backends=dtrace --format=simpletrace-stap \
  --group=all --binary %{_libexecdir}/qemu-kvm --target-name %{kvm_target} \
  --target-type system --probe-prefix qemu.kvm trace/trace-events-all qemu-kvm-simpletrace.stp

gcc %{SOURCE6} $RPM_OPT_FLAGS $RPM_LD_FLAGS -o ksmctl
gcc %{SOURCE35} $RPM_OPT_FLAGS $RPM_LD_FLAGS -o udev-kvm-check

%install
%define _udevdir %(pkg-config --variable=udevdir udev)
%define _udevrulesdir %{_udevdir}/rules.d

cd build

install -D -p -m 0644 %{SOURCE4} $RPM_BUILD_ROOT%{_unitdir}/ksm.service
install -D -p -m 0644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/ksm
install -D -p -m 0755 ksmctl $RPM_BUILD_ROOT%{_libexecdir}/ksmctl

install -D -p -m 0644 %{SOURCE7} $RPM_BUILD_ROOT%{_unitdir}/ksmtuned.service
install -D -p -m 0755 %{SOURCE8} $RPM_BUILD_ROOT%{_sbindir}/ksmtuned
install -D -p -m 0644 %{SOURCE9} $RPM_BUILD_ROOT%{_sysconfdir}/ksmtuned.conf
install -D -p -m 0644 %{SOURCE26} $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/vhost.conf
%ifarch s390x
    install -D -p -m 0644 %{SOURCE30} $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/kvm.conf
%else
%ifarch %{ix86} x86_64
    install -D -p -m 0644 %{SOURCE31} $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/kvm.conf
%else
    install -D -p -m 0644 %{SOURCE27} $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/kvm.conf
%endif
%endif

mkdir -p $RPM_BUILD_ROOT%{_bindir}/
mkdir -p $RPM_BUILD_ROOT%{_udevrulesdir}/
mkdir -p $RPM_BUILD_ROOT%{_datadir}/qemu-kvm

# Create new directories and put them all under tests-src
mkdir -p $RPM_BUILD_ROOT%{testsdir}/tests/
mkdir -p $RPM_BUILD_ROOT%{testsdir}/tests/acceptance
mkdir -p $RPM_BUILD_ROOT%{testsdir}/tests/qemu-iotests
mkdir -p $RPM_BUILD_ROOT%{testsdir}/scripts
mkdir -p $RPM_BUILD_ROOT%{testsdir}/scripts/qmp

install -p -m 0755 udev-kvm-check $RPM_BUILD_ROOT%{_udevdir}
install -p -m 0644 %{SOURCE34} $RPM_BUILD_ROOT%{_udevrulesdir}

install -m 0644 scripts/dump-guest-memory.py \
                $RPM_BUILD_ROOT%{_datadir}/qemu-kvm

# Install avocado_qemu tests
cp -R tests/acceptance/* $RPM_BUILD_ROOT%{testsdir}/tests/acceptance/

# Install qemu.py and qmp/ scripts required to run avocado_qemu tests
#install -p -m 0644 scripts/qemu.py $RPM_BUILD_ROOT%{testsdir}/scripts/
cp -R scripts/qmp/* $RPM_BUILD_ROOT%{testsdir}/scripts/qmp
install -p -m 0755 ../tests/Makefile.include $RPM_BUILD_ROOT%{testsdir}/tests/

# Install qemu-iotests
cp -R ../tests/qemu-iotests/* $RPM_BUILD_ROOT%{testsdir}/tests/qemu-iotests/
# Avoid ambiguous 'python' interpreter name
find $RPM_BUILD_ROOT%{testsdir}/tests/qemu-iotests/* -maxdepth 1 -type f -exec sed -i -e '1 s+/usr/bin/env python+%{__python3}+' {} \;
find $RPM_BUILD_ROOT%{testsdir}/scripts/qmp/* -maxdepth 1 -type f -exec sed -i -e '1 s+/usr/bin/env python+%{__python3}+' {} \;
find $RPM_BUILD_ROOT%{testsdir}/scripts/qmp/* -maxdepth 1 -type f -exec sed -i -e '1 s+/usr/bin/python+%{__python3}+' {} \;

install -p -m 0644 %{SOURCE36} $RPM_BUILD_ROOT%{testsdir}/README

make DESTDIR=$RPM_BUILD_ROOT \
    sharedir="%{_datadir}/qemu-kvm" \
    datadir="%{_datadir}/qemu-kvm" \
    install

mkdir -p $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset

# Install qemu-guest-agent service and udev rules
install -m 0644 %{_sourcedir}/qemu-guest-agent.service %{buildroot}%{_unitdir}
install -m 0644 %{_sourcedir}/qemu-ga.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/qemu-ga
install -m 0644 %{_sourcedir}/99-qemu-guest-agent.rules %{buildroot}%{_udevrulesdir}

# - the fsfreeze hook script:
install -D --preserve-timestamps \
            scripts/qemu-guest-agent/fsfreeze-hook \
            $RPM_BUILD_ROOT%{_sysconfdir}/qemu-ga/fsfreeze-hook

# - the directory for user scripts:
mkdir $RPM_BUILD_ROOT%{_sysconfdir}/qemu-ga/fsfreeze-hook.d

# - and the fsfreeze script samples:
mkdir --parents $RPM_BUILD_ROOT%{_datadir}/qemu-kvm/qemu-ga/fsfreeze-hook.d/
install --preserve-timestamps --mode=0644 \
             scripts/qemu-guest-agent/fsfreeze-hook.d/*.sample \
             $RPM_BUILD_ROOT%{_datadir}/qemu-kvm/qemu-ga/fsfreeze-hook.d/

# - Install dedicated log directory:
mkdir -p -v $RPM_BUILD_ROOT%{_localstatedir}/log/qemu-ga/

mkdir -p $RPM_BUILD_ROOT%{_bindir}
install -c -m 0755  qga/qemu-ga ${RPM_BUILD_ROOT}%{_bindir}/qemu-ga

install -m 0755 %{kvm_target}-softmmu/qemu-system-%{kvm_target} $RPM_BUILD_ROOT%{_libexecdir}/qemu-kvm
install -m 0644 qemu-kvm.stp $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/
install -m 0644 qemu-kvm-simpletrace.stp $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/

rm $RPM_BUILD_ROOT%{_bindir}/qemu-system-%{kvm_target}
rm $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/qemu-system-%{kvm_target}.stp
rm $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/qemu-system-%{kvm_target}-simpletrace.stp

# Install simpletrace
install -m 0755 scripts/simpletrace.py $RPM_BUILD_ROOT%{_datadir}/qemu-kvm/simpletrace.py
# Avoid ambiguous 'python' interpreter name
mkdir -p $RPM_BUILD_ROOT%{_datadir}/qemu-kvm/tracetool
install -m 0644 -t $RPM_BUILD_ROOT%{_datadir}/qemu-kvm/tracetool scripts/tracetool/*.py
mkdir -p $RPM_BUILD_ROOT%{_datadir}/qemu-kvm/tracetool/backend
install -m 0644 -t $RPM_BUILD_ROOT%{_datadir}/qemu-kvm/tracetool/backend scripts/tracetool/backend/*.py
mkdir -p $RPM_BUILD_ROOT%{_datadir}/qemu-kvm/tracetool/format
install -m 0644 -t $RPM_BUILD_ROOT%{_datadir}/qemu-kvm/tracetool/format scripts/tracetool/format/*.py

mkdir -p $RPM_BUILD_ROOT%{qemudocdir}
install -p -m 0644 -t ${RPM_BUILD_ROOT}%{qemudocdir} ../README.rst ../COPYING ../COPYING.LIB ../LICENSE ../docs/interop/qmp-spec.txt
chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man1/*
chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man8/*

install -D -p -m 0644 ../qemu.sasl $RPM_BUILD_ROOT%{_sysconfdir}/sasl2/qemu-kvm.conf

# Provided by package openbios
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/openbios-ppc
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/openbios-sparc32
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/openbios-sparc64
# Provided by package SLOF
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/slof.bin

# Remove unpackaged files.
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/palcode-clipper
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/petalogix*.dtb
rm -f ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/bamboo.dtb
rm -f ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/ppc_rom.bin
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/s390-zipl.rom
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/u-boot.e500
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/qemu_vga.ndrv
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/skiboot.lid

rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/s390-ccw.img
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/hppa-firmware.img
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/canyonlands.dtb
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/u-boot-sam460-20100605.bin

%ifarch s390x
    # Use the s390-ccw.img that we've just built, not the pre-built one
    install -m 0644 pc-bios/s390-ccw/s390-ccw.img $RPM_BUILD_ROOT%{_datadir}/qemu-kvm/
%else
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/s390-netboot.img
    rm -rf ${RPM_BUILD_ROOT}%{_libdir}/qemu-kvm/hw-s390x-virtio-gpu-ccw.so
%endif

%ifnarch %{power64}
    rm -f ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/spapr-rtas.bin
%endif

%ifnarch x86_64
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/kvmvapic.bin
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/linuxboot.bin
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/multiboot.bin
%endif

# Remove sparc files
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/QEMU,tcx.bin
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/QEMU,cgthree.bin

# Remove ivshmem example programs
rm -rf ${RPM_BUILD_ROOT}%{_bindir}/ivshmem-client
rm -rf ${RPM_BUILD_ROOT}%{_bindir}/ivshmem-server

# Remove efi roms
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/efi*.rom

# Provided by package ipxe
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/pxe*rom
# Provided by package vgabios
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/vgabios*bin
# Provided by package seabios
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/bios*.bin
# Provided by package sgabios
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/qemu-kvm/sgabios.bin

rm -rf ${RPM_BUILD_ROOT}%{_libdir}/debug/usr/bin/virtfs-proxy-helper-5.0.0-2020.08.13.el8.2.x86_64.debug
rm -rf ${RPM_BUILD_ROOT}%{_libdir}/debug/usr/libexec/virtiofsd-5.0.0-2020.08.13.el8.2.x86_64.debug
rm -rf ${RPM_BUILD_ROOT}%{_libdir}/debug/usr/lib64/qemu-kvm/hw-s390x-virtio-gpu-ccw.so-5.2.91-2021.03.19.el8.9.x86_64.debug
# the pxe gpxe images will be symlinks to the images on
# /usr/share/ipxe, as QEMU doesn't know how to look
# for other paths, yet.
pxe_link() {
    ln -s ../ipxe.efi/$2.rom %{buildroot}%{_datadir}/qemu-kvm/efi-$1.rom
}

%ifnarch aarch64 s390x
pxe_link e1000 8086100e
pxe_link ne2k_pci 10ec8029
pxe_link pcnet 10222000
pxe_link rtl8139 10ec8139
pxe_link virtio 1af41000
pxe_link e1000e 808610d3
%endif

rom_link() {
    ln -s $1 %{buildroot}%{_datadir}/qemu-kvm/$2
}

%ifnarch aarch64 s390x
  rom_link ../seavgabios/vgabios-isavga.bin vgabios.bin
  rom_link ../seavgabios/vgabios-cirrus.bin vgabios-cirrus.bin
  rom_link ../seavgabios/vgabios-qxl.bin vgabios-qxl.bin
  rom_link ../seavgabios/vgabios-stdvga.bin vgabios-stdvga.bin
  rom_link ../seavgabios/vgabios-vmware.bin vgabios-vmware.bin
  rom_link ../seavgabios/vgabios-virtio.bin vgabios-virtio.bin
%endif
%ifarch x86_64
  rom_link ../seabios/bios.bin bios.bin
  rom_link ../seabios/bios-256k.bin bios-256k.bin
  rom_link ../sgabios/sgabios.bin sgabios.bin
%endif

%if 0%{have_kvm_setup}
    install -D -p -m 755 %{SOURCE21} $RPM_BUILD_ROOT%{_prefix}/lib/systemd/kvm-setup
    install -D -p -m 644 %{SOURCE22} $RPM_BUILD_ROOT%{_unitdir}/kvm-setup.service
    install -D -p -m 644 %{SOURCE23} $RPM_BUILD_ROOT%{_presetdir}/85-kvm.preset
%endif

%if 0%{have_memlock_limits}
    install -D -p -m 644 %{SOURCE28} $RPM_BUILD_ROOT%{_sysconfdir}/security/limits.d/95-kvm-memlock.conf
%endif

# Install rules to use the bridge helper with libvirt's virbr0
install -D -m 0644 %{SOURCE12} $RPM_BUILD_ROOT%{_sysconfdir}/qemu-kvm/bridge.conf

# Install qemu-pr-helper service
install -m 0644 %{_sourcedir}/qemu-pr-helper.service %{buildroot}%{_unitdir}
install -m 0644 %{_sourcedir}/qemu-pr-helper.socket %{buildroot}%{_unitdir}

find $RPM_BUILD_ROOT -name '*.la' -or -name '*.a' | xargs rm -f

# We need to make the block device modules executable else
# RPM won't pick up their dependencies.
chmod +x $RPM_BUILD_ROOT%{_libdir}/qemu-kvm/block-*.so

# // Disable checks until we figure out how to do this from inside a
# // a docker container
# %check
# export DIFF=diff; make check V=1

%post -n intel-mvp-tdx-qemu-kvm-core
# load kvm modules now, so we can make sure no reboot is needed.
# If there's already a kvm module installed, we don't mess with it
%udev_rules_update
sh %{_sysconfdir}/sysconfig/modules/kvm.modules &> /dev/null || :
    udevadm trigger --subsystem-match=misc --sysname-match=kvm --action=add || :
%if %{have_kvm_setup}
    systemctl daemon-reload # Make sure it sees the new presets and unitfile
    %systemd_post kvm-setup.service
    if systemctl is-enabled kvm-setup.service > /dev/null; then
        systemctl start kvm-setup.service
    fi
%endif

%if %{have_kvm_setup}
%preun -n intel-mvp-tdx-qemu-kvm-core
%systemd_preun kvm-setup.service
%endif

%post -n intel-mvp-tdx-qemu-kvm-common
%systemd_post ksm.service
%systemd_post ksmtuned.service

getent group kvm >/dev/null || groupadd -g 36 -r kvm
getent group qemu >/dev/null || groupadd -g 107 -r qemu
getent passwd qemu >/dev/null || \
useradd -r -u 107 -g qemu -G kvm -d / -s /sbin/nologin \
  -c "qemu user" qemu

%preun -n intel-mvp-tdx-qemu-kvm-common
%systemd_preun ksm.service
%systemd_preun ksmtuned.service

%postun -n intel-mvp-tdx-qemu-kvm-common
%systemd_postun_with_restart ksm.service
%systemd_postun_with_restart ksmtuned.service

%global qemu_kvm_files \
%{_libexecdir}/qemu-kvm \
%{_datadir}/systemtap/tapset/qemu-kvm.stp \
%{_datadir}/qemu-kvm/trace-events-all \
%{_datadir}/systemtap/tapset/qemu-kvm-simpletrace.stp \
%{_datadir}/systemtap/tapset/qemu-system-x86_64-log.stp \

%files
# Deliberately empty


%files -n intel-mvp-tdx-qemu-kvm-common
%defattr(-,root,root)
/usr/share/icons/hicolor/128x128/apps/qemu.png
/usr/share/icons/hicolor/16x16/apps/qemu.png
/usr/share/icons/hicolor/24x24/apps/qemu.png
/usr/share/icons/hicolor/256x256/apps/qemu.png
/usr/share/icons/hicolor/32x32/apps/qemu.bmp
/usr/share/icons/hicolor/32x32/apps/qemu.png
/usr/share/icons/hicolor/48x48/apps/qemu.png
/usr/share/icons/hicolor/512x512/apps/qemu.png
/usr/share/icons/hicolor/64x64/apps/qemu.png
/usr/share/icons/hicolor/scalable/apps/qemu.svg
%dir %{qemudocdir}
%doc %{qemudocdir}/devel/atomics.html
%doc %{qemudocdir}/devel/bitops.html
%doc %{qemudocdir}/devel/block-coroutine-wrapper.html
%doc %{qemudocdir}/devel/build-system.html
%doc %{qemudocdir}/devel/clocks.html
%doc %{qemudocdir}/devel/control-flow-integrity.html
%doc %{qemudocdir}/devel/decodetree.html
%doc %{qemudocdir}/devel/fuzzing.html
%doc %{qemudocdir}/devel/index.html
%doc %{qemudocdir}/devel/kconfig.html
%doc %{qemudocdir}/devel/loads-stores.html
%doc %{qemudocdir}/devel/memory.html
%doc %{qemudocdir}/devel/migration.html
%doc %{qemudocdir}/devel/multi-process.html
%doc %{qemudocdir}/devel/multi-thread-tcg.html
%doc %{qemudocdir}/devel/qgraph.html
%doc %{qemudocdir}/devel/qom.html
%doc %{qemudocdir}/devel/qtest.html
%doc %{qemudocdir}/devel/reset.html
%doc %{qemudocdir}/devel/s390-dasd-ipl.html
%doc %{qemudocdir}/devel/secure-coding-practices.html
%doc %{qemudocdir}/devel/stable-process.html
%doc %{qemudocdir}/devel/style.html
%doc %{qemudocdir}/devel/tcg.html
%doc %{qemudocdir}/devel/tcg-icount.html
%doc %{qemudocdir}/devel/tcg-plugins.html
%doc %{qemudocdir}/devel/testing.html
%doc %{qemudocdir}/devel/tracing.html
%doc %{qemudocdir}/interop/bitmaps.html
%doc %{qemudocdir}/interop/dbus.html
%doc %{qemudocdir}/interop/dbus-vmstate.html
%doc %{qemudocdir}/interop/index.html
%doc %{qemudocdir}/interop/live-block-operations.html
%doc %{qemudocdir}/interop/pr-helper.html
%doc %{qemudocdir}/interop/qemu-ga.html
%doc %{qemudocdir}/interop/qemu-ga-ref.html
%doc %{qemudocdir}/interop/qemu-qmp-ref.html
%doc %{qemudocdir}/interop/qemu-storage-daemon-qmp-ref.html
%doc %{qemudocdir}/interop/vhost-user.html
%doc %{qemudocdir}/interop/vhost-user-gpu.html
%doc %{qemudocdir}/interop/vhost-vdpa.html
%doc %{qemudocdir}/specs/acpi_hest_ghes.html
%doc %{qemudocdir}/specs/acpi_hw_reduced_hotplug.html
%doc %{qemudocdir}/specs/index.html
%doc %{qemudocdir}/specs/ppc-spapr-numa.html
%doc %{qemudocdir}/specs/ppc-spapr-xive.html
%doc %{qemudocdir}/specs/ppc-xive.html
%doc %{qemudocdir}/specs/tpm.html
%doc %{qemudocdir}/system/arm/aspeed.html
%doc %{qemudocdir}/system/arm/collie.html
%doc %{qemudocdir}/system/arm/cpu-features.html
%doc %{qemudocdir}/system/arm/digic.html
%doc %{qemudocdir}/system/arm/gumstix.html
%doc %{qemudocdir}/system/arm/integratorcp.html
%doc %{qemudocdir}/system/arm/mps2.html
%doc %{qemudocdir}/system/arm/musca.html
%doc %{qemudocdir}/system/arm/musicpal.html
%doc %{qemudocdir}/system/arm/nseries.html
%doc %{qemudocdir}/system/arm/nuvoton.html
%doc %{qemudocdir}/system/arm/orangepi.html
%doc %{qemudocdir}/system/arm/palm.html
%doc %{qemudocdir}/system/arm/raspi.html
%doc %{qemudocdir}/system/arm/realview.html
%doc %{qemudocdir}/system/arm/sabrelite.html
%doc %{qemudocdir}/system/arm/sbsa.html
%doc %{qemudocdir}/system/arm/stellaris.html
%doc %{qemudocdir}/system/arm/sx1.html
%doc %{qemudocdir}/system/arm/versatile.html
%doc %{qemudocdir}/system/arm/vexpress.html
%doc %{qemudocdir}/system/arm/virt.html
%doc %{qemudocdir}/system/arm/xlnx-versal-virt.html
%doc %{qemudocdir}/system/arm/xscale.html
%doc %{qemudocdir}/system/i386/microvm.html
%doc %{qemudocdir}/system/i386/pc.html
%doc %{qemudocdir}/system/ppc/embedded.html
%doc %{qemudocdir}/system/ppc/powermac.html
%doc %{qemudocdir}/system/ppc/powernv.html
%doc %{qemudocdir}/system/ppc/prep.html
%doc %{qemudocdir}/system/ppc/pseries.html
%doc %{qemudocdir}/system/riscv/microchip-icicle-kit.html
%doc %{qemudocdir}/system/riscv/sifive_u.html
%doc %{qemudocdir}/system/s390x/3270.html
%doc %{qemudocdir}/system/s390x/bootdevices.html
%doc %{qemudocdir}/system/s390x/css.html
%doc %{qemudocdir}/system/s390x/protvirt.html
%doc %{qemudocdir}/system/s390x/vfio-ap.html
%doc %{qemudocdir}/system/s390x/vfio-ccw.html
%doc %{qemudocdir}/system/build-platforms.html
%doc %{qemudocdir}/system/cpu-hotplug.html
%doc %{qemudocdir}/system/deprecated.html
%doc %{qemudocdir}/system/gdb.html
%doc %{qemudocdir}/system/generic-loader.html
%doc %{qemudocdir}/system/guest-loader.html
%doc %{qemudocdir}/system/images.html
%doc %{qemudocdir}/system/index.html
%doc %{qemudocdir}/system/invocation.html
%doc %{qemudocdir}/system/ivshmem.html
%doc %{qemudocdir}/system/keys.html
%doc %{qemudocdir}/system/license.html
%doc %{qemudocdir}/system/linuxboot.html
%doc %{qemudocdir}/system/managed-startup.html
%doc %{qemudocdir}/system/monitor.html
%doc %{qemudocdir}/system/multi-process.html
%doc %{qemudocdir}/system/mux-chardev.html
%doc %{qemudocdir}/system/net.html
%doc %{qemudocdir}/system/pr-manager.html
%doc %{qemudocdir}/system/qemu-block-drivers.html
%doc %{qemudocdir}/system/qemu-cpu-models.html
%doc %{qemudocdir}/system/qemu-manpage.html
%doc %{qemudocdir}/system/quickstart.html
%doc %{qemudocdir}/system/removed-features.html
%doc %{qemudocdir}/system/security.html
%doc %{qemudocdir}/system/target-arm.html
%doc %{qemudocdir}/system/target-avr.html
%doc %{qemudocdir}/system/target-i386.html
%doc %{qemudocdir}/system/target-m68k.html
%doc %{qemudocdir}/system/target-mips.html
%doc %{qemudocdir}/system/target-ppc.html
%doc %{qemudocdir}/system/target-riscv.html
%doc %{qemudocdir}/system/target-rx.html
%doc %{qemudocdir}/system/target-s390x.html
%doc %{qemudocdir}/system/target-sparc.html
%doc %{qemudocdir}/system/target-sparc64.html
%doc %{qemudocdir}/system/target-xtensa.html
%doc %{qemudocdir}/system/targets.html
%doc %{qemudocdir}/system/tls.html
%doc %{qemudocdir}/system/usb.html
%doc %{qemudocdir}/system/virtio-net-failover.html
%doc %{qemudocdir}/system/virtio-pmem.html
%doc %{qemudocdir}/system/vnc-security.html
%doc %{qemudocdir}/tools/index.html
%doc %{qemudocdir}/tools/qemu-img.html
%doc %{qemudocdir}/tools/qemu-nbd.html
%doc %{qemudocdir}/tools/qemu-pr-helper.html
%doc %{qemudocdir}/tools/qemu-storage-daemon.html
%doc %{qemudocdir}/tools/qemu-trace-stap.html
%doc %{qemudocdir}/tools/virtfs-proxy-helper.html
%doc %{qemudocdir}/tools/virtiofsd.html
%doc %{qemudocdir}/user/index.html
%doc %{qemudocdir}/user/main.html
%doc %{qemudocdir}/_static/pygments.css
%doc %{qemudocdir}/_static/ajax-loader.gif
%doc %{qemudocdir}/_static/basic.css
%doc %{qemudocdir}/_static/comment-bright.png
%doc %{qemudocdir}/_static/comment-close.png
%doc %{qemudocdir}/_static/comment.png
%doc %{qemudocdir}/_static/doctools.js
%doc %{qemudocdir}/_static/documentation_options.js
%doc %{qemudocdir}/_static/down-pressed.png
%doc %{qemudocdir}/_static/down.png
%doc %{qemudocdir}/_static/file.png
%doc %{qemudocdir}/_static/jquery-3.2.1.js
%doc %{qemudocdir}/_static/jquery.js
%doc %{qemudocdir}/_static/minus.png
%doc %{qemudocdir}/_static/plus.png
%doc %{qemudocdir}/_static/searchtools.js
%doc %{qemudocdir}/_static/underscore-1.3.1.js
%doc %{qemudocdir}/_static/underscore.js
%doc %{qemudocdir}/_static/up-pressed.png
%doc %{qemudocdir}/_static/up.png
%doc %{qemudocdir}/_static/websupport.js
%doc %{qemudocdir}/_static/alabaster.css
%doc %{qemudocdir}/_static/custom.css
%doc %{qemudocdir}/index.html
%doc %{qemudocdir}/genindex.html
%doc %{qemudocdir}/search.html
%doc %{qemudocdir}/.buildinfo
%doc %{qemudocdir}/searchindex.js
%doc %{qemudocdir}/objects.inv
%doc %{qemudocdir}/README.rst
%doc %{qemudocdir}/COPYING
%doc %{qemudocdir}/COPYING.LIB
%doc %{qemudocdir}/LICENSE
%doc %{qemudocdir}/qmp-spec.txt
%{_mandir}/man1/qemu-trace-stap.1.gz
%{_mandir}/man1/qemu.1.gz
%{_mandir}/man7/qemu-cpu-models.7.gz

%{_mandir}/man7/qemu-qmp-ref.7*
%{_bindir}/qemu-keymap
%{_bindir}/qemu-pr-helper
%{_unitdir}/qemu-pr-helper.service
%{_unitdir}/qemu-pr-helper.socket
%{_mandir}/man8/qemu-pr-helper.8*
%{_mandir}/man7/qemu-ga-ref.7*

%{_libexecdir}/virtfs-proxy-helper
%{_libexecdir}/virtiofsd
%{_mandir}/man1/virtfs-proxy-helper.1.gz
%{_mandir}/man1/virtiofsd.1.gz
%{_datadir}/qemu-kvm/vhost-user/50-qemu-virtiofsd.json

%dir %{_datadir}/qemu-kvm/
%{_datadir}/qemu-kvm/keymaps/
%{_mandir}/man7/qemu-block-drivers.7*
%attr(4755, -, -) %{_libexecdir}/qemu-bridge-helper
%config(noreplace) %{_sysconfdir}/sasl2/qemu-kvm.conf
%{_unitdir}/ksm.service
%{_libexecdir}/ksmctl
%config(noreplace) %{_sysconfdir}/sysconfig/ksm
%{_unitdir}/ksmtuned.service
%{_sbindir}/ksmtuned
%{_udevdir}/udev-kvm-check
%{_udevrulesdir}/81-kvm-rhel.rules
%ghost %{_sysconfdir}/kvm
%config(noreplace) %{_sysconfdir}/ksmtuned.conf
%dir %{_sysconfdir}/qemu-kvm
%config(noreplace) %{_sysconfdir}/qemu-kvm/bridge.conf
%config(noreplace) %{_sysconfdir}/modprobe.d/vhost.conf
%config(noreplace) %{_sysconfdir}/modprobe.d/kvm.conf
%{_datadir}/qemu-kvm/simpletrace.py*
%{_datadir}/qemu-kvm/tracetool/*.py*
%{_datadir}/qemu-kvm/tracetool/backend/*.py*
%{_datadir}/qemu-kvm/tracetool/format/*.py*

%files -n intel-mvp-tdx-qemu-kvm-core
%defattr(-,root,root)
%ifarch x86_64
    %{_datadir}/qemu-kvm/bios.bin
    %{_datadir}/qemu-kvm/bios-256k.bin
    %{_datadir}/qemu-kvm/linuxboot.bin
    %{_datadir}/qemu-kvm/multiboot.bin
    %{_datadir}/qemu-kvm/kvmvapic.bin
    %{_datadir}/qemu-kvm/sgabios.bin
%endif
%ifarch s390x
    %{_datadir}/qemu-kvm/s390-ccw.img
    %{_datadir}/qemu-kvm/s390-netboot.img
%endif
%ifnarch aarch64 s390x
    %{_datadir}/qemu-kvm/vgabios.bin
    %{_datadir}/qemu-kvm/vgabios-cirrus.bin
    %{_datadir}/qemu-kvm/vgabios-qxl.bin
    %{_datadir}/qemu-kvm/vgabios-stdvga.bin
    %{_datadir}/qemu-kvm/vgabios-vmware.bin
    %{_datadir}/qemu-kvm/vgabios-virtio.bin
    %{_datadir}/qemu-kvm/efi-e1000.rom
    %{_datadir}/qemu-kvm/efi-e1000e.rom
    %{_datadir}/qemu-kvm/efi-virtio.rom
    %{_datadir}/qemu-kvm/efi-pcnet.rom
    %{_datadir}/qemu-kvm/efi-rtl8139.rom
    %{_datadir}/qemu-kvm/efi-ne2k_pci.rom
%endif
%{_datadir}/qemu-kvm/linuxboot_dma.bin
%{_datadir}/qemu-kvm/dump-guest-memory.py*
%ifarch %{power64}
    %{_datadir}/qemu-kvm/spapr-rtas.bin
%endif
%{?qemu_kvm_files:}
%if 0%{have_kvm_setup}
    %{_prefix}/lib/systemd/kvm-setup
    %{_unitdir}/kvm-setup.service
    %{_presetdir}/85-kvm.preset
%endif
%if 0%{have_memlock_limits}
    %{_sysconfdir}/security/limits.d/95-kvm-memlock.conf
%endif

%{_datadir}/qemu-kvm/edk2-aarch64-code.fd
%{_datadir}/qemu-kvm/edk2-arm-code.fd
%{_datadir}/qemu-kvm/edk2-arm-vars.fd
%{_datadir}/qemu-kvm/edk2-i386-code.fd
%{_datadir}/qemu-kvm/edk2-i386-secure-code.fd
%{_datadir}/qemu-kvm/edk2-i386-vars.fd
%{_datadir}/qemu-kvm/edk2-licenses.txt
%{_datadir}/qemu-kvm/edk2-x86_64-code.fd
%{_datadir}/qemu-kvm/edk2-x86_64-secure-code.fd
%{_datadir}/qemu-kvm/firmware/50-edk2-i386-secure.json
%{_datadir}/qemu-kvm/firmware/50-edk2-x86_64-secure.json
%{_datadir}/qemu-kvm/firmware/60-edk2-aarch64.json
%{_datadir}/qemu-kvm/firmware/60-edk2-arm.json
%{_datadir}/qemu-kvm/firmware/60-edk2-i386.json
%{_datadir}/qemu-kvm/firmware/60-edk2-x86_64.json
%{_datadir}/qemu-kvm/npcm7xx_bootrom.bin
%{_datadir}/qemu-kvm/opensbi-riscv32-generic-fw_dynamic.bin
%{_datadir}/qemu-kvm/opensbi-riscv32-generic-fw_dynamic.elf
%{_datadir}/qemu-kvm/opensbi-riscv64-generic-fw_dynamic.bin
%{_datadir}/qemu-kvm/opensbi-riscv64-generic-fw_dynamic.elf
%{_datadir}/qemu-kvm/qboot.rom

%{_datadir}/qemu-kvm/pvh.bin
%{_datadir}/qemu-kvm/qemu-nsis.bmp
/usr/share/applications/qemu.desktop


%files -n intel-mvp-tdx-qemu-img
%defattr(-,root,root)
%{_bindir}/elf2dmp
%{_bindir}/qemu-img
%{_bindir}/qemu-io
%{_bindir}/qemu-nbd
%{_bindir}/qemu-edid
%{_bindir}/qemu-storage-daemon
%{_bindir}/qemu-trace-stap
%{_mandir}/man1/qemu-img.1*
%{_mandir}/man1/qemu-storage-daemon.1*
%{_mandir}/man7/qemu-storage-daemon-qmp-ref.7*
%{_mandir}/man8/qemu-nbd.8*

%files -n intel-mvp-tdx-qemu-guest-agent
%defattr(-,root,root,-)
%doc COPYING
%{_bindir}/qemu-ga
%{_mandir}/man8/qemu-ga.8*
%{_unitdir}/qemu-guest-agent.service
%{_udevrulesdir}/99-qemu-guest-agent.rules
%config(noreplace) %{_sysconfdir}/sysconfig/qemu-ga
%{_sysconfdir}/qemu-ga
%{_datadir}/qemu-kvm/qemu-ga
%dir %{_localstatedir}/log/qemu-ga

%files tests
%{testsdir}

%files block-curl
%{_libdir}/qemu-kvm/block-curl.so

%if %{have_gluster}
%files block-gluster
%{_libdir}/qemu-kvm/block-gluster.so
%endif

%files block-iscsi
%{_libdir}/qemu-kvm/block-iscsi.so

%files block-rbd
%{_libdir}/qemu-kvm/block-rbd.so

%files block-ssh
%{_libdir}/qemu-kvm/block-ssh.so

%files spice
%{_libdir}/qemu-kvm/ui-spice-app.so
%{_libdir}/qemu-kvm/ui-spice-core.so
%{_libdir}/qemu-kvm/chardev-spice.so
%{_libdir}/qemu-kvm/audio-spice.so

%files hw-display
%{_libdir}/qemu-kvm/hw-display-qxl.so
%{_libdir}/qemu-kvm/hw-display-virtio-gpu-pci.so
%{_libdir}/qemu-kvm/hw-display-virtio-gpu.so
%{_libdir}/qemu-kvm/hw-display-virtio-vga.so

%files hw-usb
%{_libdir}/qemu-kvm/hw-usb-redirect.so
%{_libdir}/qemu-kvm/hw-usb-smartcard.so

%files ui
%{_libdir}/qemu-kvm/ui-egl-headless.so
%{_libdir}/qemu-kvm/ui-opengl.so
