#!/bin/bash

set +e  # not quit for failure command
set -x

# Stop existing redis server container if need (optional)
docker stop tdx-redis || true
while docker container inspect tdx-redis >/dev/null 2>&1; do sleep 1; done

# Start redis-server
docker run --rm -d --name tdx-redis redis
while true
do
   if docker ps -a --format '{{.Names}}' | grep -Eq "^tdx-redis\$"; then
      break
   fi
   sleep 1
done

# Get the container IP
REDIS_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' tdx-redis)
echo "Redis service is started at $REDIS_IP"

# Wait for redis-server completed work and ready
count=0
while true
do
   redis-cli -h "$REDIS_IP" ping
   ret=$?
   if [ $ret -eq 0 ]; then
      echo "Success start redis-server in docker."
      break
   else
      ((count++))
      if [[ $count -gt 10 ]]; then
         echo "Fail to run redis service after 10 seconds. ret: $ret"
         exit 1
      fi
      echo "redis-server is not ready yet, wait for more seconds..."
      sleep 1
   fi
done

# Run benchmark
/usr/bin/redis-benchmark -h "$REDIS_IP" "$@"
ret=$?
if [ $ret -eq 0 ];
then
    echo "Success to run redis service in docker and redis-benchmark"
else
    echo "Fail to run redis benchmark, ret: $ret"
fi

# Clean up
docker stop tdx-redis || true
exit $ret
