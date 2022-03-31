#!/bin/bash

PACKAGE_ROOT="$PWD/build/centos-stream-8"

if [[ ! -d "${PACKAGE_ROOT}/${INPUT_PACKAGE}" ]]; then
    echo "Invalid package: ${INPUT_PACKAGE}"
    exit 1
fi

cd "${PACKAGE_ROOT}/${INPUT_PACKAGE}" && ./build.sh
