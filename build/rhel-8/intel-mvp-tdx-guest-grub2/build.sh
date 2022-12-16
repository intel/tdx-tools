#!/usr/bin/bash

set -e

UPSTREAM_BASE_COMMIT=52823acbf284ae050e3f63590548bfe515c743c8
DOWNSTREAM_GIT_URI="https://github.com/intel/grub-tdx.git"
DOWNSTREAM_TAG="tdx-guest-rhel-8.5-2021.11.22"

CURR_DIR=$(dirname "$(readlink -f "$0")")
RPMBUILD_DIR=$CURR_DIR/rpmbuild
PATCH_SET=patches-tdx-grub-2.02
SPEC=$CURR_DIR/tdx-guest-grub2.spec
REPO_DIR=grub-2.02

pushd "$CURR_DIR"
mkdir -p $PATCH_SET
mkdir -p "$RPMBUILD_DIR"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

generate() {
    # to regenerate the sources please delete grub-2.02.tar.gz
    if [[ -f $RPMBUILD_DIR/SOURCES/grub-2.02.tar.gz ]]; then
        return 0
    fi

    echo "**** Generate tdx patchset and upstream tarball ****"
    rm -rf $REPO_DIR
    git clone -b $DOWNSTREAM_TAG --single-branch $DOWNSTREAM_GIT_URI $REPO_DIR
    cd $REPO_DIR
    git format-patch $UPSTREAM_BASE_COMMIT..$DOWNSTREAM_TAG
    git checkout $UPSTREAM_BASE_COMMIT
    cd ..
    mv $REPO_DIR/*.patch $PATCH_SET/
    tar --exclude=.git --exclude=.gitignore -czf "$RPMBUILD_DIR"/SOURCES/$REPO_DIR.tar.gz $REPO_DIR
    rm -rf $REPO_DIR
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
