#!/usr/bin/env python3

import subprocess
import traceback
import time
import threading
import copy
import os
import logging_config

from queue import Queue
from reload_squid import reload_squid_if_needed

# Global Variables
logger = logging_config.logger
g_agent = None

# Flask App
from flask import Flask, jsonify, Response
app = Flask(__name__)

@app.route('/healthz', methods=['GET'])
def health_check():
    retCode = 0
    try:
        result = subprocess.run(['/usr/sbin/squid', '-k', 'check'])
        if retCode == 0:
            return Response(status=200)
    except:
        logger.error("health_check exception, traceback: %r", traceback.format_exc())
        return Response(status=500)

    return Response(status=400) # Squid is not running


@app.route('/config', methods=['GET'])
def get_config():
    try:
        conf = g_agent.getConfigMap()
        return (jsonify({'config': conf}), 200)
    except:
        logger.error("get config exception, traceback: %r", traceback.format_exc())

    return Response(status=500)


def run_flask_app():
    app.run(host='0.0.0.0', port=5000)



class Agent():
    def __init__(self):
        self.configMap = {}
        self.configMapLock = threading.Lock()
        self.Q = {'config_change': Queue()}

    def getConfigMap(self):
        self.configMapLock.acquire()
        cfg = copy.deepcopy(self.configMap)
        self.configMapLock.release()
        return cfg

    # read config from ConfigMap Volume, then load it to memory
    def updateConfigMap(self):
        latest_conf = {}
        keys = ["whitelist", "whitelistFlag", "proxyHost", "proxyPort"]
        for k in keys:
            file_path = '/etc/squid-config/{}'.format(k)
            if os.path.exists(file_path) == False:
                latest_conf[k] = ""
                continue
            with open(file_path, "r") as f:
                latest_conf[k] = f.read()

        self.configMapLock.acquire()
        if self.configMap != latest_conf:
            self.Q['config_change'].put(1) # Notify config change
            self.configMap = latest_conf
        self.configMapLock.release()

    def update_config_task(self):
        while True:
            self.updateConfigMap()
            time.sleep(5)

    def process_config_change(self):
        while True:
            item = self.Q['config_change'].get()
            conf = self.getConfigMap()
            logger.info('receive config change message, lastest conf: %r', conf)

            reload_squid_if_needed(conf)

    def start(self):
        logger.info("Agent Started")
        flask_thread = threading.Thread(target=run_flask_app, name="flask", daemon=True)
        flask_thread.start()

        t1 = threading.Thread(target=self.update_config_task, name="update_cfg", daemon=True)
        t1.start()
        t2 = threading.Thread(target=self.process_config_change, name="process_cfg_change", daemon=True)
        t2.start()
        


if __name__ == '__main__':
    g_agent = Agent()
    g_agent.start()
    while True:
        time.sleep(10)

