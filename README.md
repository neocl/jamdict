Python library for manipulating Jim Breen's JMdict & KanjiDic2

# Main features
* Query Japanese-English dictionary JMDict, KanjiDic2, and Japanese Proper Names Dictionary (JMnedict) using SQLite database
* Console lookup tool
* jamdol (jamdict-online) - REST API using Python/Flask (jamdol-flask), experimental state

Homepage: [https://github.com/neocl/jamdict](https://github.com/neocl/jamdict)

# Installation

Jamdict is available on PyPI at [https://pypi.org/project/jamdict/](https://pypi.org/project/jamdict/) and can be installed using pip command

```bash
pip install jamdict
# pip script sometimes doesn't work properly, so you may want to try this instead
python3 -m pip install jamdict
```

## Install data file

1. Download the offical, pre-compiled jamdict database from Google Drive [https://drive.google.com/drive/u/1/folders/1z4zF9ImZlNeTZZplflvvnpZfJp3WVLPk](https://drive.google.com/drive/u/1/folders/1z4zF9ImZlNeTZZplflvvnpZfJp3WVLPk)
2. To know where to copy data files
   
   ```bash
   # initial setup (this command will create ~/.jamdict for you
   # it will also tell you where to copy the data files
   python3 -m jamdict.tools info
   ```

## Command line tools

To make sure that jamdict is configured properly, try to look up a word using command line

```bash
python3 -m jamdict.tools lookup たべる
========================================
Found entries
========================================
Entry: 1358280 | Kj:  食べる, 喰べる | Kn: たべる
--------------------
1. to eat ((Ichidan verb|transitive verb))
2. to live on (e.g. a salary)/to live off/to subsist on

========================================
Found characters
========================================
Char: 食 | Strokes: 9
--------------------
Readings: shi2, si4, sig, sa, 식, 사, Thực, Tự, ショク, ジキ, く.う, く.らう, た.べる, は.む
Meanings: eat, food
Char: 喰 | Strokes: 12
--------------------
Readings: shi2, si4, sig, 식, Thặc, Thực, Tự, く.う, く.らう
Meanings: eat, drink, receive (a blow), (kokuji)
```

# Sample jamdict Python code

```python
from jamdict import Jamdict
jmd = Jamdict()

# use wildcard matching to find anything starts with 食べ and ends with る
result = jmd.lookup('食べ%る')

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

# Find all names with 鈴木 inside
result = jmd.lookup('%鈴木%')
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

# Find an entry (word, name entity) by idseq
result = jmd.lookup('id#5711308')
print(result.names[0])
# [id#5711308] すすき (鈴木) : Susuki (family or surname)
result = jmd.lookup('id#1467640')
print(result.entries[0])
# ねこ (猫) : 1. cat 2. shamisen 3. geisha 4. wheelbarrow 5. clay bed-warmer 6. bottom/submissive partner of a homosexual relationship

# use exact matching to increase searching speed (thanks to @reem-codes)
result = jmd.lookup('猫')

for entry in result.entries:
    print(entry)

# [id#1467640] ねこ (猫) : 1. cat ((noun (common) (futsuumeishi))) 2. shamisen 3. geisha 4. wheelbarrow 5. clay bed-warmer 6. bottom/submissive partner of a homosexual relationship
# [id#2698030] ねこま (猫) : cat ((noun (common) (futsuumeishi)))

```

See `jamdict_demo.py` and `jamdict/tools.py` for more information.

# Official website

* JMdict: [http://edrdg.org/jmdict/edict_doc.html](http://edrdg.org/jmdict/edict_doc.html)
* kanjidic2: [https://www.edrdg.org/wiki/index.php/KANJIDIC_Project](https://www.edrdg.org/wiki/index.php/KANJIDIC_Project)
* JMnedict: [https://www.edrdg.org/enamdict/enamdict_doc.html](https://www.edrdg.org/enamdict/enamdict_doc.html)
* KRADFILE: [http://www.edrdg.org/krad/kradinf.html](http://www.edrdg.org/krad/kradinf.html)
