Python library for manipulating Jim Breen's JMdict & KanjiDic2

# Main features

* Support querying different Japanese language resources
  - Japanese-English dictionary JMDict
  - Kanji dictionary KanjiDic2
  - Kanji-radical and radical-kanji maps KRADFILE/RADKFILE
  - Japanese Proper Names Dictionary (JMnedict) 
* Data are stored using SQLite database
* Console lookup tool
* jamdol (jamdol-flask) - a Python/Flask server that provides Jamdict lookup via REST API (experimental state)

Homepage: [https://github.com/neocl/jamdict](https://github.com/neocl/jamdict)

Contributors are welcome! 🙇

# Installation

Jamdict is available on PyPI at [https://pypi.org/project/jamdict/](https://pypi.org/project/jamdict/) and can be installed using pip command

```bash
pip install jamdict
# pip script sometimes doesn't work properly, so you may want to try this instead
python3 -m pip install jamdict
```

## Install data file

1. Download the offical, pre-compiled jamdict database (`jamdict-0.1a7.tar.xz`) from Google Drive [https://drive.google.com/drive/u/1/folders/1z4zF9ImZlNeTZZplflvvnpZfJp3WVLPk](https://drive.google.com/drive/u/1/folders/1z4zF9ImZlNeTZZplflvvnpZfJp3WVLPk)
2. Extract and copy `jamdict.db` to jamdict data folder (defaulted to `~/.jamdict/data/jamdict.db`)
3. To know where to copy data files
   
   ```bash
   # initial setup (this command will create ~/.jamdict for you
   # it will also tell you where to copy the data files
   python3 -m jamdict info
   # Jamdict 0.1a7
   # Python library for manipulating Jim Breen's JMdict, KanjiDic2, KRADFILE and JMnedict
   # 
   # Basic configuration
   # ------------------------------------------------------------
   # JAMDICT_HOME        : /home/tuananh/.jamdict
   # Config file location: /home/tuananh/.jamdict/config.json
   # 
   # Data files
   # ------------------------------------------------------------
   # Jamdict DB location: /home/tuananh/.jamdict/data/jamdict.db - [OK]
   # JMDict XML file    : /home/tuananh/.jamdict/data/JMdict_e.gz - [OK]
   # KanjiDic2 XML file : /home/tuananh/.jamdict/data/kanjidic2.xml.gz - [OK]
   # JMnedict XML file : /home/tuananh/.jamdict/data/JMnedict.xml.gz - [OK]
   ```

## Command line tools

To make sure that jamdict is configured properly, try to look up a word using command line

```bash
python3 -m jamdict.tools lookup 言語学
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
```

## Using KRAD/RADK mapping

Jamdict has built-in support for KRAD/RADK (i.e. kanji-radical and radical-kanji mapping).
The terminology of radicals/components used by Jamdict can be different from else where.

- A radical in Jamdict is a principal component, each character has only one radical.
- A character may be decomposed into several writing components.

By default jamdict provides two maps:

- jmd.krad is a Python dict that maps characters to list of components.
- jmd.radk is a Python dict that maps each available components to a list of characters.

```python
# Find all writing components (often called "radicals") of the character 雲
print(jmd.krad['雲'])
# ['一', '雨', '二', '厶']

# Find all characters with the component 鼎
chars = jmd.radk['鼎']
print(chars)
# {'鼏', '鼒', '鼐', '鼎', '鼑'}

# look up the characters info
result = jmd.lookup(''.join(chars))
for c in result.chars:
    print(c, c.meanings())
# 鼏 ['cover of tripod cauldron']
# 鼒 ['large tripod cauldron with small']
# 鼐 ['incense tripod']
# 鼎 ['three legged kettle']
# 鼑 []
```

## Finding name entities

```bash
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
```

## Exact matching

Use exact matching for faster search

```python
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

# Contributors

- [Matteo Fumagalli](https://github.com/matteofumagalli1275)
- [Reem Alghamdi](https://github.com/reem-codes)
