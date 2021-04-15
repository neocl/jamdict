Tutorials
=========

Getting started
---------------

Just install :keyword:`jamdict` and :keyword:`jamdict_data` packages via pip and you are ready to go.

.. code:: python

   from jamdict import Jamdict
   jam = Jamdict()

The most useful function is :func:`jamdict.util.Jamdict.lookup`.
For example:

.. code:: python

   # use wildcard matching to find any word, or Kanji character, or name
   # that starts with 食べ and ends with る
   result = jam.lookup('食べ%る')

To access the result object you may use:

.. code:: python

   # print all word entries
   for entry in result.entries:
        print(entry)

   # [id#1358280] たべる (食べる) : 1. to eat ((Ichidan verb|transitive verb)) 2. to live on (e.g. a salary)/to live off/to subsist on
   # [id#1358300] たべすぎる (食べ過ぎる) : to overeat ((Ichidan verb|transitive verb))
   # [id#1852290] たべつける (食べ付ける) : to be used to eating ((Ichidan verb|transitive verb))
   # [id#2145280] たべはじめる (食べ始める) : to start eating ((Ichidan verb))
   # [id#2449430] たべかける (食べ掛ける) : to start eating ((Ichidan verb))
   # [id#2671010] たべなれる (食べ慣れる) : to be used to eating/to become used to eating/to be accustomed to eating/to acquire a taste for ((Ichidan verb))
   # [id#2765050] たべられる (食べられる) : 1. to be able to eat ((Ichidan verb|intransitive verb)) 2. to be edible/to be good to eat ((pre-noun adjectival (rentaishi)))
   # [id#2795790] たべくらべる (食べ比べる) : to taste and compare several dishes (or foods) of the same type ((Ichidan verb|transitive verb))
   # [id#2807470] たべあわせる (食べ合わせる) : to eat together (various foods) ((Ichidan verb))

   # print all related characters
   for c in result.chars:
       print(repr(c))

   # 食:9:eat,food
   # 喰:12:eat,drink,receive (a blow),(kokuji)
   # 過:12:overdo,exceed,go beyond,error
   # 付:5:adhere,attach,refer to,append
   # 始:8:commence,begin
   # 掛:11:hang,suspend,depend,arrive at,tax,pour
   # 慣:14:accustomed,get used to,become experienced
   # 比:4:compare,race,ratio,Philippines
   # 合:6:fit,suit,join,0.1
