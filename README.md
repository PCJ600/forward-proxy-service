# forward-proxy-service

## How to build 
```
./build.sh [image_version]
```

## How to deploy
```
ctr -n k8s.io import [image]
kubectl create ns squid
kubectl create -f squid-*.yaml
```
