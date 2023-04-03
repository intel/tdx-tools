#!/bin/bash
set -e

TYPE="local"
DEST_IP=""

usage() {
    cat << EOM
Usage: $(basename "$0") [OPTION]...
  -i <dest ip>              Destination platform ip address
  -t <local|remote>         Use single or cross host live migration
  -h                        Show this help
EOM
}

process_args() {
    while getopts "i:t:h" option; do
        case "${option}" in
            i) DEST_IP=$OPTARG;;
            t) TYPE=$OPTARG;;
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

    case ${TYPE} in
        "local");;
        "remote")
            if [[ -z ${DEST_IP} ]]; then
                error "Please use -i specify DEST_IP in remote type"
            fi
            ;;
        *)
            error "Invalid ${TYPE}, must be [local|remote]"
            ;;
    esac
}

error() {
    echo -e "\e[1;31mERROR: $*\e[0;0m"
    exit 1
}

pre_mig(){
    # Asking migtd-dst to connect to the dst socat
    if [[ ${TYPE} == "local" ]]; then
        echo "qom-set /objects/tdx0/ vsockport 1235" | nc -U /tmp/qmp-sock-dst
    else 
       ssh root@"${DEST_IP}" -o ConnectTimeout=30 "echo qom-set /objects/tdx0/ vsockport 1235 | nc -U /tmp/qmp-sock-dst"
    fi

    # Asking migtd-dst to connect to the src socat
    echo "qom-set /objects/tdx0/ vsockport 1234" | nc -U /tmp/qmp-sock-src
}

process_args "$@"
pre_mig