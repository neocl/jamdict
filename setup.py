#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Setup script for jamdict
Latest version can be found at https://github.com/neocl/jamdict

References:
    Python documentation:
        https://docs.python.org/
    argparse module:
        https://docs.python.org/3/howto/argparse.html
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
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

import io
import os
from setuptools import setup

import jamdict


########################################################################

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


readme_file = 'README.rst' if os.path.isfile('README.rst') else 'README.md'
print("README file: {}".format(readme_file))
long_description = read(readme_file)

setup(
    name='jamdict',
    version=jamdict.__version__,
    url=jamdict.__url__,
    project_urls={
        "Bug Tracker": "https://github.com/neocl/jamdict/issues",
        "Source Code": "https://github.com/neocl/jamdict/"
    },
    keywords="japanese dictionary sqlite xml",
    license=jamdict.__license__,
    author=jamdict.__author__,
    tests_require=['lxml', 'puchikarui'],
    install_requires=['lxml', 'puchikarui'],
    author_email=jamdict.__email__,
    description=jamdict.__description__,
    long_description=long_description,
    packages=['jamdict'],
    package_data={'jamdict': ['scripts/*.sql']},
    include_package_data=True,
    platforms='any',
    test_suite='test',
    # Reference: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=['Programming Language :: Python',
                 'Development Status :: 2 - Pre-Alpha',
                 'Natural Language :: Japanese',
                 'Environment :: Plugins',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: {}'.format(jamdict.__license__),
                 'Operating System :: OS Independent',
                 'Topic :: Database',
                 'Topic :: Text Processing :: Linguistic',
                 'Topic :: Software Development :: Libraries :: Python Modules']
)
