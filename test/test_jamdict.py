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
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import logging
import unittest
from jamdict import JMDict, JMDictXML
from jamdict import JMDictXMLParser

########################################################################

MINI_DATA_FILE = 'data/JMdict_mini.xml'


class TestJamdictXML(unittest.TestCase):

    def test_jmd_xml(self):
        print("Test lookup from mini dictionary")
        parser = JMDictXMLParser()
        entries = parser.parse_file(MINI_DATA_FILE)
        jmd = JMDictXML(entries)
        self.assertTrue(jmd.lookup(u'おてんき'))

    def test_json(self):
        # Load mini dict data
        jmd = JMDictXML.fromfile(MINI_DATA_FILE)
        e = jmd[10]
        print(e)
        print(e.to_json())
        print(jmd[-1].to_json())


########################################################################

def main():
    logging.getLogger('jamdict').setLevel(logging.DEBUG)
    unittest.main()


if __name__ == "__main__":
    main()
