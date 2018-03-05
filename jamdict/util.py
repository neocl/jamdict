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
@license: MIT
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

########################################################################

import logging
import threading
from collections import defaultdict as dd
from .jmdict import JMDictXMLParser
from .jmdict_sqlite import JMDictSQLite
from .kanjidic2 import Kanjidic2XMLParser
from .kanjidic2_sqlite import KanjiDic2SQLite


########################################################################

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

########################################################################


class LookupResult(object):

    def __init__(self, entries, chars):
        self.entries = entries if entries else []
        self.chars = chars if chars else []

    def to_json(self):
        return {'entries': [e.to_json() for e in self.entries],
                'chars': [c.to_json() for c in self.chars]}


class JamdictSQLite(KanjiDic2SQLite, JMDictSQLite):

    def __init__(self, data_source, setup_script=None, setup_file=None):
        super().__init__(data_source, setup_script=setup_script, setup_file=setup_file)


class Jamdict(object):

    def __init__(self, db_file=None, kd2_file=None, jmd_xml_file=None, kd2_xml_file=None):
        # file paths configuration
        self.db_file = db_file
        self.kd2_file = kd2_file
        self.jmd_xml_file = jmd_xml_file
        self.kd2_xml_file = kd2_xml_file
        # data sources
        self._db_sqlite = None
        self._kd2_sqlite = None
        self._jmd_xml = None
        self._kd2_xml = None

    @property
    def jmdict(self):
        if not self._db_sqlite and self.db_file:
            with threading.Lock():
                if not self.kd2_file:
                    # Use 1 DB for both
                    self._db_sqlite = JamdictSQLite(self.db_file)
                else:
                    # use 2 separated files
                    self._db_sqlite = JMDictSQLite(self.db_file)
        return self._db_sqlite

    @property
    def kd2(self):
        if not self._kd2_sqlite:
            if self.kd2_file:
                with threading.Lock():
                    self.kd2_sqlite = KanjiDic2SQLite(self.kd2_file)
            else:
                self._kd2_sqlite = self.jmdict
        return self._kd2_sqlite

    @property
    def jmdict_xml(self):
        if not self._jmd_xml and self.jmd_xml_file:
            with threading.Lock():
                self._jmd_xml = JMDictXML.from_file(self.jmd_xml_file)
        return self._jmd_xml

    @property
    def kd2_xml(self):
        if not self._kd2_xml and self.kd2_xml_file:
            with threading.Lock():
                self._kd2_xml = KanjiDic2XML.from_file(self.kd2_xml_file)
        return self._kd2_xml

    def has_kd2(self):
        return self.db_file is not None or self.kd2_file is not None or self.kd2_xml_file is not None

    def is_available(self):
        return (self.db_file is not None or self.jmd_xml_file is not None or
                self.kd2_file is not None or self.kd2_xml_file is not None)

    def import_data(self):
        ''' Import JMDict and KanjiDic2 data from XML to SQLite '''
        if self.jmdict and self.jmdict_xml:
            logger.info("Importing JMDict data")
            self.jmdict.insert_entries(self.jmdict_xml)
        if self.kd2 and self.kd2_xml:
            logger.info("Importing KanjiDic2 data")
            self.kd2.insert_chars(self.kd2_xml)

    def get_char(self, literal):
        if self.kd2:
            return self.kd2.get_char(literal)
        elif self.kd2_xml:
            return self.kd2_xml.lookup(literal)
        else:
            raise LookupError("There is no KanjiDic2 data source available")

    def get_entry(self, idseq):
        if self.jmdict:
            return self.jmdict.get_entry(idseq)
        elif self.jmdict_xml:
            return self.jmdict_xml.lookup(idseq)[0]
        else:
            raise LookupError("There is no backend data available")

    def lookup(self, query):
        if not self.is_available():
            raise LookupError("There is no backend data available")
        elif not query:
            raise ValueError("Query cannot be empty")
        # Lookup words
        entries = []
        chars = []
        if self.jmdict:
            entries = self.jmdict.search(query)
        elif self.jmdict_xml:
            entries = self.jmdict_xml.lookup(query)
        if self.has_kd2():
            # lookup each character in query and kanji readings of each found entries
            chars_to_search = set(query)
            if entries:
                for e in entries:
                    for k in e.kanji_forms:
                        chars_to_search.update(k.text)
            for c in chars_to_search:
                result = self.get_char(c)
                if result is not None:
                    chars.append(result)
        return LookupResult(entries, chars)


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
    def from_file(filename):
        parser = JMDictXMLParser()
        return JMDictXML(parser.parse_file(filename))


class KanjiDic2XML(object):

    def __init__(self, kd2):
        """
        """
        self.kd2 = kd2
        self.char_map = {}
        for char in self.kd2:
            if char.literal in self.char_map:
                logger.warning("Duplicate character entry: {}".format(char.literal))
            self.char_map[char.literal] = char

    def __len__(self):
        return len(self.kd2)

    def __getitem__(self, idx):
        return self.kd2[idx]

    def lookup(self, char):
        if char in self.char_map:
            return self.char_map[char]
        else:
            return None

    @staticmethod
    def from_file(filename):
        parser = Kanjidic2XMLParser()
        return KanjiDic2XML(parser.parse_file(filename))
