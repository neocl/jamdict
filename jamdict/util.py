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

import os
import logging
import threading
from collections import defaultdict as dd

from . import config
from .jmdict import JMDictXMLParser
from .jmdict_sqlite import JMDictSQLite
from .kanjidic2 import Kanjidic2XMLParser
from .kanjidic2_sqlite import KanjiDic2SQLite


########################################################################

def getLogger():
    return logging.getLogger(__name__)


########################################################################

class LookupResult(object):

    def __init__(self, entries, chars):
        self.entries = entries if entries else []
        self.chars = chars if chars else []

    def text(self, compact=True, entry_sep='。', separator=' | '):
        output = []
        if self.entries:
            entries_txt = str(entry_sep.join(e.text(compact=compact, separator='') for e in self.entries))
            output.append("Entries: ")
            output.append(entries_txt)
        if self.entries:
            if compact:
                chars_txt = ', '.join(str(c) for c in self.chars)
            else:
                chars_txt = ', '.join(repr(c) for c in self.chars)
            if output:
                output.append(separator)
            output.append("Chars: ")
            output.append(chars_txt)
        return "".join(output) if output else "Found nothing"

    def __repr__(self):
        return self.text(compact=True)

    def __str__(self):
        return self.text(compact=False)

    def to_json(self):
        return {'entries': [e.to_json() for e in self.entries],
                'chars': [c.to_json() for c in self.chars]}


class JamdictSQLite(KanjiDic2SQLite, JMDictSQLite):

    def __init__(self, data_source, setup_script=None, setup_file=None, *args, **kwargs):
        super().__init__(data_source, setup_script=setup_script, setup_file=setup_file, *args, **kwargs)


class Jamdict(object):

    def __init__(self, db_file=None, kd2_file=None, jmd_xml_file=None, kd2_xml_file=None, auto_config=True, auto_expand=True):
        # file paths configuration
        self.auto_expand = auto_expand
        self.db_file = db_file if db_file else config.get_file('JAMDICT_DB') if auto_config else None
        self.kd2_file = kd2_file if kd2_file else config.get_file('JAMDICT_DB') if auto_config else None
        if not self.db_file or not os.path.isfile(self.db_file):
            getLogger().warning("JAMDICT_DB could NOT be found. Searching will be extremely slow. Please run `python3 -m jamdict.tools import` first")
        if not self.kd2_file or os.path.isfile(self.kd2_file):
            getLogger().warning("Kanjidic2 database could NOT be found. Searching will be extremely slow. Please run `python3 -m jamdict.tools import` first")
        self.jmd_xml_file = jmd_xml_file if jmd_xml_file else config.get_file('JMDICT_XML') if auto_config else None
        self.kd2_xml_file = kd2_xml_file if kd2_xml_file else config.get_file('KD2_XML') if auto_config else None
        # data sources
        self._db_sqlite = None
        self._kd2_sqlite = None
        self._jmd_xml = None
        self._kd2_xml = None

    @property
    def db_file(self):
        return self.__db_file

    @db_file.setter
    def db_file(self, value):
        if self.auto_expand and value:
            self.__db_file = os.path.abspath(os.path.expanduser(value))
        else:
            self.__db_file = None

    @property
    def jmdict(self):
        if not self._db_sqlite and self.db_file:
            with threading.Lock():
                if not self.kd2_file or self.kd2_file == self.db_file:
                    # Use 1 DB for both
                    self._db_sqlite = JamdictSQLite(self.db_file, auto_expand_path=self.auto_expand)
                    self._kd2_sqlite = self._db_sqlite
                else:
                    # use 2 separated files
                    self._db_sqlite = JMDictSQLite(self.db_file, auto_expand_path=self.auto_expand)
        return self._db_sqlite

    @property
    def kd2(self):
        if self._kd2_sqlite is None:
            if self.kd2_file is not None:
                with threading.Lock():
                    self._kd2_sqlite = KanjiDic2SQLite(self.kd2_file, auto_expand_path=self.auto_expand)
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
            getLogger().info("Importing JMDict data")
            self.jmdict.insert_entries(self.jmdict_xml)
        if self.kd2 is not None and self.kd2_xml:
            getLogger().info("Importing KanjiDic2 data")
            self.kd2.insert_chars(self.kd2_xml)

    def get_char(self, literal):
        if self.kd2 is not None:
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
        if self.jmdict is not None:
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
        self._seqmap = {}  # entryID - entryObj map
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
        elif a_query.startswith('id#'):
            entry_id = a_query[3:]
            if entry_id in self._seqmap:
                return (self._seqmap[entry_id],)
        # found nothing
        return ()

    @staticmethod
    def from_file(filename):
        parser = JMDictXMLParser()
        return JMDictXML(parser.parse_file(os.path.abspath(os.path.expanduser(filename))))


class KanjiDic2XML(object):

    def __init__(self, kd2):
        """
        """
        self.kd2 = kd2
        self.char_map = {}
        for char in self.kd2:
            if char.literal in self.char_map:
                getLogger().warning("Duplicate character entry: {}".format(char.literal))
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
