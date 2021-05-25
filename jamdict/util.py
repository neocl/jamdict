# -*- coding: utf-8 -*-

"""
Jamdict public APIs
"""

# This code is a part of jamdict library: https://github.com/neocl/jamdict
# :copyright: (c) 2016 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import logging
import threading
import warnings
from collections import defaultdict as dd
from collections import OrderedDict
from typing import List, Sequence

from chirptext.deko import HIRAGANA, KATAKANA
_MEMORY_MODE = False
try:
    from puchikarui import MemorySource
    _MEMORY_MODE = True
except ImportError:
    pass
from puchikarui import ExecutionContext

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

class LookupResult(object):

    """ Contain lookup results (words, Kanji characters, or named entities) from Jamdict.

    A typical jamdict lookup is like this:

    >>> jam = Jamdict()
    >>> result = jam.lookup('食べ%る')

    The command above returns a :any:`LookupResult` object which contains found words (:any:`entries`),
    kanji characters (:any:`chars`), and named entities (:any:`names`).
    """

    def __init__(self, entries, chars, names=None):
        self.__entries: Sequence[JMDEntry] = entries if entries else []
        self.__chars: Sequence[Character] = chars if chars else []
        self.__names: Sequence[JMDEntry] = names if names else []

    @property
    def entries(self) -> Sequence[JMDEntry]:
        """ A list of words entries

        :returns: a list of :class:`JMDEntry <jamdict.jmdict.JMDEntry>` object
        :rtype: List[JMDEntry]
        """
        return self.__entries

    @entries.setter
    def entries(self, values: Sequence[JMDEntry]):
        self.__entries = values

    @property
    def chars(self) -> Sequence[Character]:
        """ A list of found kanji characters

        :returns: a list of :class:`Character <jamdict.kanjidic2.Character>` object
        :rtype: Sequence[Character]
        """
        return self.__chars

    @chars.setter
    def chars(self, values: Sequence[Character]):
        self.__chars = values

    @property
    def names(self) -> Sequence[JMDEntry]:
        """ A list of found named entities

        :returns: a list of :class:`JMDEntry <jamdict.jmdict.JMDEntry>` object
        :rtype: Sequence[JMDEntry]
        """
        return self.__names

    @names.setter
    def names(self, values: Sequence[JMDEntry]):
        self.__names = values

    def text(self, compact=True, entry_sep='。', separator=' | ', no_id=False, with_chars=True) -> str:
        """ Generate a text string that contains all found words, characters, and named entities.

        :param compact: Make the output string more compact (fewer info, fewer whitespaces, etc.)
        :param no_id: Do not include jamdict's internal object IDs (for direct query via API)
        :param entry_sep: The text to separate entries
        :param with_chars: Include characters information
        :returns: A formatted string ready for display
        """
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
                output.append(separator)  # TODO: section separator?
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
        warnings.warn("to_json() is deprecated and will be removed in the next major release. Use to_dict() instead.",
                      DeprecationWarning, stacklevel=2)
        return self.to_dict()

    def to_dict(self) -> dict:
        return {'entries': [e.to_dict() for e in self.entries],
                'chars': [c.to_dict() for c in self.chars],
                'names': [n.to_dict() for n in self.names]}


class IterLookupResult(object):

    """ Contain lookup results (words, Kanji characters, or named entities) from Jamdict.

    A typical jamdict lookup is like this:

    >>> res = jam.lookup_iter("花見")

    ``res`` is an :class:`IterLookupResult` object which contains iterators
    to scan through found words (``entries``), kanji characters (``chars``),
    and named entities (:any:`names`) one by one.

    >>> for word in res.entries:
    ...     print(word)  # do somethign with the word
    >>> for c in res.chars:
    ...     print(c)
    >>> for name in res.names:
    ...     print(name)
    """

    def __init__(self, entries, chars=None, names=None):
        self.__entries = entries if entries is not None else []
        self.__chars = chars if chars is not None else []
        self.__names = names if names is not None else []

    @property
    def entries(self):
        """ Iterator for looping one by one through all found entries, can only be used once """
        return self.__entries

    @property
    def chars(self):
        """ Iterator for looping one by one through all found kanji characters, can only be used once """
        return self.__chars

    @property
    def names(self):
        """ Iterator for looping one by one through all found named entities, can only be used once """
        return self.__names


class JamdictSQLite(KanjiDic2SQLite, JMNEDictSQLite, JMDictSQLite):

    def __init__(self, db_file, *args, **kwargs):
        super().__init__(db_file, *args, **kwargs)


class Jamdict(object):

    """ Main entry point to access all available dictionaries in jamdict.

    >>> from jamdict import Jamdict
    >>> jam = Jamdict()
    >>> result = jam.lookup('食べ%る')
    # print all word entries
    >>> for entry in result.entries:
    >>>     print(entry)
    # print all related characters
    >>> for c in result.chars:
    >>>     print(repr(c))

    To filter results by ``pos``, for example look for all "かえる" that are nouns, use:

    >>> result = jam.lookup("かえる", pos=["noun (common) (futsuumeishi)"])

    To search for named-entities by type, use the type string as query.
    For example to search for all "surname" use:

    >>> result = jam.lookup("surname")

    To find out which part-of-speeches or named-entities types are available in the 
    dictionary, use :func:`Jamdict.all_pos <jamdict.util.Jamdict.all_pos>`
    and :func:`Jamdict.all_ne_type <jamdict.util.Jamdict.all_pos>`.

    Jamdict >= 0.1a10 support ``memory_mode`` keyword argument for reading
    the whole database into memory before querying to boost up search speed.
    The database may take about a minute to load. Here is the sample code:

    >>> jam = Jamdict(memory_mode=True)

    When there is no suitable database available, Jamdict will try to use database 
    from `jamdict-data <https://pypi.org/project/jamdict-data/>`_ package by default.
    If there is a custom database available in configuration file,
    Jamdict will prioritise to use it over the ``jamdict-data`` package.
    """

    def __init__(self, db_file=None, kd2_file=None,
                 jmd_xml_file=None, kd2_xml_file=None,
                 auto_config=True, auto_expand=True, reuse_ctx=True,
                 jmnedict_file=None, jmnedict_xml_file=None,
                 memory_mode=False, **kwargs):

        # data sources
        self.reuse_ctx = reuse_ctx
        self._db_sqlite = None
        self._kd2_sqlite = None
        self._jmne_sqlite = None
        self._jmd_xml = None
        self._kd2_xml = None
        self._jmne_xml = None
        self.__krad_map = None
        self.__jm_ctx = None  # for reusing database context
        self.__memory_mode = memory_mode

        # file paths configuration
        self.auto_expand = auto_expand
        self.jmd_xml_file = jmd_xml_file if jmd_xml_file else config.get_file('JMDICT_XML') if auto_config else None
        self.kd2_xml_file = kd2_xml_file if kd2_xml_file else config.get_file('KD2_XML') if auto_config else None
        self.jmnedict_xml_file = jmnedict_xml_file if jmnedict_xml_file else config.get_file('JMNEDICT_XML') if auto_config else None

        self.db_file = db_file if db_file else config.get_file('JAMDICT_DB') if auto_config else None
        if not self.db_file or (self.db_file != ':memory:' and not os.path.isfile(self.db_file)):
            if _JAMDICT_DATA_AVAILABLE:
                self.db_file = jamdict_data.JAMDICT_DB_PATH
            elif self.jmd_xml_file and os.path.isfile(self.jmd_xml_file):
                getLogger().warning("JAMDICT_DB could NOT be found. Searching will be extremely slow. Please run `python3 -m jamdict import` first")
        self.kd2_file = kd2_file if kd2_file else self.db_file if auto_config else None
        if not self.kd2_file or (self.kd2_file != ':memory:' and not os.path.isfile(self.kd2_file)):
            if _JAMDICT_DATA_AVAILABLE:
                self.kd2_file = None  # jamdict_data.JAMDICT_DB_PATH
            elif self.kd2_xml_file and os.path.isfile(self.kd2_xml_file):
                getLogger().warning("Kanjidic2 database could NOT be found. Searching will be extremely slow. Please run `python3 -m jamdict import` first")
        self.jmnedict_file = jmnedict_file if jmnedict_file else self.db_file if auto_config else None
        if not self.jmnedict_file or (self.jmnedict_file != ':memory:' and not os.path.isfile(self.jmnedict_file)):
            if _JAMDICT_DATA_AVAILABLE:
                self.jmnedict_file = None  # jamdict_data.JAMDICT_DB_PATH
            elif self.jmnedict_xml_file and os.path.isfile(self.jmnedict_xml_file):
                getLogger().warning("JMNE database could NOT be found. Searching will be extremely slow. Please run `python3 -m jamdict import` first")

    @property
    def ready(self) -> bool:
        """ Check if Jamdict database is available """
        return os.path.isfile(self.db_file) and self.jmdict is not None

    def __del__(self):
        if self.__jm_ctx is not None:
            try:
                # try to close default SQLite context if needed
                self.__jm_ctx.close()
            except Exception:
                pass

    def __make_db_ctx(self) -> ExecutionContext:
        """ Try to reuse context if allowed """
        try:
            if not self.reuse_ctx:
                return self.jmdict.ctx()
            elif self.__jm_ctx is None and self.db_file and (self.db_file == ":memory:" or os.path.isfile(self.db_file)):
                self.__jm_ctx = self.jmdict.ctx()
        except Exception:
            getLogger().warning("JMdict data could not be accessed.")
        return self.__jm_ctx

    @property
    def db_file(self):
        return self.__db_file

    @db_file.setter
    def db_file(self, value):
        if self.auto_expand and value and value != ':memory:':
            self.__db_file = os.path.abspath(os.path.expanduser(value))
        else:
            self.__db_file = value

    @property
    def kd2_file(self):
        return self.__kd2_file

    @kd2_file.setter
    def kd2_file(self, value):
        if self.auto_expand and value and value != ':memory:':
            self.__kd2_file = os.path.abspath(os.path.expanduser(value))
        else:
            self.__kd2_file = value

    @property
    def jmnedict_file(self):
        return self.__jmnedict_file

    @jmnedict_file.setter
    def jmnedict_file(self, value):
        if self.auto_expand and value and value != ':memory:':
            self.__jmnedict_file = os.path.abspath(os.path.expanduser(value))
        else:
            self.__jmnedict_file = value

    @property
    def memory_mode(self):
        """ if memory_mode = True, Jamdict DB will be loaded into RAM before querying for better performance """
        return self.__memory_mode

    @property
    def jmdict(self):
        if not self._db_sqlite and self.db_file:
            with threading.Lock():
                # Use 1 DB for all
                if self.memory_mode and _MEMORY_MODE:
                    data_source = MemorySource(self.db_file)
                else:
                    if self.memory_mode and not _MEMORY_MODE:
                        logging.getLogger(__name__).error("Memory mode could not be enabled because puchikarui version is too old. Fallback to normal file DB mode")
                    data_source = self.db_file
                self._db_sqlite = JamdictSQLite(data_source, auto_expand_path=self.auto_expand)
        return self._db_sqlite

    @property
    def kd2(self):
        if self._kd2_sqlite is None:
            if self.kd2_file is not None and os.path.isfile(self.kd2_file):
                with threading.Lock():
                    if self.memory_mode and _MEMORY_MODE:
                        data_source = MemorySource(self.kd2_file)
                    else:
                        if self.memory_mode and not _MEMORY_MODE:
                            logging.getLogger(__name__).error("Memory mode could not be enabled because puchikarui version is too old. Fallback to normal file DB mode")
                        data_source = self.kd2_file
                    self._kd2_sqlite = KanjiDic2SQLite(data_source, auto_expand_path=self.auto_expand)
            elif not self.kd2_file or self.kd2_file == self.db_file:
                self._kd2_sqlite = self.jmdict
        return self._kd2_sqlite

    @property
    def jmnedict(self):
        """ JM NE SQLite database access object """
        if self._jmne_sqlite is None:
            if self.jmnedict_file is not None:
                with threading.Lock():
                    if self.memory_mode and _MEMORY_MODE:
                        data_source = MemorySource(self.jmnedict_file)
                    else:
                        if self.memory_mode and not _MEMORY_MODE:
                            logging.getLogger(__name__).error("Memory mode could not be enabled because puchikarui version is too old. Fallback to normal file DB mode")
                        data_source = self.jmnedict_file
                    self._jmne_sqlite = JMNEDictSQLite(data_source, auto_expand_path=self.auto_expand)
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
        """ Break a kanji down to writing components

        >>> jam = Jamdict()
        >>> print(jam.krad['雲'])
        ['一', '雨', '二', '厶']
        """
        if not self.__krad_map:
            with threading.Lock():
                self.__krad_map = KRad()
        return self.__krad_map.krad

    @property
    def radk(self):
        """ Find all kanji with a writing component

        >>> jam = Jamdict()
        >>> print(jam.radk['鼎'])
        {'鼏', '鼒', '鼐', '鼎', '鼑'}
        """
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

    def has_kd2(self) -> bool:
        return self.db_file is not None or self.kd2_file is not None or self.kd2_xml_file is not None

    def has_jmne(self, ctx=None) -> bool:
        """ Check if current database has jmne support """
        if ctx is None:
            ctx = self.__make_db_ctx()
        m = ctx.meta.select_single('key=?', ('jmnedict.version',)) if ctx is not None else None
        return m is not None and len(m.value) > 0

    def is_available(self) -> bool:
        # this function is for developer only
        # don't expose it to the public
        # ready should be used instead
        return (self.db_file is not None or self.jmd_xml_file is not None or
                self.kd2_file is not None or self.kd2_xml_file is not None or
                self.jmnedict_file is not None or self.jmnedict_xml_file is not None)

    def import_data(self):
        """ Import JMDict and KanjiDic2 data from XML to SQLite """
        ctx = self.__make_db_ctx()
        ctx.buckmode()
        if self.jmdict and self.jmdict_xml:
            getLogger().info("Importing JMDict data")
            self.jmdict.insert_entries(self.jmdict_xml, ctx=ctx)
        # import KanjiDic2
        if self.kd2 is not None and self.kd2_xml and os.path.isfile(self.kd2_xml_file):
            getLogger().info("Importing KanjiDic2 data")
            if self.jmdict is not None and self.kd2_file == self.db_file:
                self.jmdict.insert_chars(self.kd2_xml, ctx=ctx)
            else:
                getLogger().warning(f"Building Kanjidic2 DB using a different DB context {self.kd2_file} vs {self.db_file}")
                with self.kd2.ctx() as kd_ctx:
                    self.kd2.insert_chars(self.kd2_xml, ctx=kd_ctx)
        else:
            getLogger().warning("KanjiDic2 XML data is not available - skipped!")
        # import JMNEdict
        if self.jmnedict is not None and self.jmne_xml and os.path.isfile(self.jmnedict_xml_file):
            getLogger().info("Importing JMNEdict data")
            if self.jmdict is not None and self.jmnedict_file == self.db_file:
                self.jmnedict.insert_name_entities(self.jmne_xml, ctx=ctx)
            else:
                getLogger().warning(f"Building Kanjidic2 DB using a different DB context {self.jmne_file} vs {self.db_file}")
                with self.jmnedict.ctx() as ne_ctx:
                    self.jmnedict.insert_name_entities(self.jmne_xml, ctx=ne_ctx)
        else:
            getLogger().warning("JMNEdict XML data is not available - skipped!")
        _buckmode_off = getattr(ctx, "buckmode_off", None)
        if _buckmode_off is not None:
            _buckmode_off()
        ctx.commit()

    def get_ne(self, idseq, ctx=None) -> JMDEntry:
        """ Get name entity by idseq in JMNEdict """
        if self.jmnedict is not None:
            if ctx is None:
                ctx = self.__make_db_ctx()
            return self.jmnedict.get_ne(idseq, ctx=ctx)
        elif self.jmnedict_xml_file:
            return self.jmne_xml.lookup(idseq)
        else:
            raise LookupError("There is no JMnedict data source available")

    def get_char(self, literal, ctx=None) -> Character:
        if self.kd2 is not None:
            if ctx is None:
                ctx = self.__make_db_ctx()
            return self.kd2.get_char(literal, ctx=ctx)
        elif self.kd2_xml:
            return self.kd2_xml.lookup(literal)
        else:
            raise LookupError("There is no KanjiDic2 data source available")

    def get_entry(self, idseq) -> JMDEntry:
        if self.jmdict:
            return self.jmdict.get_entry(idseq)
        elif self.jmdict_xml:
            return self.jmdict_xml.lookup(idseq)[0]
        else:
            raise LookupError("There is no backend data available")

    def all_pos(self, ctx=None) -> List[str]:
        """ Find all available part-of-speeches

        :returns: A list of part-of-speeches (a list of strings)
        """
        if ctx is None:
            ctx = self.__make_db_ctx()
        return self.jmdict.all_pos(ctx=ctx)

    def all_ne_type(self, ctx=None) -> List[str]:
        """ Find all available named-entity types

        :returns: A list of named-entity types (a list of strings)
        """
        if ctx is None:
            ctx = self.__make_db_ctx()
        return self.jmnedict.all_ne_type(ctx=ctx)

    def lookup(self, query, strict_lookup=False, lookup_chars=True, ctx=None,
               lookup_ne=True, pos=None, **kwargs) -> LookupResult:
        """ Search words, characters, and characters.

        Keyword arguments:

        :param query: Text to query, may contains wildcard characters. Use `?` for 1 exact character and `%` to match any number of characters.
        :param strict_lookup: only look up the Kanji characters in query (i.e. discard characters from variants)
        :type strict_lookup: bool
        :param: lookup_chars: set lookup_chars to False to disable character lookup
        :type lookup_chars: bool
        :param pos: Filter words by part-of-speeches
        :type pos: list of strings
        :param ctx: database access context, can be reused for better performance. Normally users do not have to touch this and database connections will be reused by default.
        :param lookup_ne: set lookup_ne to False to disable name-entities lookup
        :type lookup_ne: bool
        :returns: Return a LookupResult object.
        :rtype: :class:`jamdict.util.LookupResult`

        >>> # match any word that starts with "食べ" and ends with "る" (anything from between is fine)
        >>> jam = Jamdict()
        >>> results = jam.lookup('食べ%る')
        """
        if not self.is_available():
            raise LookupError("There is no backend data available")
        elif (not query or query == "%") and not pos:
            raise ValueError("Query and POS filter cannot be both empty")
        if ctx is None:
            ctx = self.__make_db_ctx()
        entries = []
        chars = []
        names = []
        if self.jmdict is not None:
            entries = self.jmdict.search(query, pos=pos, ctx=ctx)
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
        if lookup_ne and self.has_jmne(ctx=ctx):
            names = self.jmnedict.search_ne(query, ctx=ctx)
        # finish
        return LookupResult(entries, chars, names)

    def lookup_iter(self, query, strict_lookup=False,
                    lookup_chars=True, lookup_ne=True,
                    ctx=None, pos=None, **kwargs) -> LookupResult:
        """ Search for words, characters, and characters iteratively.

        An :class:`IterLookupResult` object will be returned instead of the normal ``LookupResult``.
        ``res.entries``, ``res.chars``, ``res.names`` are iterators instead of lists and each of them
        can only be looped through once. Users have to store the results manually.
        
        >>> res = jam.lookup_iter("花見")
        >>> for word in res.entries:
        ...     print(word)  # do somethign with the word
        >>> for c in res.chars:
        ...     print(c)
        >>> for name in res.names:
        ...     print(name)

        Keyword arguments:

        :param query: Text to query, may contains wildcard characters. Use `?` for 1 exact character and `%` to match any number of characters.
        :param strict_lookup: only look up the Kanji characters in query (i.e. discard characters from variants)
        :type strict_lookup: bool
        :param: lookup_chars: set lookup_chars to False to disable character lookup
        :type lookup_chars: bool
        :param pos: Filter words by part-of-speeches
        :type pos: list of strings
        :param ctx: database access context, can be reused for better performance. Normally users do not have to touch this and database connections will be reused by default.
        :param lookup_ne: set lookup_ne to False to disable name-entities lookup
        :type lookup_ne: bool
        :returns: Return an IterLookupResult object.
        :rtype: :class:`jamdict.util.IterLookupResult`
        """
        if not self.is_available():
            raise LookupError("There is no backend data available")
        elif (not query or query == "%") and not pos:
            raise ValueError("Query and POS filter cannot be both empty")
        if ctx is None:
            ctx = self.__make_db_ctx()
        # Lookup entries, chars, and names
        entries = None
        chars = None
        names = None
        if self.jmdict is not None:
            entries = self.jmdict.search_iter(query, pos=pos, ctx=ctx)
        if lookup_chars and self.has_kd2():
            chars_to_search = OrderedDict({c: c for c in query if c not in HIRAGANA and c not in KATAKANA})
            chars = self.kd2.search_chars_iter(chars_to_search, ctx=ctx)
        # lookup name-entities
        if lookup_ne and self.has_jmne(ctx=ctx):
            names = self.jmnedict.search_ne_iter(query, ctx=ctx)
        # finish
        return IterLookupResult(entries, chars, names)


class JMDictXML(object):
    """ JMDict API for looking up information in XML
    """
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

    def lookup(self, a_query) -> Sequence[JMDEntry]:
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
