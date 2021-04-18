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
from collections import OrderedDict
from typing import List

from chirptext.deko import HIRAGANA, KATAKANA

from . import config
from .jmdict import JMDictXMLParser, JMDEntry
from .krad import KRad
from .jmdict_sqlite import JMDictSQLite
from .kanjidic2 import Kanjidic2XMLParser, Character
from .kanjidic2_sqlite import KanjiDic2SQLite
from .jmnedict_sqlite import JMNEDictSQLite

try:
    import jamdict_data
    _JAMDICT_DATA_AVAILABLE = True
except Exception:
    _JAMDICT_DATA_AVAILABLE = False


########################################################################

def getLogger():
    return logging.getLogger(__name__)


########################################################################


EntryList = List[JMDEntry]
CharacterList = List[Character]


class LookupResult(object):

    ''' Contain lookup results (words, Kanji characters, or named entities) from Jamdict. 
    
    A typical jamdict lookup is like this:

    >>> result = jam.lookup('食べ%る')

    The command above returns a :any:`LookupResult` object which contains found words (:any:`entries`),
    kanji characters (:any:`chars`), and named entities (:any:`names`).
    '''

    def __init__(self, entries, chars, names=None):
        self.__entries = entries if entries else []
        self.__chars = chars if chars else []
        self.__names = names if names else []

    @property
    def entries(self):
        ''' A list of words entries 
        
        :returns: a list of :class:`JMDEntry <jamdict.jmdict.JMDEntry>` object
        :rtype: EntryList
        '''
        return self.__entries

    @entries.setter
    def entries(self, values):
        self.__entries = values

    @property
    def chars(self):
        ''' A list of found kanji characters 

        :returns: a list of :class:`Character <jamdict.kanjidic2.Character>` object
        :rtype: CharacterList
        '''
        return self.__chars

    @chars.setter
    def chars(self, values):
        self.__chars = values

    @property
    def names(self):
        ''' A list of found named entities 

        :returns: a list of :class:`JMDEntry <jamdict.jmdict.JMDEntry>` object
        :rtype: EntryList
        '''
        return self.__names

    @names.setter
    def names(self, values):
        self.__names = values
        

    def text(self, compact=True, entry_sep='。', separator=' | ', no_id=False, with_chars=True):
        ''' Generate a text string that contains all found words, characters, and named entities.
        
        :param compact: Make the output string more compact (fewer info, fewer whitespaces, etc.)
        :param no_id: Do not include jamdict's internal object IDs (for direct query via API)
        :param with_chars: Include characters information
        :returns: A formatted string ready for display
        '''
        output = []
        if self.entries:
            entry_txts = []
            for idx, e in enumerate(self.entries, start=1):
                entry_txt = e.text(compact=compact, separator=' ', no_id=no_id)
                entry_txts.append("#{}: {}".format(idx, entry_txt))
            output.append("[Entries]")
            output.append(entry_sep)
            output.append(entry_sep.join(entry_txts))
        elif not compact:
            output.append("No entries")
        if self.chars and with_chars:
            if compact:
                chars_txt = ', '.join(str(c) for c in self.chars)
            else:
                chars_txt = ', '.join(repr(c) for c in self.chars)
            if output:
                output.append(separator)
            output.append("[Chars]")
            output.append(entry_sep)
            output.append(chars_txt)
        if self.names:
            name_txts = []
            for idx, n in enumerate(self.names, start=1):
                name_txt = n.text(compact=compact, separator=' ', no_id=no_id)
                name_txts.append("#{}: {}".format(idx, name_txt))
            if output:
                output.append(separator)
            output.append("[Names]")
            output.append(entry_sep)
            output.append(entry_sep.join(name_txts))
        return "".join(output) if output else "Found nothing"

    def __repr__(self):
        return self.text(compact=True)

    def __str__(self):
        return self.text(compact=False)

    def to_json(self):
        return {'entries': [e.to_json() for e in self.entries],
                'chars': [c.to_json() for c in self.chars],
                'names': [n.to_json() for n in self.names]}


class JamdictSQLite(KanjiDic2SQLite, JMNEDictSQLite, JMDictSQLite):

    def __init__(self, data_source, setup_script=None, setup_file=None, *args, **kwargs):
        super().__init__(data_source, setup_script=setup_script, setup_file=setup_file, *args, **kwargs)


class Jamdict(object):

    ''' Main entry point to access all available dictionaries in jamdict. 

    >>> from jamdict import Jamdict
    >>> jam = Jamdict()
    >>> result = jam.lookup('食べ%る')
    # print all word entries
    >>> for entry in result.entries:
    >>>     print(entry)
    # print all related characters
    >>> for c in result.chars:
    >>>     print(repr(c)) 
    '''

    def __init__(self, db_file=None, kd2_file=None,
                 jmd_xml_file=None, kd2_xml_file=None,
                 auto_config=True, auto_expand=True, reuse_ctx=True,
                 jmnedict_file=None, jmnedict_xml_file=None,
                 **kwargs):
        # file paths configuration
        self.auto_expand = auto_expand
        self.jmd_xml_file = jmd_xml_file if jmd_xml_file else config.get_file('JMDICT_XML') if auto_config else None
        self.kd2_xml_file = kd2_xml_file if kd2_xml_file else config.get_file('KD2_XML') if auto_config else None
        self.jmnedict_xml_file = jmnedict_xml_file if jmnedict_xml_file else config.get_file('JMNEDICT_XML') if auto_config else None

        self.db_file = db_file if db_file else config.get_file('JAMDICT_DB') if auto_config else None
        if not self.db_file or not os.path.isfile(self.db_file):
            if _JAMDICT_DATA_AVAILABLE:
                self.db_file = jamdict_data.JAMDICT_DB_PATH
            elif self.jmd_xml_file and os.path.isfile(self.jmd_xml_file):
                getLogger().warning("JAMDICT_DB could NOT be found. Searching will be extremely slow. Please run `python3 -m jamdict import` first")
        self.kd2_file = kd2_file if kd2_file else self.db_file if auto_config else None        
        if not self.kd2_file or not os.path.isfile(self.kd2_file):
            if _JAMDICT_DATA_AVAILABLE:
                self.kd2_file = None  # jamdict_data.JAMDICT_DB_PATH
            elif self.kd2_xml_file and os.path.isfile(self.kd2_xml_file):
                getLogger().warning("Kanjidic2 database could NOT be found. Searching will be extremely slow. Please run `python3 -m jamdict import` first")
        self.jmnedict_file = jmnedict_file if jmnedict_file else self.db_file if auto_config else None
        if not self.jmnedict_file or not os.path.isfile(self.jmnedict_file):
            if _JAMDICT_DATA_AVAILABLE:
                self.jmnedict_file = None  # jamdict_data.JAMDICT_DB_PATH
            elif self.jmnedict_xml_file and os.path.isfile(self.jmnedict_xml_file):
                getLogger().warning("JMNE database could NOT be found. Searching will be extremely slow. Please run `python3 -m jamdict import` first")
        # data sources
        self._db_sqlite = None
        self._kd2_sqlite = None
        self._jmne_sqlite = None
        self._jmd_xml = None
        self._kd2_xml = None
        self._jmne_xml = None
        self.__krad_map = None
        self.reuse_ctx = reuse_ctx
        self.__jm_ctx = None  # for reusing database context

    @property
    def ready(self):
        ''' Check if Jamdict database is available '''
        return os.path.isfile(self.db_file) and self.jmdict is not None

    def __del__(self):
        if self.__jm_ctx is not None:
            try:
                # try to close default SQLite context if needed
                self.__jm_ctx.close()
            except Exception:
                pass

    def __make_db_ctx(self):
        ''' Try to reuse context if allowed '''
        try:
            if not self.reuse_ctx:
                return self.jmdict.ctx()
            elif self.__jm_ctx is None and self.db_file and os.path.isfile(self.db_file):
                self.__jm_ctx = self.jmdict.ctx()
        except Exception:
            getLogger().warning("JMdict data could not be accessed.")
        return self.__jm_ctx

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
    def kd2_file(self):
        return self.__kd2_file

    @kd2_file.setter
    def kd2_file(self, value):
        if self.auto_expand and value:
            self.__kd2_file = os.path.abspath(os.path.expanduser(value))
        else:
            self.__kd2_file = None

    @property
    def jmnedict_file(self):
        return self.__jmnedict_file

    @jmnedict_file.setter
    def jmnedict_file(self, value):
        if self.auto_expand and value:
            self.__jmnedict_file = os.path.abspath(os.path.expanduser(value))
        else:
            self.__jmnedict_file = None

    @property
    def jmdict(self):
        if not self._db_sqlite and self.db_file:
            with threading.Lock():
                # Use 1 DB for all
                self._db_sqlite = JamdictSQLite(self.db_file, auto_expand_path=self.auto_expand)
        return self._db_sqlite

    @property
    def kd2(self):
        if self._kd2_sqlite is None:
            if self.kd2_file is not None and os.path.isfile(self.kd2_file):
                with threading.Lock():
                    self._kd2_sqlite = KanjiDic2SQLite(self.kd2_file, auto_expand_path=self.auto_expand)
            elif not self.kd2_file or self.kd2_file == self.db_file:
                self._kd2_sqlite = self.jmdict
        return self._kd2_sqlite

    @property
    def jmnedict(self):
        ''' JM NE SQLite database access object '''
        if self._jmne_sqlite is None:
            if self.jmnedict_file is not None:
                with threading.Lock():
                    self._jmne_sqlite = JMNEDictSQLite(self.jmnedict_file, auto_expand_path=self.auto_expand)
            elif not self.jmnedict_file or self.jmnedict_file == self.db_file:
                self._jmne_sqlite = self.jmdict
        return self._jmne_sqlite

    @property
    def jmdict_xml(self):
        if not self._jmd_xml and self.jmd_xml_file:
            with threading.Lock():
                getLogger().info("Loading JMDict from XML file at {}".format(self.jmd_xml_file))
                self._jmd_xml = JMDictXML.from_file(self.jmd_xml_file)
                getLogger().info("Loaded JMdict entries: {}".format(len(self._jmd_xml)))
        return self._jmd_xml

    @property
    def krad(self):
        ''' Break a kanji down to writing components

        >>> jam = Jamdict()        
        >>> print(jam.krad['雲'])
        ['一', '雨', '二', '厶']
        '''
        if not self.__krad_map:
            with threading.Lock():
                self.__krad_map = KRad()
        return self.__krad_map.krad

    @property
    def radk(self):
        ''' Find all kanji with a writing component 

        >>> jam = Jamdict()
        >>> print(jam.radk['鼎'])
        {'鼏', '鼒', '鼐', '鼎', '鼑'}
        '''
        if not self.__krad_map:
            with threading.Lock():
                self.__krad_map = KRad()
        return self.__krad_map.radk
    
    @property
    def kd2_xml(self):
        if not self._kd2_xml and self.kd2_xml_file:
            with threading.Lock():
                getLogger().info("Loading KanjiDic2 from XML file at {}".format(self.kd2_xml_file))
                self._kd2_xml = KanjiDic2XML.from_file(self.kd2_xml_file)
                getLogger().info("Loaded KanjiDic2 entries: {}".format(len(self._kd2_xml)))
        return self._kd2_xml

    @property
    def jmne_xml(self):
        if not self._jmne_xml and self.jmnedict_xml_file:
            with threading.Lock():
                getLogger().info("Loading JMnedict from XML file at {}".format(self.jmnedict_xml_file))
                self._jmne_xml = JMNEDictXML.from_file(self.jmnedict_xml_file)
                getLogger().info("Loaded JMnedict entries: {}".format(len(self._jmne_xml)))
        return self._jmne_xml

    def has_kd2(self):
        return self.db_file is not None or self.kd2_file is not None or self.kd2_xml_file is not None

    def has_jmne(self):
        ''' Check if current database has jmne support '''
        if self.jmnedict is not None:
            m = self.jmnedict.meta.select_single('key=?', ('jmnedict.version',))
            return m is not None and len(m.value) > 0
        return None

    def is_available(self):
        # this function is for developer only
        # don't expose it to the public
        # ready should be used instead
        return (self.db_file is not None or self.jmd_xml_file is not None or
                self.kd2_file is not None or self.kd2_xml_file is not None or
                self.jmnedict_file is not None or self.jmnedict_xml_file is not None)

    def import_data(self):
        ''' Import JMDict and KanjiDic2 data from XML to SQLite '''
        if self.jmdict and self.jmdict_xml:
            getLogger().info("Importing JMDict data")
            self.jmdict.insert_entries(self.jmdict_xml)
        if self.kd2 is not None and self.kd2_xml:
            getLogger().info("Importing KanjiDic2 data")
            self.kd2.insert_chars(self.kd2_xml)
        if self.jmnedict is not None and self.jmne_xml:
            getLogger().info("Importing JMNEdict data")
            self.jmnedict.insert_name_entities(self.jmne_xml)

    def get_ne(self, idseq, ctx=None):
        ''' Get name entity by idseq in JMnedict '''
        if self.jmnedict is not None:
            if ctx is None:
                ctx = self.__make_db_ctx()
            return self.jmnedict.get_ne(idseq, ctx=ctx)
        elif self.jmnedict_xml_file:
            return self.jmne_xml.lookup(idseq)
        else:
            raise LookupError("There is no JMnedict data source available")

    def get_char(self, literal, ctx=None):
        if self.kd2 is not None:
            if ctx is None:
                ctx = self.__make_db_ctx()
            return self.kd2.get_char(literal, ctx=ctx)
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

    def lookup(self, query, strict_lookup=False, lookup_chars=True, ctx=None, lookup_ne=True, **kwargs):
        ''' Search words, characters, and characters.

        Keyword arguments:

        :param query: Text to query, may contains wildcard characters. Use `?` for 1 exact character and `%` to match any number of characters.
        :param strict_lookup: only look up the Kanji characters in query (i.e. discard characters from variants)
        :type strict_lookup: bool
        :param: lookup_chars: set lookup_chars to False to disable character lookup
        :type lookup_chars: bool
        :param: ctx: database access context, can be reused for better performance. Normally users do not have to touch this and database connections will be reused by default.
        :param lookup_ne: set lookup_ne to False to disable name-entities lookup
        :type lookup_ne: bool
        :returns: Return a LookupResult object.
        :rtype: :class:`jamdict.util.LookupResult`

        >>> # match any word that starts with "食べ" and ends with "る" (anything from between is fine)
        >>> results = jam.lookup('食べ%る')
        '''
        if not self.is_available():
            raise LookupError("There is no backend data available")
        elif not query:
            raise ValueError("Query cannot be empty")
        ctx = self.__make_db_ctx()
        # Lookup words
        entries = []
        chars = []
        names = []
        if self.jmdict is not None:
            entries = self.jmdict.search(query, ctx=ctx)
        elif self.jmdict_xml:
            entries = self.jmdict_xml.lookup(query)
        if lookup_chars and self.has_kd2():
            # lookup each character in query and kanji readings of each found entries
            chars_to_search = OrderedDict({c: c for c in query})
            if not strict_lookup and entries:
                # auto add characters from entries
                for e in entries:
                    for k in e.kanji_forms:
                        for c in k.text:
                            if c not in HIRAGANA and c not in KATAKANA:
                                chars_to_search[c] = c
            for c in chars_to_search:
                result = self.get_char(c, ctx=ctx)
                if result is not None:
                    chars.append(result)
        # lookup name-entities
        if lookup_ne and self.has_jmne():
            names = self.jmnedict.search_ne(query, ctx=ctx)
        # finish
        return LookupResult(entries, chars, names)


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


class JMNEDictXML(JMDictXML):
    pass


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
