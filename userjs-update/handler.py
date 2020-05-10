#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 10 May 2020 00:51
# @Author  : Hamish Shing Shing Chau
# @File    : handler.py
# @Software: PyCharm

import json
import os
import traceback

from flask import Flask, request

os.environ['TZ'] = 'UTC'

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return ''


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return 'Successfully used GET'
    else:
        try:
            update = subprocess.call("cd ~/Hamish-bot/userjs-update && python3 edit.py", shell=True)
            if update == 0:
                return jsonify({'status': 'Success'}), 200
            else:
                return jsonify({'status': 'Error'}), 503
        except Exception:
            system.log(traceback.format_exc())

        return 'OK'


if __name__ == "__main__":
    app.run()
