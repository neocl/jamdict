#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
jamdol - JAMDict OnLine (REST server)
Latest version can be found at https://github.com/neocl/jamdict

References:
    Python documentation:
        https://docs.python.org/
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2017, Le Tuan Anh <tuananh.ke@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2017, jamdict"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import json
import logging
import flask
from flask import Flask, Response
from functools import wraps
from flask import request

from chirptext.cli import setup_logging

from jamdict import Jamdict

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

setup_logging('logging.json', 'logs')
app = Flask(__name__, static_url_path="")
jmd = Jamdict()


def getLogger():
    return logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def jsonp(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        data = func(*args, **kwargs)
        callback = request.args.get('callback', False)
        if callback:
            content = "{}({})".format(callback, json.dumps(data))
            return Response(content, mimetype="application/javascript")
        else:
            content = json.dumps(data)
            return Response(content, mimetype="application/json")
    return decorated_function


# ---------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------

@app.route('/jamdol/entry/<idseq>', methods=['GET'])
@jsonp
def get_entry(idseq):
    results = {'entries': [jmd.get_entry(idseq).to_json()], 'chars': []}
    return results


@app.route('/jamdol/search/<query>', methods=['GET'])
@app.route('/jamdol/search/<strict>/<query>', methods=['GET'])
@jsonp
def search(query, strict=None):
    getLogger().info("Query = {}".format(query))
    results = jmd.lookup(query, strict_lookup=strict)
    return results.to_json()


@app.route('/jamdol/', methods=['GET'])
def index():
    return Response('jamdol {jd} - jamdol-flask/Flask-{fv}'.format(jd=__version__, fv=flask.__version__), mimetype='text/html')


@app.route('/jamdol/version', methods=['GET'])
@jsonp
def version():
    return {'product': 'jamdol',
            'version': __version__,
            'server': 'jamdol-flask/Flask-{}'.format(flask.__version__)}


# ---------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------

if __name__ == '__main__':
    app.run()
