#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
JMDict in SQLite format
Latest version can be found at https://github.com/neocl/jamdict

References:
    Python documentation:
        https://docs.python.org/
    PEP 0008 - Style Guide for Python Code
        https://www.python.org/dev/peps/pep-0008/
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2017, Le Tuan Anh <tuananh.ke@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

__author__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2017, jamdict"
__license__ = "MIT"
__maintainer__ = "Le Tuan Anh"
__version__ = "0.1"
__status__ = "Prototype"
__credits__ = []

########################################################################

import sys
import os
import logging
import argparse
from collections import namedtuple

from puchikarui import Schema

#-------------------------------------------------------------------------------
# CONFIGURATION
#-------------------------------------------------------------------------------

MY_FOLDER = os.path.dirname(os.path.abspath(__file__))
SCRIPT_FOLDER = os.path.join(MY_FOLDER, 'scripts')
JMD_SETUP_SCRIPT = os.path.join(SCRIPT_FOLDER, 'setup.sql')


#-------------------------------------------------------------------------------
# MODELS
#-------------------------------------------------------------------------------

class JMDSchema(Schema):

    def __init__(self, data_source, setup_script=None, setup_file=None):
        Schema.__init__(self, data_source, setup_script=setup_script, setup_file=setup_file)
        self.add_table('Entry', ['idseq'])
        self.add_table('Link', ['id', 'idseq', 'tag', 'desc', 'uri'])
        self.add_table('Bib', ['id', 'idseq', 'tag', 'text'])
        self.add_table('Etym', ['idseq', 'text'])
        self.add_table('Audit', ['idseq', 'upd_date', 'upd_detl'])
        self.add_table('Kanji', ['id', 'idseq', 'text'])
        self.add_table('KJI', ['kid', 'text'])
        self.add_table('KJP', ['kid', 'text'])


class JMDSQLite(JMDSchema):

    def __init__(self, db_path):
        JMDSchema.__init__(self, db_path, setup_file=JMD_SETUP_SCRIPT)

    def insert(self, entry):
        ''' Insert an entry into DB '''
        
