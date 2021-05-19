#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for JMDict SQLite
"""

# This code is a part of jamdict library: https://github.com/neocl/jamdict
# :copyright: (c) 2016 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import unittest
import logging
from pathlib import Path

from chirptext.cli import setup_logging

from jamdict import Jamdict
from jamdict import JMDictXML
from jamdict import JMDictSQLite


# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

TEST_DIR = Path(os.path.realpath(__file__)).parent
TEST_DATA = TEST_DIR / 'data'
if not TEST_DATA.exists():
    TEST_DATA.mkdir()
TEST_DB = TEST_DATA / 'test.db'
MINI_JMD = TEST_DATA / 'JMdict_mini.xml'
okashi = 'お菓子'


setup_logging(TEST_DIR / 'logging.json', 'logs')


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Test cases
# -------------------------------------------------------------------------------

class TestJamdictSQLite(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JMDictSQLite(str(TEST_DB))
        self.xdb = JMDictXML.from_file(str(MINI_JMD))
        self.ramdb = JMDictSQLite(":memory:")

    @classmethod
    def setUpClass(cls):
        if os.path.isfile(TEST_DB):
            getLogger().info("Removing previous database file at {}".format(TEST_DB))
            os.unlink(TEST_DB)

    def test_xml2sqlite(self):
        print("Test JMDict: XML to SQLite")
        try:
            self.db.insert_entries(self.xdb)
        except Exception:
            getLogger().exception("Error happened while inserting entries")
            raise
        entries = self.db.Entry.select()
        self.assertEqual(len(entries), len(self.xdb))
        # test select entry by id
        e = self.db.get_entry(1001710)
        ejson = e.to_json()
        self.assertEqual(ejson['kanji'][0]['text'], 'お菓子')
        getLogger().debug(e.to_json())

    def test_import_to_ram(self):
        print("Testing XML to RAM")
        noe = len(self.xdb)
        with self.ramdb.ctx() as ctx:
            self.ramdb.insert_entries(self.xdb, ctx=ctx)
            self.assertEqual(len(self.ramdb.Entry.select(ctx=ctx)), noe)

    def test_import_function(self):
        print("Testing JMDict import function")
        jd = Jamdict(db_file=":memory:", jmd_xml_file=MINI_JMD, auto_config=False, auto_expand=False)
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
            getLogger().info('あの: {}'.format('|'.join([str(x) for x in es])))
            # Search by kanji
            es = self.db.search('%子%', ctx, exact_match=False)
            self.assertEqual(len(es), 4)
            getLogger().info('%子%: {}'.format('|'.join([str(x) for x in es])))
            # search by meaning
            es = self.db.search('%confections%', ctx, exact_match=False)
            self.assertTrue(es)
            getLogger().info('%confections%: {}'.format('|'.join([str(x) for x in es])))

# -------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
