#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Basic APIs for accessing a parsed JMDict

Latest version can be found at https://github.com/neocl/jamdict

This package uses the [EDICT][1] and [KANJIDIC][2] dictionary files.
These files are the property of the [Electronic Dictionary Research and Development Group][3], and are used in conformance with the Group's [licence][4].

[1]: http://www.csse.monash.edu.au/~jwb/edict.html
[2]: http://www.csse.monash.edu.au/~jwb/kanjidic.html
[3]: http://www.edrdg.org/
[4]: http://www.edrdg.org/edrdg/licence.html

References:
    JMDict website:
        http://www.csse.monash.edu.au/~jwb/edict.html
    Python documentation:
        https://docs.python.org/
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

from collections import defaultdict as dd
from .jamdict import JMDictXMLParser
from .jamdict_sqlite import JMDSQLite

########################################################################


class JMDict(object):

    def __init__(self, xmlfile=None, dbfile=None):
        if xmlfile:
            self.read_xml(xmlfile)
        else:
            self.jmd_xml = None
        if dbfile:
            self.read_db(dbfile)
        else:
            self.jmd_sqlite = None

    def read_db(self, filename):
        self.jmd_sqlite = JMDSQLite(filename)

    def read_xml(self, filename):
        self.jmd_xml = JMDictXML.fromfile(filename)

    def import_data(self):
        if self.jmd_sqlite and self.jmd_xml:
            self.jmd_sqlite.insert(*self.jmd_xml.entries)

    def lookup(self, query):
        if self.jmd_sqlite:
            return self.jmd_sqlite.search(query)
        elif self.jmd_xml:
            return self.jmd_xml.lookup(query)
        else:
            raise Exception("There is no backend data available")


class JMDictXML(object):
    ''' JMDict API for looking up information in XML
    '''
    def __init__(self, entries):
        self.entries = entries
        self._seqmap = {}
        self._textmap = dd(set)
        # compile map
        for entry in self.entries:
            self._seqmap[entry.idseq] = entry
            for kn in entry.kana_forms:
                self._textmap[kn.text].add(entry)
            for kj in entry.kanji_forms:
                self._textmap[kj.text].add(entry)

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, idx):
        return self.entries[idx]

    def lookup(self, a_query):
        if a_query in self._textmap:
            return tuple(self._textmap[a_query])
        elif a_query in self._seqmap:
            return (self._seqmap[a_query],)
        else:
            return ()

    @staticmethod
    def fromfile(filename):
        parser = JMDictXMLParser()
        return JMDictXML(parser.parse_file(filename))


########################################################################

def main():
    ''' Main enntry point. This should NOT be run anyway.
    '''
    print("This is a library, not an application.")


if __name__ == '__main__':
    main()
