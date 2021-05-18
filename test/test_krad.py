#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script for testing KRad module library

References:
     RADKFILE/KRADFILE
        This project provides a decomposition of kanji into a number of visual elements
        or radicals to support software which provides a lookup service using kanji components.
        https://www.edrdg.org/krad/kradinf.html
"""

# This code is a part of jamdict library: https://github.com/neocl/jamdict
# :copyright: (c) 2016 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import logging
import os
import unittest

from jamdict import config
from jamdict.krad import KRad

########################################################################

MY_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DATA = os.path.join(MY_DIR, 'data')
MINI_JMD = os.path.join(TEST_DATA, 'JMdict_mini.xml')
MINI_KD2 = os.path.join(TEST_DATA, 'kanjidic2_mini.xml')
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

    def test_read_krad(self):
        krad = KRad()
        self.assertEqual(krad.krad['㘅'], ['亅', '二', '口', '彳', '金'])
        self.assertEqual(krad.krad['𪚲'], ['乙', '勹', '月', '田', '亀'])
        self.assertEqual(krad.radk['龠'], {'籥', '鸙', '龢', '龠', '龡', '籲', '瀹', '龥', '禴', '鑰', '爚', '龣'})


########################################################################

if __name__ == "__main__":
    logging.getLogger('jamdict').setLevel(logging.DEBUG)
    unittest.main()
