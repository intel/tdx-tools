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
TELNET_PORT=""
CPU_NUM=2
MEM_SIZE=8
TDX_ENABLE="true"
NETDEV_ID=mynet0
MAC_ADDR=""
MIG_HASH=""
MIG_ATTR="0x000007f900000001"
PRE_BINDING=false
SRC_VSOCK="/tmp/qmp-sock-src"
DST_VSOCK="/tmp/qmp-sock-dst"
TD_VSOCK=""


usage() {
    cat << EOM
Usage: $(basename "$0") [OPTION]...
  -i <guest image file>     Guest image file 
  -k <kernel file>          Kernel file
  -b [direct|grub]          Boot type, default is "direct" which requires kernel binary specified via "-k"
  -q [tdvmcall|vsock]       Support for TD quote using tdvmcall or vsock
  -r <root partition>       root partition for direct boot, default is /dev/vda1
  -t <src|dst>              Must set userTD type, src or dst
  -c [cpu number]           CPU number (should be > 0), default 2
  -m [memory size]          Memory size (should be > 0, in giga byte), default 8G
  -x [true|false]           Enable TDX, default true
  -e                        Telnet port
  -n                        netdev id
  -a                        MAC address
  -g                        Enable pre-binding. When it's enabled, mig_hash will be used for TD boot. The real binding will take place before pre-migration
  -v                        Value of MIG_HASH
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

is_valid_port() {
    local port_number=$1
    local is_valid=false
    if [[ $port_number =~ ^[0-9]+$ ]]; then
        if [[ "$port_number" -lt 65536 ]]; then
            is_valid=true
        fi
    fi
    echo $is_valid
}

process_args() {
    while getopts "i:k:b:q:r:t:c:m:x:e:n:a:v:z:gh" option; do
        case "${option}" in
            i) GUEST_IMG=$OPTARG;;
            k) KERNEL=$OPTARG;;
            b) BOOT_TYPE=$OPTARG;;
            q) QUOTE_TYPE=$OPTARG;;
            r) ROOT_PARTITION=$OPTARG;;
            t) TD_TYPE=$OPTARG;;
            c) CPU_NUM=$OPTARG;;
            m) MEM_SIZE=$OPTARG;;
            x) TDX_ENABLE=$OPTARG;;
            e) TELNET_PORT=$OPTARG;;
            n) NETDEV_ID=$OPTARG;;
            a) MAC_ADDR=$OPTARG;;
            v) MIG_HASH=$OPTARG;;
            z) MIG_ATTR=$OPTARG;;
            g) PRE_BINDING=true;;
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

    if [[ ${PRE_BINDING} == true ]]; then
        if [[ -z ${MIG_HASH} ]]; then
            usage
            error "Must set MIG_HASH -v <mig_hash>"
        fi
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

    if [[ -z $MAC_ADDR ]]; then
        MAC_ADDR=$(printf '00:60:2f:%02x:%02x:%02x\n' $((RANDOM%256)) $((RANDOM%256)) $((RANDOM%256)))
    fi

    case ${TDX_ENABLE} in
        "true") ;;
        "false") ;;
        *)
            error "Invalid TDX option \"$TDX_ENABLE\", must be [true|false]"
            ;;
    esac

    case ${TD_TYPE} in
        "src")
            if [[ -z ${TELNET_PORT} ]]; then
                TELNET_PORT=9088
            fi
            if [[ ${TDX_ENABLE} == "true" ]]; then
                GUEST_CID=3
                if [[ ${PRE_BINDING} == false ]]; then 
                    TARGET_PID=$(pgrep -n migtd-src)
                fi
                if [[ ${TD_VSOCK} == "" ]]; then
                    TD_VSOCK=${SRC_VSOCK}
                fi
            fi
            ;;
        "dst")
            if [[ -z ${TELNET_PORT} ]]; then
                TELNET_PORT=9089
            fi
            if [[ ${TDX_ENABLE} == "true" ]]; then
                GUEST_CID=4
                if [[ ${PRE_BINDING} == false ]]; then 
                    TARGET_PID=$(pgrep -n migtd-dst)
                fi
                if [[ ${TD_VSOCK} == "" ]]; then
                    TD_VSOCK=${DST_VSOCK}
                fi
            fi
            ;;
        *)
            error "Invalid ${TD_TYPE}, must be [src|dst]"
            ;;
    esac

    local telnet_port_valid
    telnet_port_valid=$(is_valid_port "${TELNET_PORT}")
    if [[ $telnet_port_valid != true ]]; then
        usage
        error "Port number should be 0 ~ 65535"
    fi

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

launch_vm() {

    PARAM_MACHINE="-machine q35,memory-backend=ram1,confidential-guest-support=tdx0,kernel_irqchip=split -object memory-backend-memfd-private,id=ram1,size=${MEM_SIZE}G "
    if [[ ${TDX_ENABLE} != "true" ]]; then
        PARAM_MACHINE="-machine q35,kernel_irqchip=split "
    fi

QEMU_CMD="${QEMU_EXEC} \
-accel kvm \
-cpu host,pmu=off,-kvm-steal-time,-shstk,tsc-freq=1000000000 \
-smp ${CPU_NUM},threads=1,sockets=1 \
-m ${MEM_SIZE}G \
${PARAM_MACHINE} \
-bios ${OVMF} \
-chardev stdio,id=mux,mux=on,logfile=lm-${TD_TYPE}.log \
-drive file=$(readlink -f "${GUEST_IMG}"),if=virtio,id=virtio-disk0,format=qcow2 \
-name process=lm-${TD_TYPE},debug-threads=on \
-no-hpet -nodefaults \
-D /run/qemu-${TD_TYPE}.log -nographic -vga none \
-monitor unix:${TD_VSOCK},server,nowait \
-monitor telnet:127.0.0.1:${TELNET_PORT},server,nowait \
-device virtio-serial,romfile= \
-device virtconsole,chardev=mux -serial chardev:mux -monitor chardev:mux \
-device virtio-net-pci,netdev=${NETDEV_ID},mac=${MAC_ADDR},romfile= \
-netdev bridge,id=${NETDEV_ID},br=virbr0"

    if [[ ${TDX_ENABLE} == "true" ]]; then
        QEMU_CMD+=" -object tdx-guest,id=tdx0,sept-ve-disable=on,debug=off"

        # If pre-binding is enabled, use mig_hash other than migtd_pid
        if [[ ${PRE_BINDING} == true ]]; then
            QEMU_CMD+=",migtd-hash=${MIG_HASH},migtd-attr=${MIG_ATTR}"
        else
            QEMU_CMD+=",migtd-pid=${TARGET_PID}"
        fi
        # Append get quote method for attestation
        if [[ -n ${QUOTE_TYPE} ]]; then
            if [[ ${QUOTE_TYPE} == "tdvmcall" ]]; then
                QEMU_CMD+=",quote-generation-service=vsock:2:4050"
            else
                QEMU_CMD+=" -device vhost-vsock-pci,guest-cid=${GUEST_CID}"
            fi
        fi
    fi

    if [[ ${BOOT_TYPE} == "direct" ]]; then
        QEMU_CMD+=" -kernel $(readlink -f "${KERNEL}")"
        QEMU_CMD+=" -append \"root=${ROOT_PARTITION} rw console=hvc0\" "
    fi

    if [[ ${TD_TYPE} == "dst" ]]; then
        QEMU_CMD+=" -incoming defer"
    fi

    eval "${QEMU_CMD}"
}

process_args "$@"
launch_vm
