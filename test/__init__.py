# -*- coding: utf-8 -*-

''' Jamdict Test Scripts
Latest version can be found at https://github.com/neocl/jamdict/

:copyright: (c) 2016 Le Tuan Anh <tuananh.ke@gmail.com>
:license: MIT, see LICENSE for more details.
'''

# This source code is a part of jamdict library
# Copyright (c) 2016, Le Tuan Anh <tuananh.ke@gmail.com>
# LICENSE: The MIT License (MIT)
#
# Homepage: https://github.com/neocl/jamdict

import os
from chirptext.cli import setup_logging

TEST_DIR = os.path.dirname(__file__)
TEST_DATA = os.path.join(TEST_DIR, 'data')

setup_logging(os.path.join(TEST_DIR, 'logging.json'), os.path.join(TEST_DIR, 'logs'))
