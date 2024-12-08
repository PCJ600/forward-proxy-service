#!/usr/bin/env python3

import hashlib
import sys
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/var/log/squid/auth.log', filemode='a')

def sha1_encrypt(username):
    combined = username + "squid"
    return hashlib.sha1(combined.encode('utf-8')).hexdigest()

def authenticate(username, password):
    encrypted_password = sha1_encrypt(username)
    return encrypted_password == password

if __name__ == '__main__':
    while True:
        line = sys.stdin.readline()
        auth = line.split()
        user, passwd = auth[0], auth[1]
        logging.debug("Auth user={}, pwd={}".format(user, passwd))
        if authenticate(user, passwd):
            sys.stdout.write('OK\n')
        else:
            sys.stdout.write('ERR\n')
        sys.stdout.flush()
