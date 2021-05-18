# -*- coding: utf-8 -*-

"""
Test script for Jamcha SQLite
"""

# This code is a part of jamdict library: https://github.com/neocl/jamdict
# :copyright: (c) 2016 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import unittest
import logging

from jamdict import KanjiDic2SQLite
from jamdict import KanjiDic2XML


# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(TEST_DIR, 'data')
if not os.path.isdir(TEST_DATA):
    os.makedirs(TEST_DATA)
TEST_DB = os.path.join(TEST_DATA, 'jamcha.db')
MINI_KD2 = os.path.join(TEST_DATA, 'kanjidic2_mini.xml')


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Test cases
# -------------------------------------------------------------------------------

class TestJamdictSQLite(unittest.TestCase):

    db = KanjiDic2SQLite(TEST_DB)
    ramdb = KanjiDic2SQLite(":memory:", auto_expand_path=False)
    xdb = KanjiDic2XML.from_file(MINI_KD2)

    @classmethod
    def setUpClass(cls):
        if os.path.isfile(TEST_DB):
            getLogger().info("Removing previous database file at {}".format(TEST_DB))
            os.unlink(TEST_DB)

    def test_xml2sqlite(self):
        print("Test KanjiDic2 - XML to SQLite DB in RAM")
        getLogger().info("Testing using {} test characters".format(len(self.xdb)))
        db = self.ramdb
        with db.ctx() as ctx:
            fv = self.xdb.kd2.file_version
            dv = self.xdb.kd2.database_version
            doc = self.xdb.kd2.date_of_creation
            db.update_kd2_meta(fv, dv, doc, ctx)
            metas = ctx.meta.select()
            getLogger().debug("KanjiDic2 meta: {}".format(metas))
            for c in self.xdb:
                db.insert_char(c, ctx)
                c2 = db.char_by_id(c.ID, ctx)
                getLogger().debug("c-xml", c.to_json())
                getLogger().debug("c-sqlite", c2.to_json())
                self.assertEqual(c.to_json(), c2.to_json())
            # test searching
            # by id
            c = ctx.char.select_single()
            c = db.char_by_id(c.ID, ctx=ctx)
            self.assertIsNotNone(c)
            self.assertTrue(c.rm_groups[0].readings)
            self.assertTrue(c.rm_groups[0].meanings)
            # by literal
            c = db.get_char('持', ctx=ctx)
            self.assertEqual(c.literal, '持')
            self.assertTrue(c.rm_groups[0].readings)
            self.assertTrue(c.rm_groups[0].meanings)


# -------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
