# -*- coding: utf-8 -*-

'''
Python library for manipulating Jim Breen's JMdict and KanjiDic2
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


__author__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__copyright__ = "Copyright 2016, jamdict"
__credits__ = []
__license__ = "MIT License"
__description__ = "Python library for manipulating Jim Breen's JMdict & KanjiDic2"
__url__ = "https://github.com/neocl/jamdict"
__maintainer__ = "Le Tuan Anh"
__version_major__ = "0.1"
__version__ = "{}a2".format(__version_major__)
__version_long__ = "{} - Alpha".format(__version_major__)
__status__ = "Prototype"

########################################################################

import logging

try:
    from .jmdict_sqlite import JMDictSQLite
    from .kanjidic2_sqlite import KanjiDic2SQLite
    from .util import Jamdict, JMDictXML, KanjiDic2XML
    __all__ = ['Jamdict', 'JMDictSQLite', 'JMDictXML', 'KanjiDic2SQLite', 'KanjiDic2XML']
except:
    logging.getLogger(__name__).exception("jamdict package was not loaded properly")
