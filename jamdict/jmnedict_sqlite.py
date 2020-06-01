# -*- coding: utf-8 -*-

'''
Japanese Multilingual Named Entity Dictionary (JMnedict) in SQLite format
Latest version can be found at https://github.com/neocl/jamdict

References:
    ENAMDICT/JMnedict - Japanese Proper Names Dictionary Files
        https://www.edrdg.org/enamdict/enamdict_doc.html

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# Copyright (c) 2020, Le Tuan Anh <tuananh.ke@gmail.com>
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

from puchikarui import Schema
from . import __version__ as JAMDICT_VERSION, __url__ as JAMDICT_URL
from .jmdict import Meta, JMDEntry, KanjiForm, KanaForm, Translation, SenseGloss


# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

MY_FOLDER = os.path.dirname(os.path.abspath(__file__))
SCRIPT_FOLDER = os.path.join(MY_FOLDER, 'data')
JMNEDICT_SETUP_FILE = os.path.join(SCRIPT_FOLDER, 'setup_jmnedict.sql')
JMNEDICT_VERSION = '1.08'
JMNEDICT_URL = 'https://www.edrdg.org/enamdict/enamdict_doc.html'
JMNEDICT_DATE = '2020-05-29'
JMNEDICT_SETUP_SCRIPT = '''INSERT INTO meta VALUES ('jmnedict.version', '{jv}');
INSERT INTO meta VALUES ('jmnedict.url', '{ju}');
INSERT INTO meta VALUES ('jmnedict.date', '{jud}');
INSERT INTO meta SELECT 'generator', 'jamdict' WHERE NOT EXISTS (SELECT 1 FROM meta WHERE key = 'generator');
INSERT INTO meta SELECT 'generator_version', '{gv}' WHERE NOT EXISTS (SELECT 1 FROM meta WHERE key = 'generator_version');
INSERT INTO meta SELECT 'generator_url', '{gu}' WHERE NOT EXISTS (SELECT 1 FROM meta WHERE key = 'generator_url');'''.format(
    jv=JMNEDICT_VERSION,
    ju=JMNEDICT_URL,
    jud=JMNEDICT_DATE,
    gv=JAMDICT_VERSION,
    gu=JAMDICT_URL
)


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Models
# -------------------------------------------------------------------------------

class JMNEDictSchema(Schema):

    def __init__(self, data_source=":memory:", setup_script=None, setup_file=None, *args, **kwargs):
        super().__init__(data_source, setup_script=setup_script, setup_file=setup_file, *args, **kwargs)
        self.add_script(JMNEDICT_SETUP_SCRIPT)
        self.add_file(JMNEDICT_SETUP_FILE)
        # Meta
        self.add_table('meta', ['key', 'value'], proto=Meta).set_id('key')
        self.add_table('NEEntry', ['idseq'])
        # Kanji
        self.add_table('NEKanji', ['ID', 'idseq', 'text'])
        # Kana
        self.add_table('NEKana', ['ID', 'idseq', 'text', 'nokanji'])
        # Translation (~Sense of JMdict)
        self.add_table('NETranslation', ['ID', 'idseq'])
        self.add_table('NETransType', ['tid', 'text'])
        self.add_table('NETransXRef', ['tid', 'text'])
        self.add_table('NETransGloss', ['tid', 'lang', 'gend', 'text'])


class JMNEDictSQLite(JMNEDictSchema):

    def __init__(self, db_path, setup_script=None, setup_file=None, *args, **kwargs):
        super().__init__(db_path, setup_script=setup_script, setup_file=setup_file, *args, **kwargs)

    def search_ne(self, query, ctx=None, **kwargs):
        # ensure context
        if ctx is None:
            with self.ctx() as ctx:
                return self.search(query, ctx=ctx)
        _is_wildcard_search = '_' in query or '@' in query or '%' in query
        if _is_wildcard_search:
            where = "idseq IN (SELECT idseq FROM NEKanji WHERE text like ?) OR idseq IN (SELECT idseq FROM NEKana WHERE text like ?) OR idseq IN (SELECT idseq FROM NETranslation JOIN NETransGloss ON NETranslation.ID == NETransGloss.tid WHERE NETransGloss.text like ?) OR idseq IN (SELECT idseq FROM NETranslation JOIN NETransType ON NETranslation.ID == NETransType.tid WHERE NETransType.text like ?)"
        else:
            where = "idseq IN (SELECT idseq FROM NEKanji WHERE text == ?) OR idseq IN (SELECT idseq FROM NEKana WHERE text == ?) OR idseq IN (SELECT idseq FROM NETranslation JOIN NETransGloss ON NETranslation.ID == NETransGloss.tid WHERE NETransGloss.text == ?) or idseq in (SELECT idseq FROM NETranslation JOIN NETransType ON NETranslation.ID == NETransType.tid WHERE NETransType.text == ?)"
        getLogger().debug(where)
        params = [query, query, query, query]
        try:
            if query.startswith('id#'):
                query_int = int(query[3:])
                if query_int >= 0:
                    getLogger().debug("Searching NE by ID: {}".format(query_int))
                    where = "idseq = ?"
                    params = [query_int]
        except Exception:
            pass
        # else (a context is provided)
        eids = self.NEEntry.select(where, params, ctx=ctx)
        entries = []
        for e in eids:
            entries.append(self.get_ne(e.idseq, ctx=ctx))
        return entries

    def get_ne(self, idseq, ctx=None):
        # ensure context
        if ctx is None:
            with self.ctx() as new_context:
                return self.get_entry(idseq, new_context)
        # else (a context is provided)
        # select entry & info
        entry = JMDEntry(idseq)
        # select kanji
        kanjis = ctx.NEKanji.select('idseq=?', (idseq,))
        for dbkj in kanjis:
            kj = KanjiForm(dbkj.text)
            entry.kanji_forms.append(kj)
        # select kana
        kanas = ctx.NEKana.select('idseq=?', (idseq,))
        for dbkn in kanas:
            kn = KanaForm(dbkn.text, dbkn.nokanji)
            entry.kana_forms.append(kn)
        # select senses
        senses = ctx.NETranslation.select('idseq=?', (idseq,))
        for dbs in senses:
            s = Translation()
            # name_type
            nts = ctx.NETransType.select('tid=?', (dbs.ID,))
            for nt in nts:
                s.name_type.append(nt.text)
            # xref
            xs = ctx.NETransXRef.select('tid=?', (dbs.ID,))
            for x in xs:
                s.xref.append(x.text)
            # SenseGloss
            gs = ctx.NETransGloss.select('tid=?', (dbs.ID,))
            for g in gs:
                s.gloss.append(SenseGloss(g.lang, g.gend, g.text))
            entry.senses.append(s)
        return entry

    def insert_name_entities(self, entries, ctx=None):
        # ensure context
        if ctx is None:
            with self.ctx() as new_context:
                return self.insert_name_entities(entries, ctx=new_context)
        # else
        for entry in entries:
            self.insert_name_entity(entry, ctx)

    def insert_name_entity(self, entry, ctx=None):
        # ensure context
        if ctx is None:
            with self.ctx() as ctx:
                return self.insert_name_entity(entry, ctx=ctx)
        # else (a context is provided)
        self.NEEntry.insert(entry.idseq, ctx=ctx)
        # insert kanji
        for kj in entry.kanji_forms:
            ctx.NEKanji.insert(entry.idseq, kj.text)
        # insert kana
        for kn in entry.kana_forms:
            ctx.NEKana.insert(entry.idseq, kn.text, kn.nokanji)
        # insert translations
        for s in entry.senses:
            tid = ctx.NETranslation.insert(entry.idseq)
            # insert name_type
            for nt in s.name_type:
                ctx.NETransType.insert(tid, nt)
            # xref
            for xr in s.xref:
                ctx.NETransXRef.insert(tid, xr)
            # Gloss
            for g in s.gloss:
                ctx.NETransGloss.insert(tid, g.lang, g.gend, g.text)
