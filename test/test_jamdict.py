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
__copyright__ = "Copyright 2016, jamdict"
__license__ = "MIT"

########################################################################

import os
import logging
import unittest
from jamdict import config
from jamdict.jmdict import JMDictXMLParser
from jamdict.kanjidic2 import Kanjidic2XMLParser
from jamdict import Jamdict, JMDictXML

########################################################################

MY_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA = os.path.join(MY_DIR, 'data')
MINI_JMD = os.path.join(TEST_DATA, 'JMdict_mini.xml')
MINI_KD2 = os.path.join(TEST_DATA, 'kanjidic2_mini.xml')
MINI_JMNE = os.path.join(TEST_DATA, 'jmendict_mini.xml')
TEST_DB = os.path.join(TEST_DATA, 'jamdict_test.db')


def getLogger():
    return logging.getLogger(__name__)


class TestConfig(unittest.TestCase):

    def test_config(self):
        cfg = config.read_config()
        self.assertIn('KD2_XML', cfg)
        self.assertTrue(config.get_file('KD2_XML'))
        getLogger().info("jamdict log file location: {}".format(config._get_config_manager().locate_config()))


class TestModels(unittest.TestCase):

    def test_basic_models(self):
        parser = JMDictXMLParser()
        entries = parser.parse_file(MINI_JMD)
        self.assertEqual(len(entries), 230)  # there are 230 test entries
        e = entries[0]
        self.assertEqual(len(e), 1)  # there is only 1 sense
        self.assertEqual(len(e[0].gloss), 1)  # there is only 1 sense
        # first sense in entry e to string -> with POS
        self.assertEqual(str(e[0]), 'repetition mark in katakana ((noun (common) (futsuumeishi)))')
        self.assertEqual(str(e[0].text()), 'repetition mark in katakana')  # compact is enabled by default
        self.assertEqual(str(e[0].gloss[0]), 'repetition mark in katakana')

    def test_lookup_result(self):
        jam = Jamdict(jmd_xml_file=MINI_JMD, kd2_xml_file=MINI_KD2, auto_config=False, auto_expand=False)
        result = jam.lookup('おみやげ')
        print(repr(result))
        self.assertTrue(result.entries)
        self.assertEqual(result.entries[0].kana_forms[0].text, 'おみやげ')
        # test lookup by ID
        res = jam.lookup('id#{}'.format(1002490))
        self.assertTrue(res.entries)
        self.assertEqual(res.entries[0].kana_forms[0].text, 'おとそ')


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
        jam = Jamdict(jmd_xml_file=MINI_JMD, kd2_xml_file=MINI_KD2, auto_config=False)
        result = jam.lookup('おみやげ')
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(len(result.chars), 2)
        self.assertEqual({c.literal for c in result.chars}, {'土', '産'})


class TestJamdictSQLite(unittest.TestCase):

    def test_jamdict_sqlite_all(self):
        if os.path.isfile(TEST_DB):
            os.unlink(TEST_DB)
        jam = Jamdict(db_file=TEST_DB, kd2_file=TEST_DB, jmnedict_file=TEST_DB, jmd_xml_file=MINI_JMD, kd2_xml_file=MINI_KD2, jmnedict_xml_file=MINI_JMNE)
        # Lookup using XML
        result = jam.jmdict_xml.lookup('おみやげ')
        getLogger().debug("Results: {}".format(result))
        # Lookup using SQLite
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
