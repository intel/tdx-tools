#!/bin/bash
set -e

DEST_IP="localhost"
INCOMING_PORT=6666
POST_COPY=false
MULTI_STREAM=false
MULTI_CHANNEL=4
SRC_VSOCK="/tmp/qmp-sock-src"
DST_VSOCK="/tmp/qmp-sock-dst"


usage() {
    cat << EOM
Usage: $(basename "$0") [OPTION]...
  -i                        Destination platform ip, default is "localhost"
  -p                        incoming port
  -c                        Enable post-copy
  -m                        Enabled multi-stream
  -n                        Multifd-channel number
  -s                        Source TD vsock file, default value is "/tmp/qmp-sock-src"
  -d                        Destination vsock file, default value is "/tmp/qmp-sock-dst"
  -h                        Show this help
EOM
}

process_args() {
    while getopts "i:p:s:d:n:mch" option; do
        case "${option}" in
            i) DEST_IP=$OPTARG;;
            p) INCOMING_PORT=$OPTARG;;
            n) MULTI_CHANNEL=$OPTARG;;
            s) SRC_VSOCK=$OPTARG;;
            d) DST_VSOCK=$OPTARG;;
            m) MULTI_STREAM=true;;
            c) POST_COPY=true;;
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

    # multi stream number should be 1-255
    if ! [[ ${MULTI_STREAM} == true ]]; then
        if ! [[ ${MULTI_CHANNEL} =~ ^[0-9]+$ && ${MULTI_CHANNEL} -gt 0 && ${MULTI_CHANNEL} -lt 256 ]]; then
            echo "Invalid number of multifd_channel: ${MULTI_CHANNEL}. It should be a integer from 1 to 255"
            exit 1
        fi
    fi

    # Currently it doesn't support to enable ,post-copy and multi-stream at the same time
    if [[ $POST_COPY == true && $MULTI_STREAM == true ]]; then
        echo "It doesn't support to enable post-copy and multi-thread at the same time!"
        exit 1
    fi
}

migrate() {
    # Set post copy parameters
    if [[ $POST_COPY == true ]]; then
        echo "migrate_set_capability postcopy-ram on" | nc -U "${SRC_VSOCK}" -w3
        echo "migrate_set_capability postcopy-preempt on" | nc -U "${SRC_VSOCK}" -w3
        if [[ ${DEST_IP} == "localhost" ]]; then
            echo "migrate_set_capability postcopy-ram on" | nc -U "${DST_VSOCK}" -w3
            echo "migrate_set_capability postcopy-preempt on" | nc -U "${DST_VSOCK}" -w3
        else 
            ssh root@"${DEST_IP}" -o ConnectTimeout=30 "echo migrate_set_capability postcopy-ram on | nc -U ${DST_VSOCK} -w3"
            ssh root@"${DEST_IP}" -o ConnectTimeout=30 "echo migrate_set_capability postcopy-preempt on | nc -U ${DST_VSOCK} -w3"
        fi
    fi

    # Set multi stream parameters
    if [[ $MULTI_STREAM == true ]]; then
        echo "migrate_set_capability multifd on" | nc -U "${SRC_VSOCK}" -w3
        echo "migrate_set_parameter multifd-channels $MULTI_CHANNEL" | nc -U "${SRC_VSOCK}" -w3
        if [[ ${DEST_IP} == "localhost" ]]; then
            echo "migrate_set_capability multifd on" | nc -U "${DST_VSOCK}" -w3
            echo "migrate_set_parameter multifd-channels $MULTI_CHANNEL" | nc -U "${DST_VSOCK}" -w3
        else 
            ssh root@"${DEST_IP}" -o ConnectTimeout=30 "echo migrate_set_capability multifd on | nc -U ${DST_VSOCK} -w3"
            ssh root@"${DEST_IP}" -o ConnectTimeout=30 "echo migrate_set_capability multifd-channels on | nc -U ${DST_VSOCK} -w3"
        fi
    fi

    echo "========================================="
    echo "POST COPY         : ${POST_COPY}"
    echo "Multi Stream      : ${MULTI_STREAM}"
    echo "Multifd_channel   : ${MULTI_CHANNEL}"
    echo "Incoming port     : ${INCOMING_PORT}"
    echo "Dest host IP      : ${DEST_IP}"
    echo "========================================="

    # Trigger migration
    echo "migrate_set_parameter max-bandwidth 100G" | nc -U /tmp/qmp-sock-src -w3
    if [[ ${DEST_IP} == "localhost" ]]; then
        echo "migrate_incoming tcp:${DEST_IP}:${INCOMING_PORT}" | nc -U "${DST_VSOCK}" -w3
    else 
        ssh root@"${DEST_IP}" -o ConnectTimeout=30 "echo migrate_incoming tcp:${DEST_IP}:${INCOMING_PORT} | nc -U ${DST_VSOCK} -w3"
    fi
    sleep 3
    echo "migrate -d tcp:${DEST_IP}:${INCOMING_PORT}" | nc -U /tmp/qmp-sock-src -w3

    # Trigger post copy if it's enabled
    if [[ $POST_COPY == true ]]; then
        sleep 5
        echo "migrate_start_postcopy" | nc -U "${SRC_VSOCK}" -w3
    fi
}

process_args "$@"
migrate
