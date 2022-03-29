from quay.io/centos/centos:stream8

ARG buildreqs="bzip2 coreutils cpio diffutils \
               gcc gcc-c++ make patch python3 python3-pyyaml \
               python3-requests redhat-rpm-config \
               rpm-build unzip which git wget sudo"

COPY aliyun.repo /etc/yum.repos.d/

RUN dnf -y --setopt="tsflags=nodocs" update --nobest --allowerasing && \
    dnf -y --setopt="tsflags=nodocs" install --allowerasing $buildreqs && \
    dnf clean all && rm -rf /var/cache/yum/

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
