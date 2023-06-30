#!/bin/bash
set -e

DEST_IP="localhost"
INCOMING_PORT=6666
POST_COPY=false
MULTI_STREAM=false
SRC_VSOCK="/tmp/qmp-sock-src"
DST_VSOCK="/tmp/qmp-sock-dst"


usage() {
    cat << EOM
Usage: $(basename "$0") [OPTION]...
  -i                        Destination platform ip, default is "localhost"
  -p                        incoming port
  -c                        Enable post-copy
  -m                        Enable multi streams
  -h                        Show this help
EOM
}

process_args() {
    while getopts "i:p:s:d:cmh" option; do
        case "${option}" in
            i) DEST_IP=$OPTARG;;
            p) INCOMING_PORT=$OPTARG;;
            c) POST_COPY=true;;
            m) MULTI_STREAM=true;;
            s) SRC_VSOCK=$OPTARG;;
            d) DST_VSOCK=$OPTARG;;
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
}

migrate() {
    # Currently it doesn't support to enable ,post-copy and multi-stream at the same time
    if [[ $POST_COPY == true && $MULTI_STREAM == true ]]; then
        echo "It doesn't support to enable post-copy and multi-thread at the same time!"
        exit 1
    fi

    # Set post copy parameters
    if [[ $POST_COPY == true ]]; then
        echo "migrate_set_capability postcopy-ram on" | nc -U "${SRC_VSOCK}" -w3
        echo "migrate_set_capability postcopy-ram on" | nc -U "${DST_VSOCK}" -w3
        echo "migrate_set_capability postcopy-preempt on" | nc -U "${SRC_VSOCK}" -w3
        echo "migrate_set_capability postcopy-preempt on" | nc -U "${DST_VSOCK}" -w3
    fi

    # Set multi stream parameters
    if [[ $MULTI_STREAM == true ]]; then
        echo "migrate_set_capability multifd on" | nc -U "${SRC_VSOCK}" -w3
        echo "migrate_set_parameter multifd-channels 4" | nc -U "${SRC_VSOCK}" -w3
        echo "migrate_set_capability multifd on" | nc -U "${DST_VSOCK}" -w3
        echo "migrate_set_parameter multifd-channels 4" | nc -U "${DST_VSOCK}" -w3

    fi

    echo "========================================="
    echo "POST COPY         : ${POST_COPY}"
    echo "Multi Stream      : ${MULTI_STREAM}"
    echo "Incoming port     : ${INCOMING_PORT}"
    echo "Dest host IP      : ${DEST_IP}"
    echo "========================================="

    # Trigger migration
    echo "migrate_set_parameter max-bandwidth 100G" | nc -U "${SRC_VSOCK}" -w3
    echo "migrate -d tcp:${DEST_IP}:${INCOMING_PORT}" | nc -U "${SRC_VSOCK}" -w3

    # Trigger post copy if it's enabled
    if [[ $POST_COPY == true ]]; then
        sleep 5
        echo "migrate_start_postcopy" | nc -U "${SRC_VSOCK}" -w3
    fi
}

process_args "$@"
migrate
