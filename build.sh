#!/usr/bin/env bash
set -euo pipefail

_shutdown() {
  echo ""
  echo "SHUTDOWN - please wait"

  docker-compose --ansi never stop --timeout 0 || true

  wait

  exit 0
}

trap _shutdown INT TERM ERR
export DOCKER_DEFAULT_PLATFORM=linux/amd64

# otherwise multiple networks with the same name will appear when docker-compose is launched in parallel
docker network create tdx-tools_default || true

docker-compose --ansi never build centos-stream-8-pkg-builder

if [ "${1:-}" = "" ]; then
  packages="intel-mvp-spr-qemu-kvm intel-mvp-tdx-libvirt intel-mvp-spr-kernel intel-mvp-tdx-tdvf intel-mvp-tdx-guest-grub2 intel-mvp-tdx-guest-shim"
else
  packages=$*
fi

declare -A pids
for package in $packages; do
  echo "redirecting $package build output to /tmp/$package.log"
  (
    >/dev/null 2>&1 docker rm -f "centos-stream-8-$package" || true

    start=$SECONDS
    >"/tmp/$package.log" 2>&1 docker-compose --ansi never run --name "centos-stream-8-$package" -e INPUT_PACKAGE="$package" centos-stream-8-pkg-builder
    touch "build/centos-stream-8/$package/build.done"
    echo "$package build completed in $((SECONDS-start))s"
  ) &
  pids[$package]=$!
done

declare -A statuses
for package in "${!pids[@]}"; do
  pid=${pids[$package]}
  set +e
    wait $pid
    code=$?
  set -e
  if [ "$code" = "0" ]; then
    statuses[$package]=ok
  else
    statuses[$package]=fail
  fi
done

failed=no
for package in "${!statuses[@]}"; do
  status=${statuses[$package]}
  echo "$package logs in /tmp/$package.log: $status"
  if [ "$status" = "fail" ]; then
    failed=yes
  fi
done

if [ "$failed" = "yes" ]; then
  echo ""
  echo "FAIL"
  exit 1
fi

docker-compose --ansi never run \
  --workdir /workspace/build/centos-stream-8 \
  --entrypoint /workspace/build/centos-stream-8/build-repo.sh \
  centos-stream-8-pkg-builder

echo "generated repo in build/centos-stream-8/repo"

echo ""
echo "OK"
