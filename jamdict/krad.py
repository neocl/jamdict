# -*- coding: utf-8 -*-

'''
Module for retrieving kanji components (i.e. radicals)
Latest version can be found at https://github.com/neocl/jamdict

This package uses the RADKFILE/KRADFILE[1] file.
These files are the property of the [Electronic Dictionary Research and Development Group][2], and are used in conformance with the Group's [licence][3].

[1]: http://www.edrdg.org/krad/kradinf.html
[2]: http://www.edrdg.org/
[3]: http://www.edrdg.org/edrdg/licence.html

References:
    JMDict website:
        http://www.csse.monash.edu.au/~jwb/edict.html
    Python documentation:
        https://docs.python.org/
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

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

import os
import logging
import threading
from collections import OrderedDict
from collections import defaultdict as dd
from lxml import etree

from chirptext import chio
from chirptext.sino import Radical

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
MY_FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(MY_FOLDER, 'data')
KRADFILE = os.path.join(DATA_FOLDER, 'kradfile-u.gz')
RADKFILE = os.path.join(DATA_FOLDER, 'radkfile.gz')

logger = logging.getLogger(__name__)


########################################################################

class KRad:
    def __init__(self, **kwargs):
        """ Kanji Radical management
        """
        self.__krad_map = None
        self.__radk_map = None
        self.__rads = {}
        self.lock = threading.Lock()

    def _build_krad_map(self):
        with self.lock:
            lines = chio.read_file(KRADFILE, mode='rt').splitlines()
            # build the krad map
            self.__krad_map = {}
            self.__radk_map = dd(set)
            for line in lines:
                if line.startswith("#"):
                    continue
                else:
                    parts = line.split(':', maxsplit=1)
                    if len(parts) == 2:
                        rads = [r.strip() for r in parts[1].split()]
                        char_literal = parts[0].strip()
                        self.__krad_map[char_literal] = rads
                        for rad in rads:
                            self.__radk_map[rad].add(char_literal)

    @property
    def radk(self):
        if self.__radk_map is None:
            self._build_krad_map()
        return self.__radk_map

    @property
    def krad(self):
        if self.__krad_map is None:
            self._build_krad_map()
        return self.__krad_map
