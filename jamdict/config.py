# -*- coding: utf-8 -*-

'''
Jamdict configuration management

Latest version can be found at https://github.com/neocl/jamdict

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# Copyright (c) 2016, Le Tuan Anh <tuananh.ke@gmail.com>
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

########################################################################

import os
import logging

from chirptext import AppConfig
from chirptext.io import read_file, write_file

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

MY_DIR = os.path.dirname(__file__)
CONFIG_TEMPLATE = os.path.join(MY_DIR, 'data', 'config_template.json')
__jamdict_home = os.environ.get('JAMDICT_HOME', MY_DIR)
__app_config = AppConfig('jamdict', mode=AppConfig.JSON, working_dir=__jamdict_home)


def getLogger():
    return logging.getLogger(__name__)


def _get_config_manager():
    ''' Internal function for retrieving application config manager object
    Don't use this directly, use read_config() method instead
    '''
    return __app_config


def read_config():
    if not __app_config.config and not __app_config.locate_config():
        # need to create a config
        config_dir = os.path.expanduser('~/.jamdict/')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        cfg_loc = os.path.join(config_dir, 'config.json')
        default_config = read_file(CONFIG_TEMPLATE)
        getLogger().warning("Jamdict configuration file could not be found. A new configuration file will be generated at {}".format(cfg_loc))
        getLogger().debug("Default config: {}".format(default_config))
        write_file(cfg_loc, default_config)
    # read config
    config = __app_config.config
    return config


def home_dir():
    _config = read_config()
    return _config.get('JAMDICT_HOME', '.')


def data_dir():
    _config = read_config()
    _data_dir = _config.get('JAMDICT_DATA', '{JAMDICT_HOME}/data').format(JAMDICT_HOME=home_dir())
    return _data_dir


def get_file(file_key):
    _config = read_config()
    _data_dir = data_dir()
    return _config.get(file_key).format(JAMDICT_DATA=_data_dir)
