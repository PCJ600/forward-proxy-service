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

## Test

* forward proxy
* basic Auth
* whitelist ACL
* upstream proxy
* stunnel
* cache

* healthCheck, getConfig
* logrotate

```
curl -x localhost:3128 https://www.baidu.com
```

