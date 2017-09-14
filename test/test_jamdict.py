#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script for testing jamdict library
Latest version can be found at https://github.com/neocl/jamdict

References:
    Python documentation:
        https://docs.python.org/
    Python unittest
        https://docs.python.org/3/library/unittest.html
    --
    argparse module:
        https://docs.python.org/3/howto/argparse.html
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2016, Le Tuan Anh <tuananh.ke@gmail.com>
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

import os
import logging
import unittest
from jamdict.jmdict import JMDictXMLParser
from jamdict.kanjidic2 import Kanjidic2XMLParser
from jamdict import Jamdict, JMDictXML

########################################################################

MINI_JMD = 'data/JMdict_mini.xml'
MINI_KD2 = 'data/kanjidic2.mini.xml'
MY_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA = os.path.join(MY_DIR, 'data')
TEST_DB = os.path.join(TEST_DATA, 'jamdict_test.db')


class TestJamdictXML(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if os.path.isfile(TEST_DB):
            os.unlink(TEST_DB)

    def test_jmdict_xml(self):
        print("Test JMDict - lookup from XML")
        parser = JMDictXMLParser()
        entries = parser.parse_file(MINI_JMD)
        jmd = JMDictXML(entries)
        self.assertTrue(jmd.lookup(u'おてんき'))

    def test_jmdict_fields(self):
        parser = JMDictXMLParser()
        entries = parser.parse_file(MINI_JMD)
        jmd = JMDictXML(entries)
        results = jmd.lookup(u'おてんき')
        print(results)

    def test_jmdict_json(self):
        print("Test JMDict - XML to JSON")
        # Load mini dict data
        jmd = JMDictXML.from_file(MINI_JMD)
        e = jmd[10]
        self.assertIsNotNone(e)
        self.assertTrue(e.to_json())
        self.assertTrue(jmd[-1].to_json())

    def test_kanjidic2_xml(self):
        print("Test KanjiDic2 XML")
        # test module read kanjidic XML
        parser = Kanjidic2XMLParser()
        kd2 = parser.parse_file(MINI_KD2)
        for c in kd2:
            self.assertIsNotNone(c)
            for g in c.rm_groups:
                self.assertIsNotNone(g)
                self.assertTrue(g.readings)
                self.assertTrue(g.meanings)

    def test_kanjidic2_json(self):
        print("Test KanjiDic2 XML to JSON")
        parser = Kanjidic2XMLParser()
        kd2 = parser.parse_file(MINI_KD2)
        for c in kd2:
            self.assertIsNotNone(c.to_json())

    def test_jamdict_xml(self):
        print("Test Jamdict search in XML files")
        jam = Jamdict(jmd_xml_file=MINI_JMD, kd2_xml_file=MINI_KD2)
        result = jam.lookup('おみやげ')
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(len(result.chars), 2)
        self.assertEqual({c.literal for c in result.chars}, {'土', '産'})

    def test_jamdict_import(self):
        jam = Jamdict(db_file=":memory:", jmd_xml_file=MINI_JMD, kd2_xml_file=MINI_KD2)
        jam.import_data()

    def test_jamdict_sqlite_all(self):
        jam = Jamdict(db_file=TEST_DB, jmd_xml_file=MINI_JMD, kd2_xml_file=MINI_KD2)
        result = jam.jmdict_xml.lookup('おみやげ')
        print(result)
        jam.import_data()
        # test lookup
        result = jam.lookup('おみやげ')
        print(result.entries)
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(len(result.chars), 2)
        self.assertEqual({c.literal for c in result.chars}, {'土', '産'})


########################################################################

if __name__ == "__main__":
    logging.getLogger('jamdict').setLevel(logging.DEBUG)
    unittest.main()
