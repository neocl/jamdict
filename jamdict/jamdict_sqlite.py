#!/usr/bin/env python3
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
'''

# Copyright (c) 2017, Le Tuan Anh <tuananh.ke@gmail.com>
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

__author__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2017, jamdict"
__license__ = "MIT"
__maintainer__ = "Le Tuan Anh"
__version__ = "0.1"
__status__ = "Prototype"
__credits__ = []

########################################################################

import sys
import os
import logging
import argparse
from collections import namedtuple

from puchikarui import Schema
from . import jamdict
from .jamdict import JMDEntry, EntryInfo, Link, BibInfo, Audit, KanjiReading, KanaReading, Sense, SenseGloss, LSource

#-------------------------------------------------------------------------------
# CONFIGURATION
#-------------------------------------------------------------------------------

MY_FOLDER = os.path.dirname(os.path.abspath(__file__))
SCRIPT_FOLDER = os.path.join(MY_FOLDER, 'scripts')
JMD_SETUP_SCRIPT = os.path.join(SCRIPT_FOLDER, 'setup.sql')
JMDICT_VERSION = '1.08'
JMDICT_URL = 'http://www.csse.monash.edu.au/~jwb/edict.html'
JAMDICT_URL = 'https://github.com/neocl/jamdict'
SETUP_SCRIPT = '''INSERT INTO meta VALUES ('{jv}', '{ju}', 'jamdict', '{gv}', '{gu}')'''.format(
    jv=JMDICT_VERSION,
    ju=JMDICT_URL,
    gv=jamdict.__version__,
    gu=JAMDICT_URL
)


#-------------------------------------------------------------------------------
# MODELS
#-------------------------------------------------------------------------------

class JMDSchema(Schema):

    def __init__(self, data_source, setup_script=SETUP_SCRIPT, setup_file=JMD_SETUP_SCRIPT):
        Schema.__init__(self, data_source, setup_script=setup_script, setup_file=setup_file)
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
        # Meta
        self.add_table('meta', ['jmdict_version', 'jmdict_url', 'generator', 'generator_version', 'generator_url'])


class JMDSQLite(JMDSchema):

    def __init__(self, db_path):
        JMDSchema.__init__(self, db_path, setup_file=JMD_SETUP_SCRIPT)

    def search(self, query):
        eids = self.Entry.select("idseq IN (SELECT idseq FROM Kanji WHERE text like ?) OR idseq IN (SELECT idseq FROM Kana WHERE text like ?)", (query, query))
        entries = []
        with self.ds.open() as exe:
            for e in eids:
                entries.append(self.get_entry_with_context(e.idseq, exe=exe))
        return entries

    def get_entry(self, idseq, exe=None):
        if exe:
            return self.get_entry_with_context(idseq, exe)
        else:
            with self.ds.open() as new_context:
                return self.get_entry_with_context(idseq, new_context)

    def get_entry_with_context(self, idseq, exe):
        # select entry & info
        entry = JMDEntry(idseq)
        # links, bibs, etym, audit ...
        dblinks = self.Link.select('idseq=?', (idseq,), exe=exe)
        dbbibs = self.Bib.select('idseq=?', (idseq,), exe=exe)
        dbetym = self.Etym.select('idseq=?', (idseq,), exe=exe)
        dbaudit = self.Audit.select('idseq=?', (idseq,), exe=exe)
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
                    entry.info.audit.append(Audit(e.upd_date, e.upd_detl))

        # select kanji
        kanjis = self.Kanji.select('idseq=?', (idseq,), exe=exe)
        for dbkj in kanjis:
            kj = KanjiReading(dbkj.text)
            kjis = self.KJI.select('kid=?', (dbkj.ID,), exe=exe)
            for i in kjis:
                kj.info.append(i.text)
            kjps = self.KJP.select('kid=?', (dbkj.ID,), exe=exe)
            for p in kjps:
                kj.pri.append(p.text)
            entry.kanji_forms.append(kj)

        # select kana
        kanas = self.Kana.select('idseq=?', (idseq,), exe=exe)
        for dbkn in kanas:
            kn = KanaReading(dbkn.text, dbkn.nokanji)
            knis = self.KNI.select('kid=?', (dbkn.ID,), exe=exe)
            for i in knis:
                kn.info.append(i.text)
            knps = self.KNP.select('kid=?', (dbkn.ID,), exe=exe)
            for p in knps:
                kn.pri.append(p.text)
            knrs = self.KNR.select('kid=?', (dbkn.ID,), exe=exe)
            for r in knrs:
                kn.restr.append(r.text)
            entry.kana_forms.append(kn)

        # select senses
        senses = self.Sense.select('idseq=?', (idseq,), exe=exe)
        for dbs in senses:
            s = Sense()
            # stagk
            ks = self.stagk.select('sid=?', (dbs.ID,), exe=exe)
            for k in ks:
                s.stagk.append(k.text)
            # stagr
            rs = self.stagr.select('sid=?', (dbs.ID,), exe=exe)
            for r in rs:
                s.stagr.append(r.text)
            # pos
            ps = self.pos.select('sid=?', (dbs.ID,), exe=exe)
            for p in ps:
                s.pos.append(p.text)
            # xref
            xs = self.xref.select('sid=?', (dbs.ID,), exe=exe)
            for x in xs:
                s.xref.append(x.text)
            # antonym
            ans = self.antonym.select('sid=?', (dbs.ID,), exe=exe)
            for a in ans:
                s.antonym.append(a.text)
            # field
            fs = self.field.select('sid=?', (dbs.ID,), exe=exe)
            for f in fs:
                s.field.append(f.text)
            # misc
            ms = self.misc.select('sid=?', (dbs.ID,), exe=exe)
            for m in ms:
                s.misc.append(m.text)
            # SenseInfo
            sis = self.SenseInfo.select('sid=?', (dbs.ID,), exe=exe)
            for si in sis:
                s.info.append(si.text)
            # SenseSource
            lss = self.SenseSource.select('sid=?', (dbs.ID,), exe=exe)
            for ls in lss:
                s.lsource.append(LSource(ls.lang, ls.lstype, ls.wasei, ls.text))
            # dialect
            ds = self.dialect.select('sid=?', (dbs.ID,), exe=exe)
            for d in ds:
                s.dialect.append(d.text)
            # SenseGloss
            gs = self.SenseGloss.select('sid=?', (dbs.ID,), exe=exe)
            for g in gs:
                s.gloss.append(SenseGloss(g.lang, g.gend, g.text))
            entry.senses.append(s)
        return entry

    def insert(self, *entries, context=None):
        if context:
            for entry in entries:
                self.insert_with_context(entry, context)
        else:
            with self.ds.open() as new_context:
                for entry in entries:
                    self.insert_with_context(entry, new_context)

    def insert_with_context(self, entry, exe):
        self.Entry.insert((entry.idseq,), exe=exe)
        # insert info
        if entry.info:
            # links
            for lnk in entry.info.links:
                self.Link.insert((entry.idseq, lnk.tag, lnk.desc, lnk.uri), exe=exe)
            # bibs
            for bib in entry.info.bibinfo:
                self.Bib.insert((entry.idseq, bib.tag, bib.text), exe=exe)
            # etym
            for e in entry.info.etym:
                self.Etym.insert((entry.idseq, e), exe=exe)
            # audit
            for a in entry.info.audit:
                self.Audit.insert((entry.idseq, a.upd_date, a.upd_detl), exe=exe)
        # insert kanji
        for kj in entry.kanji_forms:
            kjid = self.Kanji.insert((entry.idseq, kj.text), exe=exe)
            # KJI
            for kji in kj.info:
                self.KJI.insert((kjid, kji), exe=exe)
            # KJP
            for kjp in kj.pri:
                self.KJP.insert((kjid, kjp), exe=exe)
            pass
        # insert kana
        for kn in entry.kana_forms:
            knid = self.Kana.insert((entry.idseq, kn.text, kn.nokanji), exe=exe)
            # KNI
            for kni in kn.info:
                self.KNI.insert((knid, kni), exe=exe)
            # KNP
            for knp in kn.pri:
                self.KNP.insert((knid, knp), exe=exe)
            # KNR
            for knr in kn.restr:
                self.KNR.insert((knid, knr), exe=exe)
            pass
        # insert senses
        for s in entry.senses:
            sid = self.Sense.insert((entry.idseq,), exe=exe)
            # stagk
            for sk in s.stagk:
                self.stagk.insert((sid, sk), exe=exe)
            # stagr
            for sr in s.stagr:
                self.stagr.insert((sid, sr), exe=exe)
            # pos
            for pos in s.stagr:
                self.pos.insert((sid, pos), exe=exe)
            # xref
            for xr in s.xref:
                self.xref.insert((sid, xr), exe=exe)
            # antonym
            for a in s.antonym:
                self.antonym.insert((sid, a), exe=exe)
            # field
            for f in s.field:
                self.field.insert((sid, f), exe=exe)
            # misc
            for m in s.misc:
                self.misc.insert((sid, m), exe=exe)
            # SenseInfo
            for i in s.info:
                self.SenseInfo.insert((sid, i), exe=exe)
            # SenseSource
            for l in s.lsource:
                self.SenseSource.insert((sid, l.text, l.lang, l.lstype, l.wasei), exe=exe)
            # dialect
            for d in s.dialect:
                self.dialect.insert((sid, d), exe=exe)
            # SenseGloss
            for g in s.gloss:
                self.SenseGloss.insert((sid, g.lang, g.gend, g.text), exe=exe)
