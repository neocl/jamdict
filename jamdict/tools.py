# -*- coding: utf-8 -*-

"""
Jamdict console app
"""

# This code is a part of jamdict library: https://github.com/neocl/jamdict
# :copyright: (c) 2017 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import json
import logging

from chirptext import confirm, TextReport, Timer
from chirptext.cli import CLIApp, setup_logging

import jamdict

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

if os.path.isfile('logging.json'):
    setup_logging('logging.json', 'logs')
else:
    setup_logging(os.path.join(jamdict.config.home_dir(), 'logging.json'), 'logs')


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------

def get_jam(cli, args):
    if not args.jdb:
        args.jdb = None
    if args.config:
        jamdict.config.read_config(args.config)
    if args.kd2 or args.jmne:
        cli.logger.warning("Jamdict database location: {}".format(args.jdb))
        cli.logger.warning("Kanjidic2 database location: {}".format(args.kd2))
        jmd = jamdict.Jamdict(db_file=args.jdb, kd2_file=args.kd2,
                              jmd_xml_file=args.jmdxml,
                              kd2_xml_file=args.kd2xml,
                              jmnedict_file=args.jmne,
                              jmnedict_xml_file=args.jmnexml)
    else:
        cli.logger.debug("Using the same database for both JMDict and Kanjidic2")
        jmd = jamdict.Jamdict(db_file=args.jdb,
                              kd2_file=args.jdb,
                              jmnedict_file=args.jdb,
                              jmd_xml_file=args.jmdxml,
                              kd2_xml_file=args.kd2xml,
                              jmnedict_xml_file=args.jmnexml)
    if jmd.kd2 is None:
        cli.logger.warning("Kanjidic2 database could not be found")
    return jmd


def import_data(cli, args):
    '''Generate Jamdict SQLite database from XML data files'''
    rp = TextReport()
    t = Timer(report=rp)
    db_loc = os.path.abspath(os.path.expanduser(args.jdb))
    show_info(cli, args)
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


def dump_result(results, report=None):
    if report is None:
        report = TextReport()
    if results.entries:
        report.print("=" * 40)
        report.print("Found entries")
        report.print("=" * 40)
        for e in results.entries:
            kj = ', '.join([k.text for k in e.kanji_forms])
            kn = ', '.join([k.text for k in e.kana_forms])
            report.print("Entry: {} | Kj:  {} | Kn: {}".format(e.idseq, kj, kn))
            report.print("-" * 20)
            for idx, s in enumerate(e.senses):
                report.print("{idx}. {s}".format(idx=idx + 1, s=s))
            report.print('')
    else:
        report.print("No dictionary entry was found.")
    if results.chars:
        report.print("=" * 40)
        report.print("Found characters")
        report.print("=" * 40)
        for c in results.chars:
            report.print("Char: {} | Strokes: {}".format(c, c.stroke_count))
            report.print("-" * 20)
            for rmg in c.rm_groups:
                report.print("Readings:", ", ".join([r.value for r in rmg.readings]))
                report.print("Meanings:", ", ".join([m.value for m in rmg.meanings if not m.m_lang or m.m_lang == 'en']))
            report.print('')
        report.print('')
    else:
        report.print("No character was found.")
    if results.names:
        report.print("=" * 40)
        report.print("Found name entities")
        report.print("=" * 40)
        for e in results.names:
            kj = ', '.join([k.text for k in e.kanji_forms])
            kn = ', '.join([k.text for k in e.kana_forms])
            report.print("Names: {} | Kj:  {} | Kn: {}".format(e.idseq, kj, kn))
            report.print("-" * 20)
            for idx, s in enumerate(e.senses):
                report.print("{idx}. {s}".format(idx=idx + 1, s=s))
            report.print('')
    else:
        report.print("No name was found.")


def lookup(cli, args):
    '''Lookup words by kanji/kana'''
    jam = get_jam(cli, args)
    if jam.ready:
        results = jam.lookup(args.query, strict_lookup=args.strict)
        report = TextReport(args.output)
        if args.format == 'json':
            report.print(json.dumps(results.to_json(),
                                    ensure_ascii=args.ensure_ascii,
                                    indent=args.indent if args.indent else None))
        else:
            if args.compact:
                report.print(results.text(separator='\n------\n', entry_sep='\n'))
            else:
                dump_result(results, report=report)
    else:
        getLogger().warning(f"Jamdict database is not available.\nThere are 3 ways to install data: \n    1) install jamdict_data via PyPI using `pip install jamdict_data` \n    2) download prebuilt dictionary database file from: {jamdict.__url__}, \n    3) or build your own database file from XML source files.")


def file_status(file_path):
    if file_path:
        real_path = os.path.abspath(os.path.expanduser(file_path))
        if os.path.isfile(real_path):
            return '[OK]'
    return '[NOT FOUND]'


def hello_jamdict(cli, args):
    ''' Say hello and test if Jamdict is working '''
    jam = get_jam(cli, args)
    if jam.ready:
        results = jam.lookup("一期一会")
        dump_result(results, report=TextReport())
    else:
        getLogger().warning("Hello there, unfortunately jamdict data is not available. Please try to install using `pip install jamdict-data`")


def show_info(cli, args):
    ''' Show jamdict configuration (data folder, configuration file location, etc.) '''
    output = TextReport(args.output) if 'output' in args else TextReport()
    if args.config:
        jamdict.config.read_config(args.config)
    output.print("Jamdict " + jamdict.version_info.__version__)
    output.print(jamdict.version_info.__description__)
    jam = get_jam(cli, args)
    output.header("Basic configuration")
    jamdict_home = jamdict.config.home_dir()
    if not os.path.isdir(jamdict_home):
        jamdict_home += " [Missing]"
    output.print(f"JAMDICT_HOME        : {jamdict_home}")
    if jamdict.util._JAMDICT_DATA_AVAILABLE:
        import jamdict_data
        data_pkg = f"version {jamdict_data.__version__} [OK]"
    else:
        data_pkg = "Not installed"
    output.print(f"jamdict-data        : {data_pkg}")
    if args.config:
        _config_path = args.config + " [Custom]"
        if not os.path.isfile(args.config):
            _config_path += " [Missing]"
    else:
        _config_path = jamdict.config._get_config_manager().locate_config()
    if not _config_path:
        _config_path = "Not available.\n     Run `python3 -m jamdict config` to create configuration file if needed."
    output.print(f"Config file location: {_config_path}")

    output.header("Data files")
    output.print(f"Jamdict DB location: {jam.db_file} - {file_status(jam.db_file)}")
    output.print(f"JMDict XML file    : {jam.jmd_xml_file} - {file_status(jam.jmd_xml_file)}")
    output.print(f"KanjiDic2 XML file : {jam.kd2_xml_file} - {file_status(jam.kd2_xml_file)}")
    output.print(f"JMnedict XML file : {jam.jmnedict_xml_file} - {file_status(jam.jmnedict_xml_file)}")

    if jam.ready:
        output.header("Jamdict database metadata")
        try:
            for meta in jam.jmdict.meta.select():
                output.print(f"{meta.key}: {meta.value}")
        except Exception as e:
            print(e)
            output.print("Error happened while retrieving database meta data")
    output.header("Others")
    output.print(f"lxml availability: {jamdict.jmdict._LXML_AVAILABLE}")


def show_version(cli, args):
    ''' Show Jamdict version '''
    if args.verbose:
        print("Jamdict {v} - {d}".format(d=jamdict.version_info.__description__, v=jamdict.version_info.__version__))
    else:
        print("Jamdict {}".format(jamdict.version_info.__version__))


def config_jamdict(cli, args):
    ''' Create Jamdict configuration file '''
    if args.config:
        jamdict.config._ensure_config(args.config)
    else:
        jamdict.config._ensure_config()
    show_info(cli, args)


# -------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------

def add_data_config(parser):
    parser.add_argument('-c', '--config', help='Path to Jamdict config file (i.e. ~/.jamdict/config.json)', default=None)
    parser.add_argument('-J', '--jdb', help='Path to JMDict SQLite file', default=None)
    parser.add_argument('-j', '--jmdxml', help='Path to JMdict XML file', default=None)
    parser.add_argument('-k', '--kd2xml', help='Path to KanjiDic2 XML file', default=None)
    parser.add_argument('-e', '--jmnexml', help='Path to JMnedict XML file', default=None)
    parser.add_argument('-K', '--kd2', help='Path to KanjiDic2 SQLite file', default=None)
    parser.add_argument('-E', '--jmne', help='Path to JMnedict SQLite file', default=None)


def main():
    '''Main entry of jamtk
    '''
    app = CLIApp(desc='Jamdict command-line toolkit', logger=__name__, show_version=show_version)
    add_data_config(app.parser)

    # import task
    import_task = app.add_task('import', func=import_data)
    add_data_config(import_task)

    # show info
    info_task = app.add_task('info', func=show_info)
    info_task.add_argument('-o', '--output', help='Write information to a text file')
    add_data_config(info_task)

    # show version
    version_task = app.add_task('version', func=show_version)
    add_data_config(version_task)

    # create config file
    config_task = app.add_task('config', func=config_jamdict)
    add_data_config(config_task)

    # hello
    hello_task = app.add_task('hello', func=hello_jamdict)
    add_data_config(hello_task)

    # look up task
    lookup_task = app.add_task('lookup', func=lookup)
    lookup_task.add_argument('query', help='kanji/kana')
    lookup_task.add_argument('-f', '--format', help='json or text')
    lookup_task.add_argument('--compact', action='store_true')
    lookup_task.add_argument('-s', '--strict', action='store_true')
    lookup_task.add_argument('--ensure_ascii', help='Force JSON dumps to ASCII only', action='store_true')
    lookup_task.add_argument('--indent', help='JSON default indent', default=2, type=int)
    lookup_task.add_argument('-o', '--output', help='Path to a file to output lookup result, leave blank to write to console standard output')
    lookup_task.set_defaults(func=lookup)
    add_data_config(lookup_task)

    # run app
    app.run()


if __name__ == "__main__":
    main()
