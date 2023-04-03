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

connect() {
    modprobe vhost_vsock
    if [[ ${TYPE} == "local" ]]; then
        socat TCP4-LISTEN:9009,reuseaddr VSOCK-LISTEN:1235,fork &
        socat TCP4-CONNECT:127.0.0.1:9009,reuseaddr VSOCK-LISTEN:1234,fork &
    else
        ssh root@"${DEST_IP}" -o ConnectTimeout=30 "modprobe vhost_vsock; nohup socat TCP4-LISTEN:9009,reuseaddr VSOCK-LISTEN:1235,fork > foo.out 2> foo.err < /dev/null &"
        sleep 3
        socat TCP4-CONNECT:"${DEST_IP}":9009,reuseaddr VSOCK-LISTEN:1234,fork &
    fi
}

process_args "$@"
connect
