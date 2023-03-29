#!/bin/bash
set -e

# Set distro related parameters according to distro
DISTRO=$(grep -w 'NAME' /etc/os-release)
if [[ "$DISTRO" =~ .*"Ubuntu".* ]]; then
    QEMU_EXEC="/usr/bin/qemu-system-x86_64"
else
    QEMU_EXEC="/usr/libexec/qemu-kvm"
fi
KERNEL=""
GUEST_IMG=""
OVMF="/usr/share/qemu/OVMF.fd"
LOG="lm-dst.log"
BOOT_TYPE="direct"
TARGET_PID=$(pgrep migtd-dst)
ROOT_PARTITION="/dev/vda1"
INCOMING_PORT=6666

usage() {
    cat << EOM
Usage: $(basename "$0") [OPTION]...
  -i <guest image file>     Guest image file 
  -k <kernel file>          Kernel file
  -b [direct|grub]          Boot type, default is "direct" which requires kernel binary specified via "-k"
  -r <root partition>       root partition for direct boot, default is /dev/vda1
  -p                        incoming port
  -h                        Show this help
EOM
}

process_args() {
    while getopts "i:k:b:r:p:h" option; do
        case "${option}" in
            i) GUEST_IMG=$OPTARG;;
            k) KERNEL=$OPTARG;;
            b) BOOT_TYPE=$OPTARG;;
            r) ROOT_PARTITION=$OPTARG;;
            p) INCOMING_PORT=$OPTARG;;
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

    case ${BOOT_TYPE} in
        "direct")
            if [[ ! -f ${KERNEL} ]]; then
                usage
                error "Kernel image file ${KERNEL} not exist. Please specify via option \"-k\""
            fi
            ;;
        "grub")
            ;;
        *)
            echo "Invalid ${BOOT_TYPE}, must be [direct|grub]"
            exit 1
            ;;
    esac

    if [[ ! -f ${GUEST_IMG} ]]; then
        usage
        error "Guest image file ${GUEST_IMG} not exist. Please specify via option \"-i\""
    fi

    if [[ ! -f ${QEMU_EXEC} ]]; then
        error "Please install QEMU which supports TDX."
    fi

    if [[ ! -f ${OVMF} ]]; then
        error "Could not find OVMF, please install first"
    fi
}

error() {
    echo -e "\e[1;31mERROR: $*\e[0;0m"
    exit 1
}

launch_TDVM() {
    QEMU_CMD="${QEMU_EXEC} \
        -accel kvm \
        -cpu host,pmu=off,-kvm-steal-time,-shstk,tsc-freq=1000000000 \
        -smp 4,threads=1,sockets=1 \
        -m 16G \
        -object tdx-guest,id=tdx0,sept-ve-disable=on,debug=off,migtd-pid=${TARGET_PID} \
        -object memory-backend-memfd-private,id=ram1,size=16G \
        -machine q35,memory-backend=ram1,confidential-guest-support=tdx0,kernel_irqchip=split \
        -bios ${OVMF} \
        -chardev stdio,id=mux,mux=on,logfile=${LOG} \
        -drive file=$(readlink -f "${GUEST_IMG}"),if=virtio,id=virtio-disk0,format=qcow2 \
        -name process=lm-dst,debug-threads=on \
        -no-hpet -nodefaults \
        -D /run/qemu-dst.log -nographic -vga none \
        -monitor unix:/tmp/qmp-sock-dst,server,nowait \
        -device virtio-serial,romfile= \
        -device virtconsole,chardev=mux -serial chardev:mux -monitor chardev:mux \
        -device virtio-net-pci,netdev=mynet0,mac=00:16:3E:68:00:10,romfile= \
        -netdev bridge,id=mynet0,br=virbr0 \
        -incoming tcp:0:${INCOMING_PORT}"

    if [[ ${BOOT_TYPE} == "direct" ]]; then
        QEMU_CMD+=" -kernel $(readlink -f "${KERNEL}")"
        QEMU_CMD+=" -append \"root=${ROOT_PARTITION} rw console=hvc0\" "
    fi

    eval "${QEMU_CMD}"
}

process_args "$@"
launch_TDVM
