#!/bin/bash

CURR_DIR=$(pwd)

REQUIRED_PACKAGES_CENTOS=(
  python3-libvirt
  libvirt-devel
  python36-devel
  python3-pip
)

REQUIRED_PACKAGES_UBUNTU=(
  python3-libvirt
  libvirt-dev
  python3-dev
  python3-pip
)

# Check whether required packages already been installed.
DISTRO=$(grep -w 'NAME' /etc/os-release)
if [[ "$DISTRO" =~ .*"Ubuntu".* ]]; then
  for package in "${REQUIRED_PACKAGES_UBUNTU[@]}"; do
    apt list --installed | grep "$package" > /dev/null 2>&1
    ret=$?
    if [ ! $ret -eq 0 ]; then
      echo "Please install package $package."
      return 1
    fi
  done
else
  for package in "${REQUIRED_PACKAGES_CENTOS[@]}"; do
    dnf list installed | grep "$package" > /dev/null 2>&1
    ret=$?
    if [ ! $ret -eq 0 ]; then
      echo "Please install package $package."
      return 1
    fi
  done
fi

# Setup the python virtualenv
if [[ ! -d ${CURR_DIR}/venv ]]; then
  python3 -m pip install virtualenv
  python3 -m virtualenv -p python3 "${CURR_DIR}"/venv
  # shellcheck source=/dev/null
  source "${CURR_DIR}"/venv/bin/activate
  pip3 install -r requirements.txt
  ret=$?
  if [ ! $ret -eq 0 ]; then
    echo "Fail to install python PIP packages, please check your proxy (https_proxy) or setup PyPi mirror."
    deactivate
    rm "${CURR_DIR}"/venv -fr
    return 1
  fi
else
  # shellcheck source=/dev/null
  source "${CURR_DIR}"/venv/bin/activate
fi

# Install tests_tdx into the PYTHON path, so you can use "python3 -m pytest tests_tdx/xxx.py" to
# run the case module individually
export PYTHONPATH=$PYTHONPATH:$CURR_DIR/tests

# Add pycloudstack into PYTHONPATH in case not installing it via pip3
if [[ -d $CURR_DIR/../utils/pycloudstack ]]; then
  if pip3 list | grep -q "pycloudstack"; then
    echo "pycloudstack is already installed but will be replaced by $CURR_DIR/../utils/pycloudstack"
  fi

  # pycloudstack package could be installed via "pip3" or copied to $CURR_DIR/pycloudstack
  export PYTHONPATH=$CURR_DIR/../utils/pycloudstack:$PYTHONPATH
fi

# Check whether virt-customize tool was installed
if ! command -v virt-customize &>/dev/null; then
  echo WARNING! Please install libguestfs-tools
  return 1
fi

# Check whether libvirt service started
if ! systemctl --all --type service | grep -q "libvirtd"; then
  echo WARNING! Please install intel-mvp-tdx-libvirt and \"systemctl start libvirtd\"
  return 1
fi

# Check whether virtual bridge virbr0 was created
if ! ip a | grep -q virbr0; then
  echo WARNING! Please enable virbr0 via \"virsh net-start default\", you may need remove firewall via \"dnf remove firewalld\" or \"apt remove ufw\"
  return 1
fi

# Check whether current user belong to libvirt
if [[ ! $(id -nG "$USER") == *"libvirt"* ]]; then
  echo WARNING! Please add user "$USER" into group "libvirt" via \"sudo usermod -aG libvirt "$USER"\"
  return 1
fi

#
# Start from qemu 6.2's commit: https://github.com/qemu/qemu/commit/5dacda5167560b3af8eadbce5814f60ba44b467e.
# LIBGUESTFS_BACKEND=direct is required
#
export LIBGUESTFS_BACKEND=direct
