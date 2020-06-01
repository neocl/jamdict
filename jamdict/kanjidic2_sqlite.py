# -*- coding: utf-8 -*-

'''
KanjiDic2 in SQLite format
Latest version can be found at https://github.com/neocl/jamdict

References:
    KANJIDIC2 project
        https://www.edrdg.org/wiki/index.php/KANJIDIC_Project 

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
from .jmdict import Meta
from .kanjidic2 import Character, CodePoint, Radical, Variant, DicRef, QueryCode, RMGroup, Reading, Meaning

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

MY_FOLDER = os.path.dirname(os.path.abspath(__file__))
SCRIPT_FOLDER = os.path.join(MY_FOLDER, 'data')
KANJIDIC2_VERSION = '1.6'
KANJIDIC2_URL = 'https://www.edrdg.org/wiki/index.php/KANJIDIC_Project'
KANJIDIC2_DATE = 'April 2008'
KANJIDIC2_SETUP_FILE = os.path.join(SCRIPT_FOLDER, 'setup_kanjidic2.sql')
KANJIDIC2_SETUP_SCRIPT = '''
INSERT INTO meta VALUES ('kanjidic2.version', '{kdv}');
INSERT INTO meta VALUES ('kanjidic2.url', '{kdu}');
INSERT INTO meta VALUES ('kanjidic2.date', '{kdd}');
INSERT INTO meta SELECT 'generator', 'jamdict'
WHERE NOT EXISTS (SELECT 1 FROM meta WHERE key='generator');
INSERT INTO meta SELECT 'generator_version', '{gv}'
WHERE NOT EXISTS (SELECT 1 FROM meta WHERE key='generator_version');
INSERT INTO meta SELECT 'generator_url', '{gu}'
WHERE NOT EXISTS (SELECT 1 FROM meta WHERE key='generator_url');'''.format(
    kdv=KANJIDIC2_VERSION,
    kdu=KANJIDIC2_URL,
    kdd=KANJIDIC2_DATE,
    gv=JAMDICT_VERSION,
    gu=JAMDICT_URL
)


def getLogger():
    return logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Models
# ------------------------------------------------------------------------------

class KanjiDic2Schema(Schema):

    KEY_FILE_VER = 'kanjidic2.file_version'
    KEY_DB_VER = 'kanjidic2.database_version'
    KEY_CREATED_DATE = 'kanjidic2.date_of_creation'

    def __init__(self, data_source, setup_script=None, setup_file=None, *args, **kwargs):
        super().__init__(data_source, setup_script=setup_script, setup_file=setup_file, *args, **kwargs)
        self.add_file(KANJIDIC2_SETUP_FILE)
        self.add_script(KANJIDIC2_SETUP_SCRIPT)
        # Meta
        self.add_table('meta', ['key', 'value'], proto=Meta).set_id('key')
        self.add_table('character', ['ID', 'literal', 'stroke_count', 'grade', 'freq', 'jlpt'], proto=Character, alias="char").set_id('ID')
        self.add_table('codepoint', ['cid', 'cp_type', 'value'], proto=CodePoint)
        self.add_table('radical', ['cid', 'rad_type', 'value'], proto=Radical)
        self.add_table('stroke_miscount', ['cid', 'value'], alias="smc")
        self.add_table('variant', ['cid', 'var_type', 'value'], proto=Variant)
        self.add_table('rad_name', ['cid', 'value'])
        self.add_table('dic_ref', ['cid', 'dr_type', 'value', 'm_vol', 'm_page'], proto=DicRef)
        self.add_table('query_code', ['cid', 'qc_type', 'value', 'skip_misclass'], proto=QueryCode)
        self.add_table('nanori', ['cid', 'value'])
        self.add_table('rm_group', ['ID', 'cid'], proto=RMGroup, alias='rmg').set_id('ID')
        self.add_table('reading', ['gid', 'r_type', 'value', 'on_type', 'r_status'], proto=Reading)
        self.add_table('meaning', ['gid', 'value', 'm_lang'], proto=Meaning)


class KanjiDic2SQLite(KanjiDic2Schema):

    def __init__(self, db_path, setup_script=None, setup_file=None, *args, **kwargs):
        super().__init__(db_path, setup_script=setup_script, setup_file=setup_file, *args, **kwargs)

    def update_meta(self, file_version, database_version, date_of_creation, ctx=None):
        # ensure context
        if ctx is None:
            with self.ctx() as new_context:
                return self.update_meta(file_version, database_version, date_of_creation, new_context)
        # else
        # file_version
        fv = ctx.meta.by_id(self.KEY_FILE_VER)
        if not fv:
            ctx.meta.insert(self.KEY_FILE_VER, file_version)
        else:
            fv.value = file_version
            ctx.meta.save(fv)
        # database_version
        dv = ctx.meta.by_id(self.KEY_DB_VER)
        if not dv:
            ctx.meta.insert(self.KEY_DB_VER, database_version)
        else:
            dv.value = database_version
            ctx.meta.save(dv)
        # date_of_creation
        doc = ctx.meta.by_id(self.KEY_CREATED_DATE)
        if not doc:
            ctx.meta.insert(self.KEY_CREATED_DATE, date_of_creation)
        else:
            doc.value = date_of_creation
            ctx.meta.save(doc)

    def insert_chars(self, chars, ctx=None):
        # ensure context
        if ctx is None:
            with self.ctx() as ctx:
                return self.insert_chars(chars, ctx=ctx)
        # else
        for c in chars:
            self.insert_char(c, ctx=ctx)

    def insert_char(self, c, ctx=None):
        # ensure context
        if ctx is None:
            with self.ctx() as ctx:
                return self.insert_char(c, ctx=ctx)
        # else
        c.ID = ctx.character.save(c)
        # save codepoints
        for cp in c.codepoints:
            cp.cid = c.ID
            ctx.codepoint.save(cp)
        # radicals
        for r in c.radicals:
            r.cid = c.ID
            ctx.radical.save(r)
        # stroke_miscount
        for smc in c.stroke_miscounts:
            ctx.smc.insert(c.ID, smc)
        # variants
        for v in c.variants:
            v.cid = c.ID
            ctx.variant.save(v)
        # radnames
        for rn in c.rad_names:
            ctx.rad_name.insert(c.ID, rn)
        # dic_refs
        for dr in c.dic_refs:
            dr.cid = c.ID
            ctx.dic_ref.save(dr)
        # query_codes
        for qc in c.query_codes:
            qc.cid = c.ID
            ctx.query_code.save(qc)
        # nanoris
        for n in c.nanoris:
            ctx.nanori.insert(c.ID, n)
        # reading groups
        for rmg in c.rm_groups:
            rmg.cid = c.ID
            rmg.ID = ctx.rmg.save(rmg)
            # save readings inside
            for r in rmg.readings:
                r.gid = rmg.ID
                ctx.reading.save(r)
            # save meanings inside
            for m in rmg.meanings:
                m.gid = rmg.ID
                ctx.meaning.save(m)

    def get_char(self, literal, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.get_char(literal, ctx=ctx)
        # context was ensured
        c = ctx.char.select_single('literal=?', (literal,))
        if not c:
            getLogger().debug("character {} could not be found".format(literal))
            return None
        else:
            return self.char_by_id(c.ID, ctx)

    def char_by_id(self, cid, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.select_char(cid, ctx=ctx)
        # context was ensured
        c = ctx.char.by_id(cid)
        c.codepoints = ctx.codepoint.select('cid=?', (cid,))
        c.radicals = ctx.radical.select('cid=?', (cid,))
        for smc in ctx.smc.select('cid=?', (cid,)):
            c.stroke_miscounts.append(smc.value)
        c.variants = ctx.variant.select('cid=?', (cid,))
        for r in ctx.rad_name.select('cid=?', (cid,)):
            c.rad_names.append(r.value)
        c.dic_refs = ctx.dic_ref.select('cid=?', (cid,))
        c.query_codes = ctx.query_code.select('cid=?', (cid,))
        for n in ctx.nanori.select('cid=?', (cid,)):
            c.nanoris.append(n.value)
        c.rm_groups = ctx.rmg.select('cid=?', (cid,))
        for rmg in c.rm_groups:
            rmg.readings = ctx.reading.select('gid=?', (rmg.ID,))
            rmg.meanings = ctx.meaning.select('gid=?', (rmg.ID,))
        return c
