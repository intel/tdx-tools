#!/bin/bash

#export env var
while read env_var; do
  export "$env_var"
done < /etc/environment

echo "============Install docker repo"
# install GPG key
install -m 0755 -d /etc/apt/keyrings
rm -f /etc/apt/keyrings/docker.gpg
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# install repo
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update

echo "============Install docker component"
# install docker components
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# config proxy
if [ -z $(cat /usr/lib/systemd/system/docker.service | grep HTTPS_PROXY)]; then
  HTTPS_PROXY=$(echo $HTTPS_PROXY)
  if [ -z $HTTPS_PROXY ]; then
    HTTPS_PROXY=$(echo $https_proxy)
  fi
  if [ ! -z $HTTPS_PROXY ];then 
    HTTPS_PROXY=$(echo $HTTPS_PROXY | sed 's/\//\\\//g')
    sed -i "s/\[Service\]/\[Service\]\nEnvironment=\"HTTPS_PROXY=$HTTPS_PROXY\"/g" /usr/lib/systemd/system/docker.service
  fi
fi

if [ -z $(cat /usr/lib/systemd/system/docker.service | grep HTTP_PROXY)]; then
  HTTP_PROXY=$(echo $HTTP_PROXY)
  if [ -z $HTTP_PROXY ]; then
    HTTP_PROXY=$(echo $http_proxy)
  fi
  if [ ! -z $HTTP_PROXY ];then 
    HTTP_PROXY=$(echo $HTTP_PROXY | sed 's/\//\\\//g')
    sed -i "s/\[Service\]/\[Service\]\nEnvironment=\"HTTP_PROXY=$HTTP_PROXY\"/g" /usr/lib/systemd/system/docker.service
  fi
fi

if [ -z $(cat /usr/lib/systemd/system/docker.service | grep NO_PROXY)]; then
  NO_PROXY=$(echo $NO_PROXY)
  if [ -z $NO_PROXY ]; then
    NO_PROXY=$(echo $no_proxy)
  fi
  if [ ! -z $NO_PROXY ];then 
    NO_PROXY=$(echo $NO_PROXY | sed 's/\//\\\//g')
    sed -i "s/\[Service\]/\[Service\]\nEnvironment=\"NO_PROXY=$NO_PROXY\"/g" /usr/lib/systemd/system/docker.service
  fi
fi

echo "============Pull container images"
# restart dockerd
systemctl daemon-reload
systemctl restart docker

# pull docker image
docker pull nginx:latest
docker pull redis:latest
docker pull intel/intel-optimized-tensorflow-avx512:2.8.0

