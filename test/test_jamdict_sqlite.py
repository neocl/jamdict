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

import sys
import os
import unittest
import logging

from jamdict import JMDict
from jamdict import JMDictXML
from jamdict import JMDSQLite


#-------------------------------------------------------------------------------
# CONFIGURATION
#-------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(TEST_DIR, 'data')
if not os.path.isdir(TEST_DATA):
    os.makedirs(TEST_DATA)
TEST_DB = os.path.join(TEST_DATA, 'test.db')
RAM_DB = ':memory:'
MINI_DATA_FILE = 'data/JMdict_mini.xml'


#-------------------------------------------------------------------------------
# DATA STRUCTURES
#-------------------------------------------------------------------------------

class TestJamdictSQLite(unittest.TestCase):

    db = JMDSQLite(TEST_DB)
    xdb = JMDictXML.fromfile(MINI_DATA_FILE)
    ramdb = JMDSQLite(RAM_DB)

    def test_xml2sqlite(self):
        try:
            self.db.insert(*self.xdb)
        except:
            pass
        entries = self.db.Entry.select()
        self.assertEqual(len(entries), len(self.xdb))

    def test_xml2ramdb(self):
        noe = len(self.xdb)
        with self.ramdb.ds.open() as ctx:
            self.ramdb.insert(*self.xdb, context=ctx)
            self.assertEqual(len(self.ramdb.Entry.select(ctx=ctx)), noe)

    def test_import_function(self):
        jd = JMDict(MINI_DATA_FILE, RAM_DB)
        jd.import_data()

    def test_search(self):
        self.test_xml2sqlite()
        # Search by kana
        es = self.db.search('あの')
        self.assertEqual(len(es), 2)
        logger.info('あの: {}'.format('|'.join([str(x) for x in es])))
        # Search by kanji
        es = self.db.search('%子%')
        self.assertEqual(len(es), 4)
        logger.info('%子%: {}'.format('|'.join([str(x) for x in es])))

    def test_select_entry(self):
        e = self.db.get_entry(1001710)
        logger.info(e.to_json())
        pass


#-------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
