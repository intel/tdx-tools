FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG QGS_VERSION="1.18.100.1-jammy1"

RUN apt-get update && apt-get install -y wget gnupg ca-certificates curl

RUN wget https://download.01.org/intel-sgx/sgx-dcap/1.18/linux/distro/ubuntu22.04-server/sgx_debian_local_repo.tgz

RUN tar zxvf sgx_debian_local_repo.tgz && \
    rm -f sgx_debian_local_repo.tgz

RUN echo "deb [trusted=yes arch=amd64] file:/sgx_debian_local_repo jammy main" |\
    tee /etc/apt/sources.list.d/sgx_debian_local_repo.list

RUN apt-get update && apt-get install -y tdx-qgs=${QGS_VERSION} libsgx-enclave-common-dev libsgx-dcap-default-qpl sgx-ra-service && \
    rm -rf /var/lib/apt/lists/*

ADD sgx_default_qcnl.conf /etc/
CMD ["/opt/intel/tdx-qgs/qgs", "--no-daemon"]
