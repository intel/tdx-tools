%global debug_package %{nil}

# This spec file began as CentOS's ovmf spec file, then cut down and modified.

Name:       intel-mvp-vtpm-td
Version:    v0.1.0
Release:    mvp6
Summary:    Trust Domain (TD) based vTPM solution
Group:      Applications/Emulators
License:    BSD and OpenSSL and MIT
URL:        https://github.com/intel/vtpm-td

Source0: vtpm-td.tar.gz

BuildRequires:  llvm clang
BuildRequires:  pkgconf
BuildRequires:  wget
BuildRequires:  ocaml
BuildRequires:  ocaml-ocamlbuild

# Only OVMF includes 80x86 assembly files (*.nasm*).
BuildRequires:  nasm

# Use cargo nightly-2022-11-15 instead.
BuildConflicts: cargo

BuildArch:  noarch

%description
rust-vtpm-td is a Trust Domain (TD) based vTPM solution, which can support vTPM functionality with VMM out of TCB.

%prep
%setup -q -n vtpm-td

# Done by %setup, but we do not use it for the auxiliary tarballs
chmod -Rf a+rX,u+w,g-w,o-w .

%build

curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > rustup-init.sh
chmod +x rustup-init.sh;./rustup-init.sh -y --profile minimal --default-toolchain nightly-2022-11-15
source "$HOME/.cargo/env"
cargo install cargo-xbuild
rustup component add rust-src

export CC=clang
export AR=llvm-ar
# build
sh_script/pre-build.sh
sh_script/build.sh

%install
mkdir -p %{buildroot}/usr/share/tdx-vtpm/
cp target/x86_64-unknown-none/release/vtpmtd.bin %{buildroot}/usr/share/tdx-vtpm

%files
/usr/share/tdx-vtpm/vtpmtd.bin
