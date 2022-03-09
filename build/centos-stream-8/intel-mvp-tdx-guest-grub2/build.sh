#!/usr/bin/bash

set -e

UPSTREAM_GIT_URI="https://github.com/rhboot/grub2.git"
UPSTREAM_BRANCH="rhel-8.4.0"
DOWNSTREAM_GIT_URI="https://github.com/intel/grub-tdx.git"
DOWNSTREAM_BRANCH="2.02-rhel-8.4"

CURR_DIR=$(dirname "$(readlink -f "$0")")
RPMBUILD_DIR=$CURR_DIR/rpmbuild
PATCH_SET=patches-tdx-grub-2.02
SPEC=$CURR_DIR/tdx-guest-grub2.spec

pushd "$CURR_DIR"
mkdir -p $PATCH_SET
mkdir -p "$RPMBUILD_DIR"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

generate() {
    # To regenerate the sources please delete grub-2.02.tar.gz
    if [[ -f $RPMBUILD_DIR/SOURCES/grub-2.02.tar.gz ]]; then
        return 0
    fi

    echo "**** Generate tdx patchset and upstream tarball ****"
    rm -rf grub-2.02
    git clone -b $DOWNSTREAM_BRANCH --single-branch $DOWNSTREAM_GIT_URI grub-2.02
    cd grub-2.02
    upstream_base=$(git ls-remote $UPSTREAM_GIT_URI refs/heads/$UPSTREAM_BRANCH | cut -f 1)
    git format-patch "$upstream_base"..$DOWNSTREAM_BRANCH
    git checkout "$upstream_base"
    cd ..
    mv grub-2.02/*.patch $PATCH_SET/
    tar --exclude=.git --exclude=.gitignore -czf "$RPMBUILD_DIR"/SOURCES/grub-2.02.tar.gz grub-2.02
    rm -rf grub-2.02
}

prepare() {
    echo "**** Will apply all patches put in $PATCH_SET ****"
    tar cvf $PATCH_SET.tar.gz -C $PATCH_SET .
    mv "$CURR_DIR"/$PATCH_SET.tar.gz "$RPMBUILD_DIR"/SOURCES/
    cp "$CURR_DIR"/grub.macros "$RPMBUILD_DIR"/SOURCES/
}

build() {
    echo "**** Install dependencies and build RPM packages ****"
    sudo -E dnf builddep --define "_topdir $RPMBUILD_DIR" -y "$SPEC"
    rpmbuild --define "_topdir $RPMBUILD_DIR" --undefine=_disable_source_fetch -v -ba "$SPEC"
}

generate
prepare
build

popd
