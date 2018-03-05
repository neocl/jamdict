#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Jamdict console app
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

import sys
import os
import logging
import argparse
from jamdict import Jamdict

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

DEFAULT_HOME = os.path.abspath(os.path.expanduser('~/local/jamdict'))
DATA_FOLDER = os.path.join(os.environ.get('JAMDICT_HOME', DEFAULT_HOME), 'data')
JMD_XML = os.path.join(DATA_FOLDER, 'JMdict.xml')
KD2_XML = os.path.join(DATA_FOLDER, 'kanjidic2.xml')
JMD_DB = os.path.join(DATA_FOLDER, 'jamdict.db')


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------

def get_jam(args):
    if args.jdb == args.kd2 or not args.kd2:
        jmd = Jamdict(db_file=args.jdb, jmd_xml_file=args.jmdxml, kd2_xml_file=args.kd2xml)
    else:
        jmd = Jamdict(db_file=args.jdb, kd2_file=args.kd2, jmd_xml_file=args.jmdxml, kd2_xml_file=args.kd2xml)
    return jmd


def import_data(args):
    if args and (args.jdb or args.kd2):
        # perform input
        jam = get_jam(args)
        print("Importing data. This process may take very long time ...")
        jam.import_data()
        print("Done!")
    else:
        print("Database paths were not provided. Process aborted.")


def lookup(args):
    jam = get_jam(args)
    results = jam.lookup(args.query)
    if args.format == 'json':
        print(results.to_json())
    else:
        print("=" * 40)
        print("Found entries")
        print("=" * 40)
        for e in results.entries:
            kj = ', '.join([k.text for k in e.kanji_forms])
            kn = ', '.join([k.text for k in e.kana_forms])
            print("Entry: {} | Kj:  {} | Kn: {}".format(e.idseq, kj, kn))
            print("-" * 20)
            for idx, s in enumerate(e.senses):
                print("{idx}. {s}".format(idx=idx + 1, s=s))
            print('')
        print("=" * 40)
        print("Found characters")
        print("=" * 40)
        for c in results.chars:
            print("Char: {} | Strokes: {}".format(c, c.stroke_count))
            print("-" * 20)
            for rmg in c.rm_groups:
                print("Readings:", ", ".join([r.value for r in rmg.readings]))
                print("Meanings:", ", ".join([m.value for m in rmg.meanings if not m.m_lang or m.m_lang == 'en']))


# -------------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------------

def main():
    '''Main entry of jamtk
    '''

    # It's easier to create a user-friendly console application by using argparse
    # See reference at the top of this script
    parser = argparse.ArgumentParser(description="Jamdict toolkit")

    # Positional argument(s)
    task = parser.add_subparsers(help='Task to be done')

    # Optional arguments
    parser.add_argument('-j', '--jmdxml', help='Path to JMdict XML file', default=JMD_XML)
    parser.add_argument('-k', '--kd2xml', help='Path to KanjiDic2 XML file', default=KD2_XML)
    parser.add_argument('-J', '--jdb', help='Path to JMDict SQLite file', default=JMD_DB)
    parser.add_argument('-K', '--kd2', help='Path to KanjiDic2 SQLite file', default=JMD_DB)

    # import task
    import_task = task.add_parser('import', help='Import XML data into SQLite database')
    import_task.set_defaults(func=import_data)

    # look up task
    lookup_task = task.add_parser('lookup', help='Lookup words by kanji/kana')
    lookup_task.add_argument('query', help='kanji/kana')
    lookup_task.add_argument('-f', '--format', help='json or text')
    lookup_task.set_defaults(func=lookup)

    # Main script
    if len(sys.argv) == 1:
        # User didn't pass any value in, show help
        parser.print_help()
    else:
        args = parser.parse_args()
        args.func(args)


if __name__ == "__main__":
    main()
