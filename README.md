Python library for manipulating Jim Breen's JMdict & KanjiDic2

# Main features
* Query JMDict and KanjiDic2 in XML format directly (but slow)
* Convert JMDict and KanjiDic2 into SQLite format for faster access
* Basic console lookup tool
* jamdol (jamdict-online) - REST API using Python/Flask (jamdol-flask)

# Installation

```bash
pip install jamdict
# pip script sometimes doesn't work properly, so you may want to try this instead
python3 -m pip install jamdict
```

## Data
XML files (JMdict_e.xml, kanjidic2.xml) must be downloaded from JMdict home page and copy into `~/local/jamdict/data`

Read more about JMdict here: http://www.csse.monash.edu.au/~jwb/edict.html

# Sample codes

```python
>>> from jamdict import Jamdict
>>> jmd = Jamdict("/home/tuananh/local/jamdict/data/jamdict.db")
>>> jmd.lookup('食べる')
<jamdict.util.LookupResult object at 0x7fc70775a710>
>>> result = jmd.lookup('食べる')
>>> print(result.entries)
[ID:1358280|たべる|食べる|1. to eat ((Ichidan verb|transitive verb))|2. to live on (e.g. a salary)/to live off/to subsist on]
>>> for c in result.chars:
...     print(c, c.rm_groups)
... 
喰 [R: shi2, si4, sig, 식, Thặcÿ, Thựcÿ, Tự,ÿ く.う, く.らう | M: eat, drink, receive (a blow), (kokuji)]
食 [R: shi2, si4, sig, sa, 식, 사, Thực, Tự, ショク, ジキ, く.う, く.らう, た.べる, は.む | M: eat, food, manger, nourriture, alimento, comida, eclipse, comer, comer, comida, alimento]
```

See `jamdict_demo.py` and `jamdict/tools.py` for more information.
