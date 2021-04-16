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

