from registry.access.redhat.com/ubi8/ubi:8.5

ARG buildreqs="bzip2 coreutils cpio diffutils \
               gcc gcc-c++ make patch python3 python3-pyyaml \
               python3-requests redhat-rpm-config \
               rpm-build unzip which git wget sudo"

RUN dnf -y --setopt="tsflags=nodocs" update --allowerasing && \
    dnf -y --setopt="tsflags=nodocs" install --allowerasing $buildreqs && \
    dnf clean all && rm -rf /var/cache/yum/

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
