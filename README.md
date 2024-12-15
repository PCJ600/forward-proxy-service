# forward-proxy-service

## How to build
```
./build.sh [image_version]
```

## How to deploy
```
#!/bin/bash
version=$1

if [ -z ${version} ]; then
    echo "warning: Input Image tag"
    exit 1
fi

tar -zxvf squid-${version}-deploy.tar.gz
cd output/
ctr -n k8s.io image import squid-${version}.tar

cd deploy/
kubectl -n squid delete cm squid-configmap
kubectl create -f squid-configmap.yaml

kubectl -n squid delete deploy squid
kubectl create -f squid-deployment.yaml

kubectl create -f squid-volume.yaml
if [ $? -ne 0 ]; then
    kubectl replace -f squid-volume.yaml
fi

watch kubectl get pods -A
```

## How to Test
* healthz, getconfig
```
curl localhost:5000/healthz -i
curl localhost:5000/config -i
```
* forward proxy
```
curl -x localhost:3128 https://www.baidu.com -i
```
* basic auth
Return 407 if basic auth not passed, otherwise return 200 OK
```
curl -x peter:47ae7e2352e92154c82669de2a99dd2091e60faa@192.168.52.200:3128 https://www.baidu.com -i
```
* whitelist ACL
Enable whitelistFlag, should return 403 if dst FQDN not in whitelist, otherwise return 200 OK
```
curl -x peter:47ae7e2352e92154c82669de2a99dd2091e60faa@192.168.52.200:3128 https://www.4399.com -i
curl -x peter:47ae7e2352e92154c82669de2a99dd2091e60faa@192.168.52.200:3128 https://www.baidu.com -i
```
* upstream proxy
```
```
* stunnel
* cache
