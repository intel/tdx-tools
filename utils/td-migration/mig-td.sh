#!/bin/bash
set -e

# Set distro related parameters according to distro
DISTRO=$(grep -w 'NAME' /etc/os-release)
if [[ "$DISTRO" =~ .*"Ubuntu".* ]]; then
    QEMU_EXEC="/usr/bin/qemu-system-x86_64"
else
    QEMU_EXEC="/usr/libexec/qemu-kvm"
fi

GUEST_CID=18
MIGTD="/usr/share/td-migration/migtd.bin"
MIGTD_TYPE=""

usage() {
    cat << EOM
Usage: $(basename "$0") [OPTION]...
  -m <migtd file>           MigTD file
  -t <src|dst>              Must set migtd type, src or dst
  -h                        Show this help
EOM
}

process_args() {
    while getopts "m:t:h" option; do
        case "${option}" in
            m) MIGTD=$OPTARG;;
            t) MIGTD_TYPE=$OPTARG;;
            h) usage
               exit 0
               ;;
            *)
               echo "Invalid option '-$OPTARG'"
               usage
               exit 1
               ;;
        esac
    done

    if [[ -z ${MIGTD_TYPE} ]]; then
        usage
        error "Must set MIGTD_TYPE -t [src|dst]"
    fi

    case ${MIGTD_TYPE} in
        "src")
            GUEST_CID=18
            ;;
        "dst")
            GUEST_CID=36
            ;;
        *)
            error "Invalid ${MIGTD_TYPE}, must be [src|dst]"
            ;;
    esac
}

error() {
    echo -e "\e[1;31mERROR: $*\e[0;0m"
    exit 1
}

launch_migTD() {
QEMU_CMD="${QEMU_EXEC} \
-accel kvm \
-M q35 \
-cpu host,host-phys-bits,-kvm-steal-time,pmu=off \
-smp 1,threads=1,sockets=1 \
-m 1G \
-object tdx-guest,id=tdx0,sept-ve-disable=off,debug=off,quote-generation-service=vsock:1:4050 \
-object memory-backend-memfd-private,id=ram1,size=1G \
-machine q35,memory-backend=ram1,confidential-guest-support=tdx0,kernel_irqchip=split \
-bios ${MIGTD} \
-device vhost-vsock-pci,id=vhost-vsock-pci1,guest-cid=${GUEST_CID},disable-legacy=on \
-name migtd-${MIGTD_TYPE},process=migtd-${MIGTD_TYPE},debug-threads=on \
-no-hpet \
-nographic -vga none -nic none \
-serial mon:stdio"

    eval "${QEMU_CMD}"
}

process_args "$@"
launch_migTD
