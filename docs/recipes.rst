.. _recipes:

Common Recipes
==============

- Search words using wildcards.
- Searching for kanji characters.
- Decomposing kanji characters into components, or search kanji characters by components.
- Search for named entities.

.. warning::
    👉 ⚠️ THIS SECTION IS STILL UNDER CONSTRUCTION ⚠️

All code here assumed that you have created a Jamdict object named :samp:`jam`, like this

    >>> from jamdict import Jamdict
    >>> jam = Jamdict()

High-performance tuning
-----------------------

When you need to do a lot of queries on the database, it is possible to load the whole database
into memory to boost up querying performance (This will takes about 400 MB of RAM) by using the ``memory_mode``
keyword argument, like this:

>>> from jamdict import Jamdict
>>> jam = Jamdict(memory_mode=True)

The first query will be extremely slow (it may take about a minute for the whole database to be loaded into memory)
but subsequent queries will be much faster.
    
Kanjis and radical/components (KRAD/RADK mappings)
--------------------------------------------------

Jamdict has built-in support for KRAD/RADK (i.e. kanji-radical and
radical-kanji mapping). The terminology of radicals/components used by
Jamdict can be different from else where.

-  A radical in Jamdict is a principal component, each character has
   only one radical.
-  A character may be decomposed into several writing components.

By default jamdict provides two maps:

-  jam.krad is a Python dict that maps characters to list of components.
-  jam.radk is a Python dict that maps each available components to a
   list of characters.

.. code:: python

   # Find all writing components (often called "radicals") of the character 雲
   print(jam.krad['雲'])
   # ['一', '雨', '二', '厶']

   # Find all characters with the component 鼎
   chars = jam.radk['鼎']
   print(chars)
   # {'鼏', '鼒', '鼐', '鼎', '鼑'}

   # look up the characters info
   result = jam.lookup(''.join(chars))
   for c in result.chars:
       print(c, c.meanings())
   # 鼏 ['cover of tripod cauldron']
   # 鼒 ['large tripod cauldron with small']
   # 鼐 ['incense tripod']
   # 鼎 ['three legged kettle']
   # 鼑 []

Finding name entities
---------------------

.. code:: bash

   # Find all names that contain the string 鈴木
   result = jam.lookup('%鈴木%')
   for name in result.names:
       print(name)

   # [id#5025685] キューティーすずき (キューティー鈴木) : Kyu-ti- Suzuki (1969.10-) (full name of a particular person)
   # [id#5064867] パパイヤすずき (パパイヤ鈴木) : Papaiya Suzuki (full name of a particular person)
   # [id#5089076] ラジカルすずき (ラジカル鈴木) : Rajikaru Suzuki (full name of a particular person)
   # [id#5259356] きつねざきすずきひなた (狐崎鈴木日向) : Kitsunezakisuzukihinata (place name)
   # [id#5379158] こすずき (小鈴木) : Kosuzuki (family or surname)
   # [id#5398812] かみすずき (上鈴木) : Kamisuzuki (family or surname)
   # [id#5465787] かわすずき (川鈴木) : Kawasuzuki (family or surname)
   # [id#5499409] おおすずき (大鈴木) : Oosuzuki (family or surname)
   # [id#5711308] すすき (鈴木) : Susuki (family or surname)
   # ...

Exact matching
--------------

Use exact matching for faster search

.. code:: python

   # Find an entry (word, name entity) by idseq
   result = jam.lookup('id#5711308')
   print(result.names[0])
   # [id#5711308] すすき (鈴木) : Susuki (family or surname)
   result = jam.lookup('id#1467640')
   print(result.entries[0])
   # ねこ (猫) : 1. cat 2. shamisen 3. geisha 4. wheelbarrow 5. clay bed-warmer 6. bottom/submissive partner of a homosexual relationship

   # use exact matching to increase searching speed (thanks to @reem-codes)
   result = jam.lookup('猫')

   for entry in result.entries:
       print(entry)

   # [id#1467640] ねこ (猫) : 1. cat ((noun (common) (futsuumeishi))) 2. shamisen 3. geisha 4. wheelbarrow 5. clay bed-warmer 6. bottom/submissive partner of a homosexual relationship
   # [id#2698030] ねこま (猫) : cat ((noun (common) (futsuumeishi)))

Low-level data queries
----------------------

It’s possible to access to the dictionary data by querying database directly using lower level APIs.
However these are prone to future changes so please keep that in mind.

When you create a Jamdict object, you have direct access to the
underlying databases, via these properties

.. code:: python

   from jamdict import Jamdict
   jam = Jamdict()
   >>> jam.jmdict    # jamdict.JMDictSQLite object for accessing word dictionary
   >>> jam.kd2       # jamdict.KanjiDic2SQLite object, for accessing kanji dictionary
   >>> jam.jmnedict  # jamdict.JMNEDictSQLite object, for accessing named-entities dictionary

You can perform database queries on each of these databases by obtaining
a database cursor with ``ctx()`` function (i.e. database query context).

For example the following code list down all existing part-of-speeches
in the database.

.. code:: python

   # returns a list of sqlite3.Row object
   pos_rows = jam.jmdict.ctx().select("SELECT DISTINCT text FROM pos")  

   # access columns in each query row by name
   all_pos = [x['text'] for x in pos_rows]  

   # sort all POS
   all_pos.sort()
   for pos in all_pos:
       print(pos)

For more information, please see `Jamdict database schema </_static/jamdict_db_schema.png>`_.

Say we want to get all irregular suru verbs, we can start with finding
all Sense IDs with pos = ``suru verb - irregular``, and then find all the
Entry idseq connected to those Senses.

Words (and also named entities) can be retrieved directly using their ``idseq``.
Each word may have many Senses (meaning) and each Sense may have different pos.

::

   # Entry (idseq) --(has many)--> Sense --(has many)--> pos

.. note::
   Tips: Since we hit the database so many times (to find the IDs, to retrieve
   each word, etc.), we also should consider to reuse the database
   connection using database context to have better performance
   (``with jam.jmdict.ctx() as ctx:`` and ``ctx=ctx`` in the code below).

Here is the sample code:

.. code:: python

   # find all idseq of lexical entry (i.e. words) that have at least 1 sense with pos = suru verb - irregular
   with jam.jmdict.ctx() as ctx:
       # query all word's idseqs
       rows = ctx.select(
           query="SELECT DISTINCT idseq FROM Sense WHERE ID IN (SELECT sid FROM pos WHERE text = ?) LIMIT 10000",
           params=("suru verb - irregular",))
       for row in rows:
           # reuse database connection with ctx=ctx for better performance
           word = jam.jmdict.get_entry(idseq=row['idseq'], ctx=ctx)
           print(word)
