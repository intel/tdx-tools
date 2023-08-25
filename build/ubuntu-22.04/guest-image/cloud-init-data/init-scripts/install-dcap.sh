#!/bin/bash

#export env var
while read env_var; do
  export "$env_var"
done < /etc/environment

wget https://download.01.org/intel-sgx/sgx-dcap/1.17/linux/distro/ubuntu22.04-server/sgx_debian_local_repo.tgz
tar xvf sgx_debian_local_repo.tgz -C /srv

cat <<EOT >> /etc/apt/sources.list.d/sgx_debian_local_repo.list
deb [trusted=yes arch=amd64] file:/srv/sgx_debian_local_repo jammy main
EOT

apt update
apt install -y libtdx-attest libtdx-attest-dev