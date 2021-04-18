# -*- coding: utf-8 -*-

'''
JMDict in SQLite format
Latest version can be found at https://github.com/neocl/jamdict

References:
    Python documentation:
        https://docs.python.org/
    PEP 0008 - Style Guide for Python Code
        https://www.python.org/dev/peps/pep-0008/
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# Copyright (c) 2017, Le Tuan Anh <tuananh.ke@gmail.com>
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
from .jmdict import Meta, JMDEntry, EntryInfo, Link, BibInfo, Audit, KanjiForm, KanaForm, Sense, SenseGloss, LSource


# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

MY_FOLDER = os.path.dirname(os.path.abspath(__file__))
SCRIPT_FOLDER = os.path.join(MY_FOLDER, 'data')
JMDICT_SETUP_FILE = os.path.join(SCRIPT_FOLDER, 'setup_jmdict.sql')
JMDICT_VERSION = '1.08'
JMDICT_URL = 'http://www.csse.monash.edu.au/~jwb/edict.html'
SETUP_SCRIPT = '''INSERT INTO meta VALUES ('jmdict.version', '{jv}');
INSERT INTO meta VALUES ('jmdict.url', '{ju}');
INSERT INTO meta VALUES ('generator', 'jamdict');
INSERT INTO meta VALUES ('generator_version', '{gv}');
INSERT INTO meta VALUES ('generator_url', '{gu}');'''.format(
    jv=JMDICT_VERSION,
    ju=JMDICT_URL,
    gv=JAMDICT_VERSION,
    gu=JAMDICT_URL
)


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Models
# -------------------------------------------------------------------------------

class JMDictSchema(Schema):

    KEY_JMD_VER = "jmdict.version"
    KEY_JMD_URL = "jmdict.url"

    def __init__(self, data_source=":memory:", setup_script=None, setup_file=None, *args, **kwargs):
        super().__init__(data_source, setup_script=setup_script, setup_file=setup_file, *args, **kwargs)
        self.add_script(SETUP_SCRIPT)
        self.add_file(JMDICT_SETUP_FILE)
        # Meta
        self.add_table('meta', ['key', 'value'], proto=Meta).set_id('key')
        self.add_table('Entry', ['idseq'])
        self.add_table('Link', ['ID', 'idseq', 'tag', 'desc', 'uri'])
        self.add_table('Bib', ['ID', 'idseq', 'tag', 'text'])
        self.add_table('Etym', ['idseq', 'text'])
        self.add_table('Audit', ['idseq', 'upd_date', 'upd_detl'])
        # Kanji
        self.add_table('Kanji', ['ID', 'idseq', 'text'])
        self.add_table('KJI', ['kid', 'text'])
        self.add_table('KJP', ['kid', 'text'])
        # Kana
        self.add_table('Kana', ['ID', 'idseq', 'text', 'nokanji'])
        self.add_table('KNI', ['kid', 'text'])
        self.add_table('KNP', ['kid', 'text'])
        self.add_table('KNR', ['kid', 'text'])
        # Senses
        self.add_table('Sense', ['ID', 'idseq'])
        self.add_table('stagk', ['sid', 'text'])
        self.add_table('stagr', ['sid', 'text'])
        self.add_table('pos', ['sid', 'text'])
        self.add_table('xref', ['sid', 'text'])
        self.add_table('antonym', ['sid', 'text'])
        self.add_table('field', ['sid', 'text'])
        self.add_table('misc', ['sid', 'text'])
        self.add_table('SenseInfo', ['sid', 'text'])
        self.add_table('SenseSource', ['sid', 'text', 'lang', 'lstype', 'wasei'])
        self.add_table('dialect', ['sid', 'text'])
        self.add_table('SenseGloss', ['sid', 'lang', 'gend', 'text'])


class JMDictSQLite(JMDictSchema):

    def __init__(self, db_path, setup_script=None, setup_file=None, *args, **kwargs):
        super().__init__(db_path, setup_script=setup_script, setup_file=setup_file, *args, **kwargs)

    def update_meta(self, version, url, ctx=None):
        # create a default context if none was provided
        if ctx is None:
            with self.open(ctx) as ctx:
                return self.update_meta(version, url, ctx=ctx)
        # else (a context is provided)
        # version
        jv = ctx.meta.by_id(self.KEY_JMD_VER)
        if not jv:
            ctx.meta.insert(self.KEY_JMD_VER, version)
        else:
            jv.value = version
            ctx.meta.save(jv)
        # url
        ju = ctx.meta.by_id(self.KEY_JMD_URL)
        if not ju:
            ctx.meta.insert(self.KEY_JMD_URL, version)
        else:
            ju.value = url
            ctx.meta.save(ju)

    def search(self, query, ctx=None, **kwargs):
        # ensure context
        if ctx is None:
            with self.ctx() as ctx:
                return self.search(query, ctx=ctx)
        _is_wildcard_search = '_' in query or '@' in query or '%' in query
        if _is_wildcard_search:
            where = "idseq IN (SELECT idseq FROM Kanji WHERE text like ?) OR idseq IN (SELECT idseq FROM Kana WHERE text like ?) OR idseq IN (SELECT idseq FROM sense JOIN sensegloss ON sense.ID == sensegloss.sid WHERE text like ?)"
        else:
            where = "idseq IN (SELECT idseq FROM Kanji WHERE text == ?) OR idseq IN (SELECT idseq FROM Kana WHERE text == ?) OR idseq IN (SELECT idseq FROM sense JOIN sensegloss ON sense.ID == sensegloss.sid WHERE text == ?)"
        getLogger().debug(where)
        params = [query, query, query]
        try:
            if query.startswith('id#'):
                query_int = int(query[3:])
                if query_int >= 0:
                    getLogger().debug("Searching by ID: {}".format(query_int))
                    where = "idseq = ?"
                    params = [query_int]
        except Exception:
            pass
        # else (a context is provided)
        eids = self.Entry.select(where, params, ctx=ctx)
        entries = []
        for e in eids:
            entries.append(self.get_entry(e.idseq, ctx=ctx))
        return entries

    def get_entry(self, idseq, ctx=None):
        # ensure context
        if ctx is None:
            with self.ctx() as new_context:
                return self.get_entry(idseq, new_context)
        # else (a context is provided)
        # select entry & info
        entry = JMDEntry(idseq)
        # links, bibs, etym, audit ...
        dblinks = ctx.Link.select('idseq=?', (idseq,))
        dbbibs = ctx.Bib.select('idseq=?', (idseq,))
        dbetym = ctx.Etym.select('idseq=?', (idseq,))
        dbaudit = ctx.Audit.select('idseq=?', (idseq,))
        if dblinks or dbbibs or dbetym or dbaudit:
            entry.info = EntryInfo()
            if dblinks:
                for l in dblinks:
                    entry.info.links.append(Link(l.tag, l.desc, l.uri))
            if dbbibs:
                for b in dbbibs:
                    entry.info.bibinfo.append(BibInfo(b.tag, b.text))
            if dbetym:
                for e in dbetym:
                    entry.info.etym.append(e)
            if dbaudit:
                for a in dbaudit:
                    entry.info.audit.append(Audit(a.upd_date, a.upd_detl))
        # select kanji
        kanjis = ctx.Kanji.select('idseq=?', (idseq,))
        for dbkj in kanjis:
            kj = KanjiForm(dbkj.text)
            kjis = ctx.KJI.select('kid=?', (dbkj.ID,))
            for i in kjis:
                kj.info.append(i.text)
            kjps = ctx.KJP.select('kid=?', (dbkj.ID,))
            for p in kjps:
                kj.pri.append(p.text)
            entry.kanji_forms.append(kj)
        # select kana
        kanas = ctx.Kana.select('idseq=?', (idseq,))
        for dbkn in kanas:
            kn = KanaForm(dbkn.text, dbkn.nokanji)
            knis = ctx.KNI.select('kid=?', (dbkn.ID,))
            for i in knis:
                kn.info.append(i.text)
            knps = ctx.KNP.select('kid=?', (dbkn.ID,))
            for p in knps:
                kn.pri.append(p.text)
            knrs = ctx.KNR.select('kid=?', (dbkn.ID,))
            for r in knrs:
                kn.restr.append(r.text)
            entry.kana_forms.append(kn)
        # select senses
        senses = ctx.Sense.select('idseq=?', (idseq,))
        for dbs in senses:
            s = Sense()
            # stagk
            ks = ctx.stagk.select('sid=?', (dbs.ID,))
            for k in ks:
                s.stagk.append(k.text)
            # stagr
            rs = ctx.stagr.select('sid=?', (dbs.ID,))
            for r in rs:
                s.stagr.append(r.text)
            # pos
            ps = ctx.pos.select('sid=?', (dbs.ID,))
            for p in ps:
                s.pos.append(p.text)
            # xref
            xs = ctx.xref.select('sid=?', (dbs.ID,))
            for x in xs:
                s.xref.append(x.text)
            # antonym
            ans = ctx.antonym.select('sid=?', (dbs.ID,))
            for a in ans:
                s.antonym.append(a.text)
            # field
            fs = ctx.field.select('sid=?', (dbs.ID,))
            for f in fs:
                s.field.append(f.text)
            # misc
            ms = ctx.misc.select('sid=?', (dbs.ID,))
            for m in ms:
                s.misc.append(m.text)
            # SenseInfo
            sis = ctx.SenseInfo.select('sid=?', (dbs.ID,))
            for si in sis:
                s.info.append(si.text)
            # SenseSource
            lss = ctx.SenseSource.select('sid=?', (dbs.ID,))
            for ls in lss:
                s.lsource.append(LSource(ls.lang, ls.lstype, ls.wasei, ls.text))
            # dialect
            ds = ctx.dialect.select('sid=?', (dbs.ID,))
            for d in ds:
                s.dialect.append(d.text)
            # SenseGloss
            gs = ctx.SenseGloss.select('sid=?', (dbs.ID,))
            for g in gs:
                s.gloss.append(SenseGloss(g.lang, g.gend, g.text))
            entry.senses.append(s)
        return entry

    def insert_entries(self, entries, ctx=None):
        # ensure context
        if ctx is None:
            with self.ctx() as new_context:
                return self.insert_entries(entries, ctx=new_context)
        # else
        getLogger().debug("JMdict bulk insert {} entries".format(len(entries)))
        for entry in entries:
            self.insert_entry(entry, ctx)

    def insert_entry(self, entry, ctx=None):
        # ensure context
        if ctx is None:
            with self.ctx() as ctx:
                return self.insert_entry(entry, ctx=ctx)
        # else (a context is provided)
        self.Entry.insert(entry.idseq, ctx=ctx)
        # insert info
        if entry.info:
            # links
            for lnk in entry.info.links:
                ctx.Link.insert(entry.idseq, lnk.tag, lnk.desc, lnk.uri)
            # bibs
            for bib in entry.info.bibinfo:
                ctx.Bib.insert(entry.idseq, bib.tag, bib.text)
            # etym
            for e in entry.info.etym:
                ctx.Etym.insert(entry.idseq, e)
            # audit
            for a in entry.info.audit:
                ctx.Audit.insert(entry.idseq, a.upd_date, a.upd_detl)
        # insert kanji
        for kj in entry.kanji_forms:
            kjid = ctx.Kanji.insert(entry.idseq, kj.text)
            # KJI
            for kji in kj.info:
                ctx.KJI.insert(kjid, kji)
            # KJP
            for kjp in kj.pri:
                ctx.KJP.insert(kjid, kjp)
        # insert kana
        for kn in entry.kana_forms:
            knid = ctx.Kana.insert(entry.idseq, kn.text, kn.nokanji)
            # KNI
            for kni in kn.info:
                ctx.KNI.insert(knid, kni)
            # KNP
            for knp in kn.pri:
                ctx.KNP.insert(knid, knp)
            # KNR
            for knr in kn.restr:
                ctx.KNR.insert(knid, knr)
        # insert senses
        for s in entry.senses:
            sid = ctx.Sense.insert(entry.idseq)
            # stagk
            for sk in s.stagk:
                ctx.stagk.insert(sid, sk)
            # stagr
            for sr in s.stagr:
                ctx.stagr.insert(sid, sr)
            # pos
            for pos in s.pos:
                ctx.pos.insert(sid, pos)
            # xref
            for xr in s.xref:
                ctx.xref.insert(sid, xr)
            # antonym
            for a in s.antonym:
                ctx.antonym.insert(sid, a)
            # field
            for f in s.field:
                ctx.field.insert(sid, f)
            # misc
            for m in s.misc:
                ctx.misc.insert(sid, m)
            # SenseInfo
            for i in s.info:
                ctx.SenseInfo.insert(sid, i)
            # SenseSource
            for l in s.lsource:
                ctx.SenseSource.insert(sid, l.text, l.lang, l.lstype, l.wasei)
            # dialect
            for d in s.dialect:
                ctx.dialect.insert(sid, d)
            # SenseGloss
            for g in s.gloss:
                ctx.SenseGloss.insert(sid, g.lang, g.gend, g.text)
