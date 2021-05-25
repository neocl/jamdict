# -*- coding: utf-8 -*-

# jamdict's package version information
__author__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__copyright__ = "Copyright (c) 2016, Le Tuan Anh"
__credits__ = []
__license__ = "MIT License"
__description__ = "Python library for using Japanese dictionaries and resources (Jim Breen's JMdict, KanjiDic2, KRADFILE, JMnedict)"
__url__ = "https://github.com/neocl/jamdict"
__maintainer__ = "Le Tuan Anh"
# ------------------------------------------------------------------------------
# Version configuration (enforcing PEP 440)
# ------------------------------------------------------------------------------
__status__ = "3 - Alpha"
__version_tuple__ = (0, 1, 0, 11)
__version_status__ = ''  # a specific value ('rc', 'dev', etc.) or leave blank to be auto-filled
# ------------------------------------------------------------------------------
__status_map__ = {'3 - Alpha': 'a', '4 - Beta': 'b', '5 - Production/Stable': '', '6 - Mature': ''}
if not __version_status__:
    __version_status__ = __status_map__[__status__]
if len(__version_tuple__) == 3:
    __version_build__ = ''
elif len(__version_tuple__) == 4:
    __version_build__ = f"{__version_tuple__[3]}"
elif len(__version_tuple__) == 5:
    __version_build__ = f"{__version_tuple__[3]}.post{__version_tuple__[4]}"
else:
    raise ValueError("Invalid version information")
if __version_tuple__[2] == 0:
    __version_main__ = f"{'.'.join(str(n) for n in __version_tuple__[:2])}"
else:
    __version_main__ = f"{'.'.join(str(n) for n in __version_tuple__[:3])}"
__version__ = f"{__version_main__}{__version_status__}{__version_build__}"
__version_long__ = f"{__version_main__} - {__status__.split('-')[1].strip()} {__version_build__}"
