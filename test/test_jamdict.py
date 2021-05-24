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
from jamdict.jmdict import JMDictXMLParser, JMDEntry
from jamdict.kanjidic2 import Kanjidic2XMLParser
from jamdict.util import _JAMDICT_DATA_AVAILABLE


MY_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
TEST_DATA = MY_DIR / 'data'
MINI_JMD = TEST_DATA / 'JMdict_mini.xml'
MINI_KD2 = TEST_DATA / 'kanjidic2_mini.xml'
MINI_JMNE = TEST_DATA / 'jmendict_mini.xml'
TEST_DB = TEST_DATA / 'jamdict_test.db'


def getLogger():
    return logging.getLogger(__name__)


def all_kana(result, forms=None):
    if forms is None:
        forms = set()
    for e in result.entries:
        forms.update(f.text for f in e.kana_forms)
    return forms


def all_kanji(result, forms=None):
    if forms is None:
        forms = set()
    for e in result.entries:
        forms.update(f.text for f in e.kanji_forms)
    return forms


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
        self.assertTrue(results)
        self.assertIsInstance(results[0], JMDEntry)

    def test_jmdict_json(self):
        print("Test JMDict - XML to JSON")
        # Load mini dict data
        jmd = JMDictXML.from_file(MINI_JMD)
        e = jmd[10]
        self.assertIsNotNone(e)
        self.assertTrue(e.to_dict())
        self.assertTrue(jmd[-1].to_dict())

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
            self.assertIsNotNone(c.to_dict())

    def test_jamdict_xml(self):
        print("Test Jamdict search in XML files")
        jam = Jamdict(":memory:", jmd_xml_file=MINI_JMD,
                      kd2_xml_file=MINI_KD2,
                      jmnedict_xml_file=MINI_JMNE, auto_config=True)
        jam.import_data()
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


class TestAPIWarning(unittest.TestCase):

    def test_warn_to_json_deprecated(self):
        print("Test Jamdict search in XML files")
        jam = Jamdict(":memory:", jmd_xml_file=MINI_JMD,
                      kd2_xml_file=MINI_KD2,
                      jmnedict_xml_file=MINI_JMNE)
        jam.import_data()
        with self.assertWarns(DeprecationWarning):
            r = jam.lookup("おみやげ")
            self.assertTrue(r.to_json())
        with self.assertWarns(DeprecationWarning):
            r2 = jam.lookup("シェンロン")
            self.assertTrue(r2.to_json())


class TestJamdictSQLite(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(TEST_DB):
            os.unlink(TEST_DB)

    def test_search_by_pos(self):
        print("Test Jamdict search in XML files")
        jam = Jamdict(":memory:", jmd_xml_file=MINI_JMD,
                      kd2_xml_file=MINI_KD2,
                      jmnedict_xml_file=MINI_JMNE, auto_config=True)
        jam.import_data()
        # test get all pos
        poses = jam.all_pos()
        expected = {'Godan verb - -aru special class',
                    "Godan verb with `ku' ending",
                    "Godan verb with `ru' ending",
                    "Godan verb with `su' ending",
                    "Godan verb with `u' ending",
                    'Ichidan verb',
                    'adjectival nouns or quasi-adjectives (keiyodoshi)',
                    'adjective (keiyoushi)',
                    'adverb (fukushi)',
                    "adverb taking the `to' particle",
                    'auxiliary verb',
                    'conjunction',
                    'expressions (phrases, clauses, etc.)',
                    'interjection (kandoushi)',
                    'intransitive verb',
                    'noun (common) (futsuumeishi)',
                    'noun or participle which takes the aux. verb suru',
                    'noun or verb acting prenominally',
                    "nouns which may take the genitive case particle `no'",
                    'pre-noun adjectival (rentaishi)',
                    'pronoun',
                    'transitive verb'}
        self.assertEqual(expected, set(poses))
        result = jam.lookup('おみやげ', pos=['noun (common) (futsuumeishi)'])
        self.assertEqual(1, len(result.entries))
        with self.assertLogs('jamdict.jmdict_sqlite', level="WARNING") as cm:
            result = jam.lookup('おみやげ', pos='noun (common) (futsuumeishi)')
            self.assertEqual(1, len(result.entries))
            warned_pos_as_str = False
            for line in cm.output:
                if "POS filter should be a collection, not a string" in line:
                    warned_pos_as_str = True
                    break
            self.assertTrue(warned_pos_as_str)
        result = jam.lookup('おみやげ', pos=['intransitive verb'])
        self.assertFalse(result.entries)
        result = jam.lookup('おみやげ', pos=['intransitive verb', 'noun (common) (futsuumeishi)'])
        self.assertTrue(result.entries)

    def test_search_by_ne_type(self):
        print("Test Jamdict search in XML files")
        jam = Jamdict(":memory:", jmd_xml_file=MINI_JMD,
                      kd2_xml_file=MINI_KD2,
                      jmnedict_xml_file=MINI_JMNE, auto_config=True)
        jam.import_data()
        netypes = jam.all_ne_type()
        expected = ['company', 'fem', 'given', 'organization', 'person', 'place', 'surname', 'unclass']
        self.assertEqual(expected, netypes)
        res = jam.lookup("place")
        actual = set()
        for n in res.names:
            actual.update(k.text for k in n.kanji_forms)
        self.assertIn("厦門", actual)
        res = jam.lookup("company")
        actual = set()
        for n in res.names:
            actual.update(k.text for k in n.kanji_forms)
        expected = {'埼銀', 'ＩＫＥＡ'}
        self.assertTrue(expected.issubset(actual))

    def test_find_all_verbs(self):
        jam = Jamdict(":memory:", jmd_xml_file=MINI_JMD,
                      kd2_xml_file=MINI_KD2,
                      jmnedict_xml_file=MINI_JMNE, auto_config=True)
        jam.import_data()
        # cannot search for everything
        self.assertRaises(ValueError, lambda: jam.lookup(""))
        self.assertRaises(ValueError, lambda: jam.lookup("%"))
        self.assertRaises(ValueError, lambda: jam.lookup("%", pos=""))
        res = jam.lookup("", pos="pronoun")
        actual = all_kana(res)
        pronouns = {'おい', 'おまい', 'おたく', 'あのひと', 'かしこ', 'あのかた', 'おめえ',
                    'おまえ', 'おおい', 'おーい', 'あそこ', 'あこ', 'あしこ', 'あすこ'}
        self.assertTrue(pronouns.issubset(actual))
        result = jam.lookup("%", pos=["intransitive verb", 'pronoun'])
        forms = all_kana(result)
        iverbs = {'いじける', 'イカす', 'うろたえる', 'いかす', 'おっこちる',
                  'いらっしゃる', 'あぶれる', 'いななく', 'いちゃつく'}
        self.assertTrue(iverbs.issubset(forms))
        self.assertTrue(pronouns.issubset(forms))

    @unittest.skipIf(not _JAMDICT_DATA_AVAILABLE, "Jamdict data is not available. Data test is skipped")
    def test_jamdict_data(self):
        jam = Jamdict()
        # search verb kaeru
        res = jam.lookup("かえる", pos="transitive verb")
        actual = [e.idseq for e in res.entries]
        self.assertIn(1510650, actual)
        self.assertIn(1589780, actual)
        forms = all_kanji(res)
        expected = {'変える', '代える', '換える', '替える'}
        self.assertTrue(expected.issubset(forms))
        # search by noun kaeru
        res2 = jam.lookup("かえる", pos='noun (common) (futsuumeishi)')
        actual2 = [e.idseq for e in res2.entries]
        forms2 = all_kanji(res2)
        self.assertIn(1577460, actual2)
        expected2 = {'蛙', '蛤', '蝦'}
        self.assertTrue(expected2.issubset(forms2))
        # search both noun and verb
        res3 = jam.lookup("かえる", pos=['noun (common) (futsuumeishi)', "transitive verb"])
        forms3 = all_kanji(res3)
        self.assertTrue(expected.issubset(forms3))
        self.assertTrue(expected2.issubset(forms3))

    def test_jamdict_sqlite_all(self):
        if os.path.isfile(TEST_DB):
            os.unlink(TEST_DB)
        TEST_DB.touch()
        jam = Jamdict(db_file=TEST_DB,
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

    def test_lookup_iter(self):
        jam = Jamdict(":memory:", jmd_xml_file=MINI_JMD,
                      kd2_xml_file=MINI_KD2,
                      jmnedict_xml_file=MINI_JMNE, auto_config=True)
        jam.import_data()
        # verify entries
        res = jam.lookup_iter("おこ%", pos="noun (common) (futsuumeishi)")
        entries = [e.text() for e in res.entries]
        expected = ['おこのみやき (お好み焼き) : okonomiyaki/savoury pancake containing meat or seafood and '
                    'vegetables',
                    'おこさん (お子さん) : child',
                    "おこさま (お子様) : child (someone else's)"]
        self.assertEqual(expected, entries)
        # verify characters
        res = jam.lookup_iter("お土産")
        self.assertIsNotNone(res.entries)
        self.assertIsNotNone(res.chars)
        self.assertIsNotNone(res.names)
        # verify characters
        chars = [repr(c) for c in res.chars]
        expected = ['土:3:soil,earth,ground,Turkey',
                    '産:11:products,bear,give birth,yield,childbirth,native,property']
        self.assertEqual(expected, chars)
        # verify names
        res = jam.lookup_iter("surname")
        names = [n.text() for n in res.names]
        expected = ['しめたに (〆谷) : Shimetani (surname)',
                    'しめき (〆木) : Shimeki (surname)',
                    'しめの (〆野) : Shimeno (surname)']
        self.assertEqual(expected, names)


########################################################################

if __name__ == "__main__":
    unittest.main()
