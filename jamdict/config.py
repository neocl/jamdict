# -*- coding: utf-8 -*-

"""
Jamdict configuration management
"""

# This code is a part of jamdict library: https://github.com/neocl/jamdict
# :copyright: (c) 2016 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
from pathlib import Path
import logging

from chirptext import AppConfig
from chirptext.chio import read_file, write_file

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

MY_DIR = os.path.dirname(__file__)
CONFIG_TEMPLATE = os.path.join(MY_DIR, 'data', 'config_template.json')
__jamdict_home = os.environ.get('JAMDICT_HOME', MY_DIR)
__app_config = AppConfig('jamdict', mode=AppConfig.JSON, working_dir=__jamdict_home)


def _get_config_manager():
    ''' Internal function for retrieving application config manager object
    Don't use this directly, use read_config() method instead
    '''
    return __app_config


def _ensure_config(config_path='~/.jamdict/config.json', mkdir=True):
    _path = Path(os.path.expanduser(config_path))
    # auto create config dir
    if mkdir:
        _path.parent.mkdir(exist_ok=True)
    if not _path.exists():
        default_config = read_file(CONFIG_TEMPLATE)
        logging.getLogger(__name__).warning(f"Jamdict configuration file could not be found. A new configuration file will be generated at {_path}")
        logging.getLogger(__name__).debug(f"Default config: {default_config}")
        write_file(_path, default_config)


def read_config(config_file=None, force_refresh=False, ensure_config=False):
    ''' Read jamdict configuration (jamdict home folder, database name, etc.) from config file.

    When no configuration is available, jamdict will default JAMDICT_HOME to ``~/.jamdict``

    This function should be called right after import statements (i.e. before jam = Jamdict())

    The "standard" locations for configuration file include but not limited to:
    ~/.jamdict/config.json
    ~/.config/jamdict/config.json
    ./data/jamdict.json
    ./jamdict.json
    ./data/.jamdict.json
    ./.jamdict.json
    
    :param config_file: Path to configuration file. When config_file is None, jamdict will try to guess the location of the file.
    :param force_refresh: Force to re-read configuration from file
    :param ensure_config: Create configuration file automatically if it does not exist
    '''
    if ensure_config and not config_file and not __app_config.locate_config():
        # [2021-04-15] data can be installed via PyPI
        # configuration file can be optional now
        # load config from default template
        _ensure_config()
    if force_refresh or not __app_config.config:
        if config_file and os.path.isfile(config_file):
            __app_config.load(config_file)
        else:
            __app_config.load(CONFIG_TEMPLATE)
    # read config
    config = __app_config.config
    return config


def home_dir():
    ''' Find JAMDICT_HOME folder.
    if there is an environment variable that points to an existing directory
    (e.g. export JAMDICT_HOME=/home/user/jamdict)
    that folder will be used instead of the configured in jamdict JSON config file
    '''
    _config = read_config()
    # [2020-06-01] Allow JAMDICT_HOME to be overridden by environment variables
    if 'JAMDICT_HOME' in os.environ:
        _env_jamdict_home = os.path.abspath(os.path.expanduser(os.environ['JAMDICT_HOME']))
        if os.path.isdir(_env_jamdict_home):
            logging.getLogger(__name__).debug("JAMDICT_HOME: {}".format(_env_jamdict_home))
            return _env_jamdict_home
    return _config.get('JAMDICT_HOME', __jamdict_home)


def data_dir():
    _config = read_config()
    _data_dir = _config.get('JAMDICT_DATA', '{JAMDICT_HOME}/data').format(JAMDICT_HOME=home_dir())
    return _data_dir


def get_file(file_key):
    ''' Get configured path by key '''
    _config = read_config()
    _data_dir = data_dir()
    _home = home_dir()
    _value = _config.get(file_key)
    return _value.format(JAMDICT_DATA=_data_dir, JAMDICT_HOME=_home) if _value else ''
