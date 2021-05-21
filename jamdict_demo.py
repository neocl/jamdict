#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Jamdict demo application

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
"""

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

import json
from jamdict import Jamdict

########################################################################

# Create an instance of Jamdict
jam = Jamdict()
print("Jamdict DB file: {}".format(jam.db_file))

if not jam.ready:
    print("""Jamdict DB is not available. Database can be installed via PyPI:

    pip install jamdict-data

Or downloaded from: https://jamdict.readthedocs.io/en/latest/install.html
To create a config file, run:

    python3 -m jamdict config

Program aborted.""")
    exit()

# Lookup by kana
result = jam.lookup('おかえし')
for entry in result.entries:
    print(entry)

# Lookup by kanji
print("-----------------")
result = jam.lookup('御土産')
for entry in result.entries:
    print(entry)

# Lookup a name
# a name entity is also a jamdict.jmdict.JMDEntry object
# excep that the senses is a list of Translation objects instead of Sense objects
print("-----------------")
if jam.has_jmne():
    result = jam.lookup('鈴木')
    for name in result.names:
        print(name)

# Use wildcard matching
# Find all names ends with -jida
print("-----------------")
result = jam.lookup('%じだ')
for name in result.names:
    print(name)

# ------------------------------------------------------------------------------
# lookup entry by idseq
print("---------------------")
otenki = jam.lookup('id#1002470').entries[0]
# extract all kana forms
kana_forms = ' '.join([x.text for x in otenki.kana_forms])
# extract all kanji forms
kanji_forms = ' '.join([x.text for x in otenki.kanji_forms])
print("Entry #{id}: Kanji: {kj} - Kana: {kn}".format(id=otenki.idseq, kj=kanji_forms, kn=kana_forms))

# extract all sense glosses
for idx, sense in enumerate(otenki):
    print("{i}. {s}".format(i=idx, s=sense))

# Look up radical & writing components of kanji characters
# 1. Lookup kanji's components
print("---------------------")
result = jam.lookup('筋斗雲')
for c in result.chars:
    meanings = ', '.join(c.meanings())
    # has components
    print(f"{c}: {meanings}")
    print(f"    Radical: {c.radical}")
    print(f"    Components: {c.components}")

# 2. Lookup kanjis by component
print("---------------------")
chars = jam.radk['鼎']  # this returns a list of strings (each string is the literal of a character)
result = jam.lookup(''.join(chars))
for c in result.chars:
    meanings = ', '.join(c.meanings())
    # has components
    print(f"{c}: {meanings}")
    print(f"    Radical: {c.radical}")
    print(f"    Components: {c.components}")

# using JSON
print("---------------------")
result = jam.lookup('こうしえん')
print(result.text(separator='\n'))
print("---------------------")
otenki_dict = result.to_json()  # get a dict structure to produce a JSON string
json_string = json.dumps(otenki_dict, ensure_ascii=False, indent=2)
print(json_string)
