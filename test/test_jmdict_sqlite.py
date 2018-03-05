#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test script for JMDict SQLite
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

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2016, jamdict"
__license__ = "MIT"

########################################################################

import sys
import os
import unittest
import logging

from jamdict import Jamdict
from jamdict import JMDictXML
from jamdict import JMDictSQLite


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

    db = JMDictSQLite(TEST_DB)
    xdb = JMDictXML.from_file(MINI_DATA_FILE)
    ramdb = JMDictSQLite(RAM_DB)

    @classmethod
    def setUpClass(cls):
        if os.path.isfile(TEST_DB):
            logger.info("Removing previous database file at {}".format(TEST_DB))
            os.unlink(TEST_DB)

    def test_xml2sqlite(self):
        print("Test JMDict: XML to SQLite")
        try:
            self.db.insert_entries(self.xdb)
        except:
            logger.exception("Error happened while inserting entries")
            raise
            pass
        entries = self.db.Entry.select()
        self.assertEqual(len(entries), len(self.xdb))
        # test select entry by id
        e = self.db.get_entry(1001710)
        ejson = e.to_json()
        self.assertEqual(ejson['kanji'][0]['text'], 'お菓子')
        logger.debug(e.to_json())

    def test_xml2ramdb(self):
        print("Testing XML to RAM")
        noe = len(self.xdb)
        with self.ramdb.ds.open() as ctx:
            self.ramdb.insert_entries(self.xdb, ctx=ctx)
            self.assertEqual(len(self.ramdb.Entry.select(ctx=ctx)), noe)

    def test_import_function(self):
        print("Testing JMDict import function")
        jd = Jamdict(MINI_DATA_FILE, RAM_DB)
        jd.import_data()

    def test_search(self):
        print("Test searching JMDict SQLite")
        with self.ramdb.ds.open() as ctx:
            self.ramdb.insert_entries(self.xdb, ctx=ctx)
            entries = ctx.Entry.select()
            print(len(entries))
            # Search by kana
            es = self.ramdb.search('あの', ctx)
            self.assertEqual(len(es), 2)
            logger.info('あの: {}'.format('|'.join([str(x) for x in es])))
            # Search by kanji
            es = self.db.search('%子%', ctx)
            self.assertEqual(len(es), 4)
            logger.info('%子%: {}'.format('|'.join([str(x) for x in es])))


#-------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
