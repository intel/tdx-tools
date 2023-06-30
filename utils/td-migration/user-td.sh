#!/bin/bash
set -e

# Set distro related parameters according to distro
DISTRO=$(grep -w 'NAME' /etc/os-release)
if [[ "$DISTRO" =~ .*"Ubuntu".* ]]; then
    QEMU_EXEC="/usr/bin/qemu-system-x86_64"
else
    QEMU_EXEC="/usr/libexec/qemu-kvm"
fi

TD_TYPE=""
KERNEL=""
GUEST_IMG=""
OVMF="/usr/share/qemu/OVMF.fd"
BOOT_TYPE="direct"
TARGET_PID=""
ROOT_PARTITION="/dev/vda1"
QUOTE_TYPE=""
GUEST_CID=3
TELNET_PORT=9088
INCOMING_PORT=6666
CPU_NUM=2
MEM_SIZE=8
MIG_HASH="d83d9a38c238ef3b7bc207bbea3287a8b37b37e731480a8d240d2a6953086c5ecbdf7ee4c72fec3a3e9d4a87f4f9b4fe"
PRE_BINDING=false


usage() {
    cat << EOM
Usage: $(basename "$0") [OPTION]...
  -i <guest image file>     Guest image file 
  -k <kernel file>          Kernel file
  -b [direct|grub]          Boot type, default is "direct" which requires kernel binary specified via "-k"
  -p                        incoming port
  -q [tdvmcall|vsock]       Support for TD quote using tdvmcall or vsock
  -r <root partition>       root partition for direct boot, default is /dev/vda1
  -t <src|dst>              Must set userTD type, src or dst
  -c [cpu number]           CPU number (should be > 0), default 2
  -m [memory size]          Memory size (should be > 0, in giga byte), default 8G
  -e                        Enable pre-binding. Whenit's enabled, mig_hash will be used for TD boot. The real binding will take place before pre-migration
  -h                        Show this help
EOM
}

is_positive_int() {
    local param=$1
    local is_positive=false
    if [[ $param =~ ^[0-9]+$ ]]; then
        if [[ $param -gt 0 ]]; then
            is_positive=true
	fi
    fi
    echo $is_positive
}

process_args() {
    while getopts "i:k:b:p:q:r:t:c:m:eh" option; do
        case "${option}" in
            i) GUEST_IMG=$OPTARG;;
            k) KERNEL=$OPTARG;;
            b) BOOT_TYPE=$OPTARG;;
            p) INCOMING_PORT=$OPTARG;;
            q) QUOTE_TYPE=$OPTARG;;
            r) ROOT_PARTITION=$OPTARG;;
            t) TD_TYPE=$OPTARG;;
            c) CPU_NUM=$OPTARG;;
            m) MEM_SIZE=$OPTARG;;
            e) PRE_BINDING=true;;
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

    if [[ -z ${TD_TYPE} ]]; then
        usage
        error "Must set TD_TYPE -t [src|dst]"
    fi

    local cpu_num_valid
    cpu_num_valid=$(is_positive_int "${CPU_NUM}")
    if [[ $cpu_num_valid != true ]]; then
        usage
	error "CPU number should be positive integer"
    fi

    local mem_size_valid
    mem_size_valid=$(is_positive_int "${MEM_SIZE}")
    if [[ $mem_size_valid != true ]]; then
        usage
	error "Memory size should be positive integer"
    fi

    case ${TD_TYPE} in
        "src")
            GUEST_CID=3
            TELNET_PORT=9088
            if [[ ${PRE_BINDING} == false ]]; then 
                TARGET_PID=$(pgrep -n migtd-src)
            fi
            ;;
        "dst")
            GUEST_CID=4
            TELNET_PORT=9089
            if [[ ${PRE_BINDING} == false ]]; then
                TARGET_PID=$(pgrep -n migtd-dst)
            fi
            ;;
        *)
            error "Invalid ${TD_TYPE}, must be [src|dst]"
            ;;
    esac

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

    if [[ -n ${QUOTE_TYPE} ]]; then
        case ${QUOTE_TYPE} in
            "tdvmcall") ;;
            "vsock");;
            *)
                error "Invalid quote type \"$QUOTE_TYPE\", must be [vsock|tdvmcall]"
                ;;
        esac
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
-smp ${CPU_NUM},threads=1,sockets=1 \
-m ${MEM_SIZE}G \
-object memory-backend-memfd-private,id=ram1,size=${MEM_SIZE}G \
-machine q35,memory-backend=ram1,confidential-guest-support=tdx0,kernel_irqchip=split \
-bios ${OVMF} \
-chardev stdio,id=mux,mux=on,logfile=lm-${TD_TYPE}.log \
-drive file=$(readlink -f "${GUEST_IMG}"),if=virtio,id=virtio-disk0,format=qcow2 \
-name process=lm-${TD_TYPE},debug-threads=on \
-no-hpet -nodefaults \
-D /run/qemu-${TD_TYPE}.log -nographic -vga none \
-monitor unix:/tmp/qmp-sock-${TD_TYPE},server,nowait \
-monitor telnet:127.0.0.1:${TELNET_PORT},server,nowait \
-device virtio-serial,romfile= \
-device virtconsole,chardev=mux -serial chardev:mux -monitor chardev:mux \
-device virtio-net-pci,netdev=mynet0,romfile= \
-netdev bridge,id=mynet0,br=virbr0"

    QEMU_CMD+=" -object tdx-guest,id=tdx0,sept-ve-disable=on,debug=off"

    if [[ ${PRE_BINDING} == true ]]; then
        QEMU_CMD+=",migtd-hash=${MIG_HASH}"
    else
        QEMU_CMD+=",migtd-pid=${TARGET_PID}"
    fi

    if [[ -n ${QUOTE_TYPE} ]]; then
        if [[ ${QUOTE_TYPE} == "tdvmcall" ]]; then
		    QEMU_CMD+=",quote-generation-service=vsock:2:4050"
        else
            QEMU_CMD+=" -device vhost-vsock-pci,guest-cid=${GUEST_CID}"
        fi
    fi

    if [[ ${BOOT_TYPE} == "direct" ]]; then
        QEMU_CMD+=" -kernel $(readlink -f "${KERNEL}")"
        QEMU_CMD+=" -append \"root=${ROOT_PARTITION} rw console=hvc0\" "
    fi

    if [[ ${TD_TYPE} == "dst" ]]; then
        QEMU_CMD+=" -incoming tcp:0:${INCOMING_PORT}"
    fi

    eval "${QEMU_CMD}"
}

process_args "$@"
launch_TDVM
