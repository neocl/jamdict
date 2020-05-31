#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test script for JMendict support
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

# Copyright (c) 2020, Le Tuan Anh <tuananh.ke@gmail.com>
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
__copyright__ = "Copyright 2020, jamdict"
__license__ = "MIT"

########################################################################

import os
import unittest
import logging

from jamdict.jmdict import JMDictXMLParser, JMENDICT_TYPE_MAP
from jamdict.util import JMNEDictXML, JamdictSQLite
from jamdict.jmnedict_sqlite import JMNEDictSQLite


# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(TEST_DIR, 'data')
if not os.path.isdir(TEST_DATA):
    os.makedirs(TEST_DATA)
TEST_DB = os.path.join(TEST_DATA, 'jamcha.db')
MINI_JMNE = os.path.join(TEST_DATA, 'jmendict_mini.xml')


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Test cases
# -------------------------------------------------------------------------------

class TestJMendictModels(unittest.TestCase):

    xdb = JMNEDictXML.from_file(MINI_JMNE)
    ramdb = JMNEDictSQLite(":memory:", auto_expand_path=False)
    ramdb = JamdictSQLite(":memory:", auto_expand_path=False)

    def extract_fields(self):
        ''' Test JMnedict XML parser '''
        entries = self.xdb.entries
        expected_idseqs = ['1657560', '2092920', '2831743', '5000000',
                           '5000001', '5000002', '5000003', '5000004',
                           '5000005', '5000006', '5000007', '5000008',
                           '5000009', '5741686', '5723538', '5741815', '5001644']
        idseqs = [e.idseq for e in entries]
        self.assertEqual(expected_idseqs, idseqs)

    def test_ne_type_map(self):
        ''' Test all name_type* '''
        expected = {'person', 'organization', 'surname', 'company',
                    'place', 'fem', 'unclass', 'masc', 'given', 'work',
                    'product', 'ok', 'station'}
        actual = set(JMENDICT_TYPE_MAP.keys())
        self.assertEqual(expected, actual)

    def test_jmne_support(self):
        ''' Test metadata '''
        with self.ramdb.ctx() as ctx:
            self.ramdb.insert_name_entities(self.xdb, ctx=ctx)
            m = ctx.meta.select_single('key=?', ('jmnedict.version',))
            self.assertEqual(m.key, 'jmnedict.version')
            self.assertEqual(m.value, '1.08')

    def test_xml2ramdb(self):
        print("Testing XML to RAM")
        with self.ramdb.ctx() as ctx:
            self.ramdb.insert_name_entities(self.xdb, ctx=ctx)
            # all entries were inserted
            expected_idseqs = {int(e.idseq) for e in self.xdb}
            inserted_idseqs = {e.idseq for e in self.ramdb.NEEntry.select(ctx=ctx)}
            getLogger().info("Inserted entries: {}".format(len(inserted_idseqs)))
            self.assertEqual(expected_idseqs, inserted_idseqs)
            # make sure that the kanjis are inserted
            expected_kanjis = set()
            for e in self.xdb.entries:
                expected_kanjis.update(k.text for k in e.kanji_forms)
            kanjis = {k.text for k in self.ramdb.NEKanji.select(ctx=ctx)}
            self.assertEqual(expected_kanjis, kanjis)
            # make sure that the kanas were inserted
            expected_readings = set()
            for e in self.xdb.entries:
                expected_readings.update(k.text for k in e.kana_forms)
            readings = {k.text for k in self.ramdb.NEKana.select(ctx=ctx)}
            self.assertEqual(expected_readings, readings)
            # make sure that the definitions were inserted
            expected_glosses = set()
            for e in self.xdb.entries:
                for s in e.senses:
                    expected_glosses.update(g.text for g in s.gloss)
            glosses = {k.text for k in self.ramdb.NETransGloss.select(ctx=ctx)}
            self.assertEqual(expected_glosses, glosses)
            # make sure that the XML entries and the SQLite entries are the same
            for idseq in inserted_idseqs:
                ne_xml = self.xdb.lookup("id#{}".format(idseq))[0]
                ne_xml.idseq = int(ne_xml.idseq)
                getLogger().debug(ne_xml.to_json())
                ne = self.ramdb.get_ne(idseq, ctx=ctx)
                getLogger().debug(ne.to_json())
                self.assertEqual(ne_xml.to_json(), ne.to_json())
            # test search by idseq
            shenron = self.ramdb.search_ne('id#5741815', ctx=ctx)
            self.assertEqual(len(shenron), 1)
            self.assertEqual(shenron[0].idseq, 5741815)
            # test exact search
            shenron2 = self.ramdb.search_ne('神龍', ctx=ctx)
            self.assertEqual(len(shenron2), 1)
            self.assertEqual(shenron2[0].idseq, 5741815)
            # test search by kana
            shenron3 = self.ramdb.search_ne('シェンロン', ctx=ctx)
            self.assertEqual(len(shenron3), 1)
            self.assertEqual(shenron3[0].idseq, 5741815)
            # test search by definition
            shenron4 = self.ramdb.search_ne('%spiritual%', ctx=ctx)
            self.assertEqual(len(shenron4), 1)
            self.assertEqual(shenron4[0].idseq, 5741815)
            # test search by wild card
            all_shime_names = self.ramdb.search_ne('しめ%', ctx=ctx)
            expected_idseqs = [5000001, 5000002, 5000003, 5000004, 5000005, 5000006, 5000007, 5000008, 5000009]
            actual = [x.idseq for x in all_shime_names]
            print(actual)
            self.assertEqual(expected_idseqs, actual)
            # test search by name_type
            all_fems = self.ramdb.search_ne('person', ctx=ctx)
            expected_idseqs = [2831743, 5001644]
            actual = [x.idseq for x in all_fems]
            self.assertEqual(expected_idseqs, actual)


# -------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
