#!/bin/bash

IMAGE_NAME=squid
IMAGE_TAG=$1
[ -z "$IMAGE_TAG" ] && { echo "please input image tag"; exit 1; }

docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -f Dockerfile .
docker save ${IMAGE_NAME}:${IMAGE_TAG} > ${IMAGE_NAME}-${IMAGE_TAG}.tar

# Docker测试
#cid=$(docker run -d --privileged=true --net=host --ulimit nofile=65535:65535 ${IMAGE_NAME}:${IMAGE_TAG})
#docker exec -it ${cid} /bin/bash
