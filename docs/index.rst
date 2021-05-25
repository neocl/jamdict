
Jamdict's documentation!
========================

`Jamdict <https://github.com/neocl/jamdict>`_ is a Python 3 library for manipulating Jim Breen's JMdict, KanjiDic2, JMnedict and kanji-radical mappings.

Welcome
-------

Are you new to this documentation? Here are some useful pages:

- Want to try out Jamdict package? Try `Jamdict online demo <https://replit.com/@tuananhle/jamdict-demo>`_
- Want some useful code samples? See :ref:`recipes`.
- Want to look deeper into the package? See :ref:`api_index`.
- If you want to help developing Jamdict, please visit :ref:`contributing` page.

Main features
-------------

-  Support querying different Japanese language resources

   -  Japanese-English dictionary JMDict
   -  Kanji dictionary KanjiDic2
   -  Kanji-radical and radical-kanji maps KRADFILE/RADKFILE
   -  Japanese Proper Names Dictionary (JMnedict)

-  Fast look up (dictionaries are stored in SQLite databases)
-  Command-line lookup tool :ref:`(Example) <commandline>`
   
..
   Hide this for now
   -  jamdol (jamdol-flask) - a Python/Flask server that provides Jamdict lookup via REST API (experimental state)

:ref:`Contributors <contributors>` are welcome! 🙇.
If you want to help developing Jamdict, please visit :ref:`contributing` page.

Installation
------------

Jamdict and `jamdict-data <https://pypi.org/project/jamdict/>`_ are both `available on PyPI <https://pypi.org/project/jamdict/>`_ and
can be installed using pip.
For more information please see :ref:`installpage` page.

.. code:: bash

   pip install jamdict jamdict-data

Also, there is an online demo Jamdict virtual machine to try out on Repl.it

https://replit.com/@tuananhle/jamdict-demo

Sample jamdict Python code
--------------------------

Looking up words

   >>> from jamdict import Jamdict
   >>> jam = Jamdict()
   >>> result = jam.lookup('はな')
   >>> for word in result.entries:
   ...     print(word)
   ... 
   [id#1194500] はな (花) : 1. flower/blossom/bloom/petal ((noun (common) (futsuumeishi))) 2. cherry blossom 3. beauty 4. blooming (esp. of cherry blossoms) 5. ikebana 6. Japanese playing cards 7. (the) best
   [id#1486720] はな (鼻) : nose ((noun (common) (futsuumeishi)))
   [id#1581610] はし (端) : 1. end (e.g. of street)/tip/point/edge/margin ((noun (common) (futsuumeishi))) 2. beginning/start/first 3. odds and ends/scrap/odd bit/least
   [id#1634180] はな (洟) : snivel/nasal mucus/snot ((noun (common) (futsuumeishi)))

Looking up kanji characters

   >>> for c in result.chars:
   ...     print(repr(c))
   ... 
   花:7:flower
   華:10:splendor,flower,petal,shine,luster,ostentatious,showy,gay,gorgeous
   鼻:14:nose,snout
   端:14:edge,origin,end,point,border,verge,cape
   洟:9:tear,nasal discharge

Looking up named entities
   
   >>> result = jam.lookup('ディズニー%')
   >>> for name in result.names:
   ...     print(name)
   ... 
   [id#5053163] ディズニー : Disney (family or surname/company name)
   [id#5741091] ディズニーランド : Disneyland (place name)

See :ref:`recipes` for more code samples.

.. _commandline:

Command line tools
------------------

Jamdict can be used from the command line.

.. code:: bash

   python3 -m jamdict lookup 言語学
   ========================================
   Found entries
   ========================================
   Entry: 1264430 | Kj:  言語学 | Kn: げんごがく
   --------------------
   1. linguistics ((noun (common) (futsuumeishi)))

   ========================================
   Found characters
   ========================================
   Char: 言 | Strokes: 7
   --------------------
   Readings: yan2, eon, 언, Ngôn, Ngân, ゲン, ゴン, い.う, こと
   Meanings: say, word
   Char: 語 | Strokes: 14
   --------------------
   Readings: yu3, yu4, eo, 어, Ngữ, Ngứ, ゴ, かた.る, かた.らう
   Meanings: word, speech, language
   Char: 学 | Strokes: 8
   --------------------
   Readings: xue2, hag, 학, Học, ガク, まな.ぶ
   Meanings: study, learning, science

   No name was found.

To show help you may use

.. code:: bash

   python3 -m jamdict --help

Documentation
-------------

.. toctree::
   :maxdepth: 2

   install
   tutorials
   recipes
   api
   contributing
   updates

Other info
==========

Release Notes
-------------

Release notes is available :ref:`here <updates>`.

.. _contributors:
  
Contributors
------------

-  `Le Tuan Anh <https://github.com/letuananh>`__ (Maintainer)
-  `alt-romes <https://github.com/alt-romes>`__
-  `Matteo Fumagalli <https://github.com/matteofumagalli1275>`__
-  `Reem Alghamdi <https://github.com/reem-codes>`__
-  `Techno-coder <https://github.com/Techno-coder>`__

Useful links
------------

- jamdict on PyPI: https://pypi.org/project/jamdict/
- jamdict source code: https://github.com/neocl/jamdict/
- Documentation: https://jamdict.readthedocs.io/
- Dictionaries
   -  JMdict: http://edrdg.org/jmdict/edict_doc.html
   -  kanjidic2: https://www.edrdg.org/wiki/index.php/KANJIDIC_Project
   -  JMnedict: https://www.edrdg.org/enamdict/enamdict_doc.html
   -  KRADFILE: http://www.edrdg.org/krad/kradinf.html

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
