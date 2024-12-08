#!/usr/bin/env python3

import hashlib

user="peter"
key=user+"squid"

key = key.encode('utf-8')
pwd = hashlib.sha1(key).hexdigest()
print("user:", user, " passwd:", pwd)
