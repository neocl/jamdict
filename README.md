Python library for manipulating Jim Breen's JMdict & KanjiDic2

# Main features
* Query JMDict and KanjiDic2 in XML format directly (but slow)
* Convert JMDict and KanjiDic2 into SQLite format for faster access
* Basic console lookup tool
* jamdol (jamdict-online) - REST API using Python/Flask (jamdol-flask)

# Installation

Homepage: [https://github.com/neocl/jamdict](https://github.com/neocl/jamdict)

```bash
pip install jamdict
# pip script sometimes doesn't work properly, so you may want to try this instead
python3 -m pip install jamdict

# initial setup (this command will create ~/.jamdict for you
# it will also tell you where to copy the data files
python3 -m jamdict.tools info

# to look up a word using command line
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

## Data
XML files (JMdict_e.xml, kanjidic2.xml) must be downloaded and copy into `~/.jamdict/data`

I have mirrored these files to Google Drive so you can download there too:
[https://drive.google.com/drive/folders/1z4zF9ImZlNeTZZplflvvnpZfJp3WVLPk](https://drive.google.com/drive/folders/1z4zF9ImZlNeTZZplflvvnpZfJp3WVLPk)

Official website

* JMdict: [http://edrdg.org/jmdict/edict_doc.html](http://edrdg.org/jmdict/edict_doc.html)
* kanjidic2: [http://www.edrdg.org/kanjidic/kanjd2index.html](http://www.edrdg.org/kanjidic/kanjd2index.html)
* KRADFILE: [http://www.edrdg.org/krad/kradinf.html](http://www.edrdg.org/krad/kradinf.html)


# Sample codes

```python
>>> from jamdict import Jamdict
>>> jmd = Jamdict()
# use wildcard matching to find anything starts with 食べ and ends with る
>>> result = jmd.lookup('食べ%る')
# print all found word entries
>>> for entry in result.entries:
...     print(entry)
...
[id#1358280] たべる (食べる) : 1. to eat ((Ichidan verb|transitive verb)) 2. to live on (e.g. a salary)/to live off/to subsist on
[id#1358300] たべすぎる (食べ過ぎる) : to overeat ((Ichidan verb|transitive verb))
[id#1852290] たべつける (食べ付ける) : to be used to eating ((Ichidan verb|transitive verb))
[id#2145280] たべはじめる (食べ始める) : to start eating ((Ichidan verb))
[id#2449430] たべかける (食べ掛ける) : to start eating ((Ichidan verb))
[id#2671010] たべなれる (食べ慣れる) : to be used to eating/to become used to eating/to be accustomed to eating/to acquire a taste for ((Ichidan verb))
[id#2765050] たべられる (食べられる) : 1. to be able to eat ((Ichidan verb|intransitive verb)) 2. to be edible/to be good to eat ((pre-noun adjectival (rentaishi)))
[id#2795790] たべくらべる (食べ比べる) : to taste and compare several dishes (or foods) of the same type ((Ichidan verb|transitive verb))
[id#2807470] たべあわせる (食べ合わせる) : to eat together (various foods) ((Ichidan verb))
# print all related characters
>>> for c in result.chars:
...     print(repr(c))
... 
食:9:eat,food
喰:12:eat,drink,receive (a blow),(kokuji)
過:12:overdo,exceed,go beyond,error
付:5:adhere,attach,refer to,append
始:8:commence,begin
掛:11:hang,suspend,depend,arrive at,tax,pour
慣:14:accustomed,get used to,become experienced
比:4:compare,race,ratio,Philippines
合:6:fit,suit,join,0.1

# use exact matching to increase searching speed (thanks to @reem-codes)
result = jmd.lookup('食べる')

>>> for entry in result.entries:
...     print(entry)
... 
[id#1358280] たべる (食べる) : 1. to eat ((Ichidan verb|transitive verb)) 2. to live on (e.g. a salary)/to live off/to subsist on
```

See `jamdict_demo.py` and `jamdict/tools.py` for more information.
