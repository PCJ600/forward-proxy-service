#!/usr/bin/env python3

# logging
import logging
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('/var/log/squid/agent.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

import subprocess
import traceback

# Flask
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/healthz', methods=['GET'])
def health_check():
    retCode = 0
    try:
        result = subprocess.run(['/usr/sbin/squid', '-k', 'check'])
        retCode = result.returncode
        if retCode == 0:
            return (jsonify({'code': 0, 'msg': 'OK'}), 200)
    except:
        logger.error("health_check %r", traceback.format_exc())
        return (jsonify({'code': -1, 'msg': 'Fail', 'msg': 'Service Unavailable'}), 500)

    return (jsonify({'code': retCode, 'msg': 'Fail'}), 400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
