#!/bin/bash

useradd -M -s /sbin/nologin squid
mkdir -p /var/log/squid
chown -R squid:squid /var/log/squid
squid

python3 /agent

while true ; do
    sleep 60
done
