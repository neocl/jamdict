#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test script for jamdict_sqlite
Latest version can be found at https://github.com/neocl/jamdict

References:
    Python unittest documentation:
        https://docs.python.org/3/library/unittest.html
    Python documentation:
        https://docs.python.org/
    PEP 0008 - Style Guide for Python Code
        https://www.python.org/dev/peps/pep-0008/
    PEP 0257 - Python Docstring Conventions:
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

import os
import unittest

from jamdict import JMDict
from jamdict import JMDSQLite


#-------------------------------------------------------------------------------
# CONFIGURATION
#-------------------------------------------------------------------------------

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
# TEST_DB = os.path.join(TEST_DIR, 'data', 'test.db')
TEST_DB = ':memory:'
MINI_DATA_FILE = 'data/JMdict_mini.xml'


#-------------------------------------------------------------------------------
# DATA STRUCTURES
#-------------------------------------------------------------------------------

class TestJamdictSQLite(unittest.TestCase):

    db = JMDSQLite(TEST_DB)

    def test_jamdict_sqlite(self):
        entries = self.db.Entry.select()
        print(len(entries))

    def test_xml2sqlite(self):
        entries = JMDict.fromfile(MINI_DATA_FILE)
        print(len(entries))
        for entry in entries:
            self.db.insert(entry)


#-------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
