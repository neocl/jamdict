.. _updates:

Jamdict Changelog
=================

jamdict 0.1a11
--------------

-  2021-05-25

  - Added ``lookup_iter()`` for iteration search
  - Added ``pos`` filter for filtering words by part-of-speeches
  - Added ``all_pos()`` and ``all_ne_type()`` to Jamdict to list part-of-speeches and named-entity types
  - Better version checking in ``__version__.py``
  - Improved documentation

-  2021-05-29

   - (.post1) Sorted kanji readings to have on & kun readings listed first
   - (.post1) Add ``on_readings``, ``kun_readings``, and ``other_readings`` filter to ``kanjidic2.RMGroup``

jamdict 0.1a10
--------------

-  2021-05-19

  - Added ``memory_mode`` keyword to load database into memory before querying to boost up performance
  - Improved import performance by using puchikarui's ``buckmode``
  - Tested with both puchikarui 0.1.* and 0.2.*

jamdict 0.1a9
-------------

-  2021-04-19

  -  Fix data audit query
  -  Enhanced ``Jamdict()`` constructor. ``Jamdict('/path/to/jamdict.db')``
     works properly.
  -  Code quality review
  -  Automated documentation build via
     `readthedocs.org <https://jamdict.readthedocs.io/en/latest/>`__

jamdict 0.1a8
-------------

-  2021-04-15

  -  Make ``lxml`` optional
  -  Data package can be installed via PyPI with ``jamdict_data`` package
  -  Make configuration file optional as data files can be installed via PyPI.

jamdict 0.1a7
-------------

-  2020-05-31

  -  Added Japanese Proper Names Dictionary (JMnedict) support
  -  Included built-in KRADFILE/RADKFile support
  -  Improved command line tools (json, compact mode, etc.)

Older versions
--------------

- 2017-08-18

  -  Support KanjiDic2 (XML/SQLite formats)

- 2016-11-09

  -  Release first version to Github
