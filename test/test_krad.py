#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script for testing KRad module library
Latest version can be found at https://github.com/neocl/jamdict

References:
     RADKFILE/KRADFILE
        This project provides a decomposition of kanji into a number of visual elements
        or radicals to support software which provides a lookup service using kanji components.
        https://www.edrdg.org/krad/kradinf.html

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
