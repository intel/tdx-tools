#!/bin/bash

# 0. export env var
while read env_var; do
  export "$env_var"
done < /etc/environment

echo "============Starting download go1.20.7.linux-amd64.tar.gz"
# download go
if [ -f /root/go1.20.7.linux-amd64.tar.gz ]; then
    rm /root/go1.20.7.linux-amd64.tar.gz
fi
wget -P /root https://go.dev/dl/go1.20.7.linux-amd64.tar.gz

echo "============Starting install go1.20.7.linux-amd64.tar.gz"
# uninstall old version
if [ -d /usr/local/go ]; then
    rm -rf /usr/local/go
fi

# install new version
tar -C /usr/local -xzf /root/go1.20.7.linux-amd64.tar.gz
echo "export PATH=$PATH:/usr/local/go/bin" >> /etc/profile
rm /root/go1.20.7.linux-amd64.tar.gz