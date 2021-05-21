#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script for testing jamdict library
"""

# This code is a part of jamdict library: https://github.com/neocl/jamdict
# :copyright: (c) 2016 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import logging
import os
import unittest
from pathlib import Path

from jamdict import Jamdict, JMDictXML
from jamdict import config
from jamdict.jmdict import JMDictXMLParser
from jamdict.kanjidic2 import Kanjidic2XMLParser


MY_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
TEST_DATA = MY_DIR / 'data'
MINI_JMD = TEST_DATA / 'JMdict_mini.xml'
MINI_KD2 = TEST_DATA / 'kanjidic2_mini.xml'
MINI_JMNE = TEST_DATA / 'jmendict_mini.xml'
TEST_DB = TEST_DATA / 'jamdict_test.db'


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
        self.assertEqual(1, len(result.entries))
        self.assertEqual(2, len(result.chars))
        self.assertEqual({c.literal for c in result.chars}, {'土', '産'})


class TestConfig(unittest.TestCase):

    _cfg_dir = TEST_DATA / '.jamdict'
    _cfg_file = _cfg_dir / 'config.json'

    @classmethod
    def setUpClass(cls):
        cls.clean_config_file()

    @classmethod
    def tearDownClass(cls):
        cls.clean_config_file()

    @classmethod
    def clean_config_file(cls):
        if cls._cfg_file.exists():
            cls._cfg_file.unlink()
        if cls._cfg_dir.exists():
            cls._cfg_dir.rmdir()

    def test_config_file(self):
        # if configuration file doesn't exist
        conf = config.read_config(ensure_config=False, force_refresh=True)
        self.assertIsNotNone(conf)
        # and force creating config
        conf = config.read_config(ensure_config=True, force_refresh=True)
        self.assertIsNotNone(conf)

    def test_ensure_config(self):
        self.clean_config_file()
        self.assertFalse(self._cfg_file.is_file())
        conf = config._ensure_config(self._cfg_file)
        self.assertTrue(self._cfg_file.is_file())

    def test_home_dir(self):
        _orig_home = ''
        if 'JAMDICT_HOME' in os.environ:
            _orig_home = os.environ['JAMDICT_HOME']
        # set a new home
        os.environ['JAMDICT_HOME'] = str(self._cfg_dir)
        # home_dir exist ...
        if not self._cfg_dir.is_dir():
            self._cfg_dir.mkdir(parents=True)
        self.assertEqual(config.home_dir(), str(self._cfg_dir))
        # home_dir does not exist ...
        if self._cfg_dir.is_dir():
            self.clean_config_file()
        self.assertEqual(config.home_dir(), "~/.jamdict")
        # no environ
        del os.environ['JAMDICT_HOME']
        self.assertEqual(config.home_dir(), "~/.jamdict")
        os.environ['JAMDICT_HOME'] = _orig_home


class TestJamdictSQLite(unittest.TestCase):

    def test_jamdict_sqlite_all(self):
        if os.path.isfile(TEST_DB):
            os.unlink(TEST_DB)
        jam = Jamdict(db_file=TEST_DB, kd2_file=TEST_DB, jmnedict_file=TEST_DB,
                      jmd_xml_file=MINI_JMD, kd2_xml_file=MINI_KD2, jmnedict_xml_file=MINI_JMNE)
        # Lookup using XML
        result = jam.jmdict_xml.lookup('おみやげ')
        getLogger().debug("Results: {}".format(result))
        # Lookup using SQLite
        jam.import_data()
        # test lookup
        result = jam.lookup('おみやげ')
        self.assertIsNotNone(result.entries)
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(len(result.chars), 2)
        self.assertEqual({c.literal for c in result.chars}, {'土', '産'})

    def test_memory_mode(self):
        if not os.path.isfile(TEST_DB):
            jam = Jamdict(db_file=TEST_DB, kd2_file=TEST_DB, jmnedict_file=TEST_DB, jmd_xml_file=MINI_JMD, kd2_xml_file=MINI_KD2, jmnedict_xml_file=MINI_JMNE)
            jam.import_data()
        print("Test reading DB into RAM")
        ram_jam = Jamdict(TEST_DB, memory_mode=True)
        print("1st lookup")
        result = ram_jam.lookup('おみやげ')
        self.assertIsNotNone(result.entries)
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(len(result.chars), 2)
        self.assertEqual({c.literal for c in result.chars}, {'土', '産'})
        print("2nd lookup")
        result = ram_jam.lookup('おみやげ')
        self.assertIsNotNone(result.entries)
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(len(result.chars), 2)
        self.assertEqual({c.literal for c in result.chars}, {'土', '産'})
        print("3rd lookup")
        result = ram_jam.lookup('おみやげ')
        self.assertIsNotNone(result.entries)
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(2, len(result.chars))
        self.assertEqual({c.literal for c in result.chars}, {'土', '産'})


########################################################################

if __name__ == "__main__":
    unittest.main()
