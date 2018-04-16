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
- JMdict: [http://edrdg.org/jmdict/edict_doc.html](http://edrdg.org/jmdict/edict_doc.html)
- kanjidic2: [http://www.edrdg.org/kanjidic/kanjd2index.html](http://www.edrdg.org/kanjidic/kanjd2index.html)
- KRADFILE: [http://www.edrdg.org/krad/kradinf.html](http://www.edrdg.org/krad/kradinf.html)


# Sample codes

```python
>>> from jamdict import Jamdict
>>> jmd = Jamdict()
>>> jmd.lookup('食べる')
'Entries: たべる(食べる):1. to eat2. to live on (e.g. a salary)/to live off/to subsist on | Chars: 食, 喰'
>>> result = jmd.lookup('食べる')
>>> print(result.entries)
[たべる (食べる) : 1. to eat 2. to live on (e.g. a salary)/to live off/to subsist on]
>>> for c in result.chars:
...     print(c, c.rm_groups)
... 
食 [R: shi2, si4, sig, sa, 식, 사, Thực, Tự, ショク, ジキ, く.う, く.らう, た.べる, は.む | M: eat, food, manger, nourriture, alimento, comida, eclipse, comer, comer, comida, alimento]
喰 [R: shi2, si4, sig, 식, Thặc, Thực, Tự, く.う, く.らう | M: eat, drink, receive (a blow), (kokuji)]
```

See `jamdict_demo.py` and `jamdict/tools.py` for more information.
