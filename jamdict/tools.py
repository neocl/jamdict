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

import os

from chirptext import confirm, TextReport, Timer
from chirptext.cli import CLIApp, setup_logging

from jamdict import Jamdict
from jamdict import config

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------


JMD_XML = config.get_file('JMDICT_XML')
KD2_XML = config.get_file('KD2_XML')
JMD_DB = config.get_file('JAMDICT_DB')
setup_logging('logging.json', 'logs')


# -------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------

def get_jam(cli, args):
    if not args.jdb:
        args.jdb = None
    if args.kd2:
        cli.logger.warning("Jamdict database location: {}".format(args.jdb))
        cli.logger.warning("Kanjidic2 database location: {}".format(args.kd2))
        jmd = Jamdict(db_file=args.jdb, kd2_file=args.kd2, jmd_xml_file=args.jmdxml, kd2_xml_file=args.kd2xml)
    else:
        cli.logger.debug("Using the same database for both JMDict and Kanjidic2")
        jmd = Jamdict(db_file=args.jdb, kd2_file=args.jdb, jmd_xml_file=args.jmdxml, kd2_xml_file=args.kd2xml)
    if jmd.kd2 is None:
        cli.logger.warning("Kanjidic2 database could not be found")
    return jmd


def import_data(cli, args):
    '''Import XML data into SQLite database'''
    rp = TextReport()
    t = Timer(report=rp)
    db_loc = os.path.abspath(os.path.expanduser(args.jdb))
    rp.print("Jamdict DB location        : {}".format(db_loc))
    rp.print("JMDict XML file location   : {}".format(args.jmdxml))
    rp.print("Kanjidic2 XML file location: {}".format(args.kd2xml))
    jam = get_jam(cli, args)
    if args and (args.jdb or args.kd2):
        if os.path.isfile(db_loc):
            if not confirm("Database file exists. Do you want to overwite (This action cannot be undone! yes/no?) "):
                cli.logger.warning("Program aborted.")
                exit()
            else:
                os.unlink(db_loc)
        # perform input
        t.start("Creating Jamdict SQLite database. This process may take very long time ...")
        jam.import_data()
        t.stop()
    else:
        print("Database paths were not provided. Process aborted.")


def dump_result(results):
    if results.entries:
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
    else:
        print("No dictionary entry was found.")
    if results.chars:
        print("=" * 40)
        print("Found characters")
        print("=" * 40)
        for c in results.chars:
            print("Char: {} | Strokes: {}".format(c, c.stroke_count))
            print("-" * 20)
            for rmg in c.rm_groups:
                print("Readings:", ", ".join([r.value for r in rmg.readings]))
                print("Meanings:", ", ".join([m.value for m in rmg.meanings if not m.m_lang or m.m_lang == 'en']))
    else:
        print("No character was found.")


def lookup(cli, args):
    '''Lookup words by kanji/kana'''
    jam = get_jam(cli, args)
    results = jam.lookup(args.query)
    if args.format == 'json':
        print(results.to_json())
    else:
        if args.compact:
            print(results.text(separator='\n------\n', entry_sep='\n'))
        else:
            dump_result(results)


def file_status(file_path):
    real_path = os.path.abspath(os.path.expanduser(file_path))
    return '[NOT FOUND]' if not os.path.isfile(real_path) else '[OK]'


def show_info(cli, args):
    ''' Show jamdict configuration (data folder, configuration file location, etc.) '''
    print("Configuration location: {}".format(config._get_config_manager().locate_config()))
    print("-" * 40)
    print("Jamdict DB location   : {} - {}".format(args.jdb, file_status(args.jdb)))
    print("JMDict XML file       : {} - {}".format(args.jmdxml, file_status(args.jmdxml)))
    print("KanjiDic2 XML file    : {} - {}".format(args.kd2xml, file_status(args.kd2xml)))


# -------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------

def add_data_config(parser):
    parser.add_argument('-j', '--jmdxml', help='Path to JMdict XML file', default=JMD_XML)
    parser.add_argument('-k', '--kd2xml', help='Path to KanjiDic2 XML file', default=KD2_XML)
    parser.add_argument('-J', '--jdb', help='Path to JMDict SQLite file', default=JMD_DB)
    parser.add_argument('-K', '--kd2', help='Path to KanjiDic2 SQLite file', default=None)


def main():
    '''Main entry of jamtk
    '''
    app = CLIApp(desc='Jamdict toolkit', logger=__name__)
    add_data_config(app.parser)

    # import task
    import_task = app.add_task('import', func=import_data)
    add_data_config(import_task)

    # show info
    info_task = app.add_task('info', func=show_info)
    add_data_config(info_task)

    # look up task
    lookup_task = app.add_task('lookup', func=lookup)
    lookup_task.add_argument('query', help='kanji/kana')
    lookup_task.add_argument('-f', '--format', help='json or text')
    lookup_task.add_argument('--compact', action='store_true')
    lookup_task.set_defaults(func=lookup)
    add_data_config(lookup_task)

    # run app
    app.run()


if __name__ == "__main__":
    main()
