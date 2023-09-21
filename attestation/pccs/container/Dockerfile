FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG PCCS_VERSION="1.18.100.1-jammy1"

RUN apt-get update && apt-get install -y wget gnupg ca-certificates curl

RUN wget https://download.01.org/intel-sgx/sgx-dcap/1.18/linux/distro/ubuntu22.04-server/sgx_debian_local_repo.tgz

RUN tar zxvf sgx_debian_local_repo.tgz && \
    rm -f sgx_debian_local_repo.tgz

RUN echo "deb [trusted=yes arch=amd64] file:/sgx_debian_local_repo jammy main" |\
    tee /etc/apt/sources.list.d/sgx_debian_local_repo.list

RUN mkdir -p /etc/apt/keyrings
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key |\
    gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" |\
    tee /etc/apt/sources.list.d/nodesource.list

# The postinst will check the directory for configuration
RUN mkdir /etc/init/

RUN apt-get update && apt-get install -y nodejs cracklib-runtime sgx-dcap-pccs=${PCCS_VERSION} sgx-pck-id-retrieval-tool=${PCCS_VERSION} && \
    rm -rf /var/lib/apt/lists/*

RUN cd /opt/intel/sgx-dcap-pccs/ && \
    npm config set engine-strict true && \
    npm install

RUN mkdir /opt/intel/sgx-dcap-pccs/ssl_key

ADD default.json /opt/intel/sgx-dcap-pccs/config/
ADD network_setting.conf /opt/intel/sgx-pck-id-retrieval-tool/
COPY ssl_key /opt/intel/sgx-dcap-pccs/ssl_key

WORKDIR /opt/intel/sgx-dcap-pccs/

EXPOSE 8081

CMD ["node", "pccs_server.js"]
