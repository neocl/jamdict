#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Jamdict toolkit
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
from jamdict import JMDict

#-------------------------------------------------------------------------------
# CONFIGURATION
#-------------------------------------------------------------------------------

DATA_FOLDER = os.path.abspath(os.path.expanduser('./data'))
JMD_XML = os.path.join(DATA_FOLDER, 'JMdict')
JMD_DB = os.path.join(DATA_FOLDER, 'jamdict.db')


#-------------------------------------------------------------------------------
# FUNCTIONS
#-------------------------------------------------------------------------------

def import_data(args):
    print("Importing data: from {} ==to==> {}".format(args.xml, args.sqlite))
    print("Reading XML file ...")
    jmd = JMDict(args.xml, args.sqlite)
    print("writing to SQLite ...")
    jmd.import_data()
    print("Done!")


def lookup(args):
    jmd = JMDict(dbfile=args.sqlite)
    entries = jmd.lookup(args.query)
    if args.format == 'json':
        print([e.to_json() for e in entries])
    else:
        for e in entries:
            print("Entry: {}".format(e))
            for idx, s in enumerate(e.senses):
                print("{}. {}".format(idx, s))
            print('')


#-------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------

def main():
    '''Main entry of jamtk
    '''

    # It's easier to create a user-friendly console application by using argparse
    # See reference at the top of this script
    parser = argparse.ArgumentParser(description="Jamdict toolkit")

    # Positional argument(s)
    task = parser.add_subparsers(help='Task to be done')

    # Optional arguments
    parser.add_argument('-x', '--xml', help='Path to JMdict XML file', default=JMD_XML)
    parser.add_argument('-s', '--sqlite', help='Path to JMdict SQLite file', default=JMD_DB)

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
