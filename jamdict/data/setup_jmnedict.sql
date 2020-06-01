/* Add meta info */
CREATE TABLE IF NOT EXISTS meta (
       key TEXT PRIMARY KEY NOT NULL,
       value TEXT NOT NULL
);

-------------------------------------------------------------------------------------
-- JMDict
-------------------------------------------------------------------------------------

CREATE TABLE NEEntry (
       idseq INTEGER NOT NULL UNIQUE
);

-------------------------------------------------------------------------------------
-- Kanji reading(s) of an entry
-------------------------------------------------------------------------------------
CREATE TABLE NEKanji (
       ID INTEGER PRIMARY KEY
       ,idseq INTEGER
       ,text TEXT
       ,FOREIGN KEY (idseq) REFERENCES Entry(idseq)
);

-------------------------------------------------------------------------------------
-- Kana reading(s) of an entry
-------------------------------------------------------------------------------------
CREATE TABLE NEKana (
       ID INTEGER PRIMARY KEY
       ,idseq INTEGER
       ,text TEXT
       ,nokanji BOOLEAN
       ,FOREIGN KEY (idseq) REFERENCES Entry(idseq)
);

-------------------------------------------------------------------------------------
-- Senses of an entry
-------------------------------------------------------------------------------------
CREATE TABLE NETranslation (
       ID INTEGER PRIMARY KEY
       ,idseq INTEGER
       ,FOREIGN KEY (idseq) REFERENCES Entry(idseq)
);

CREATE TABLE NETransType (
       tid INTEGER
       ,text TEXT
       ,FOREIGN KEY (tid) REFERENCES NETranslation(id)
);

CREATE TABLE NETransXRef (
       tid INTEGER
       ,text TEXT
       ,FOREIGN KEY (tid) REFERENCES NETranslation(id)
);

CREATE TABLE NETransGloss (
       tid INTEGER
       ,lang TEXT
       ,gend TEXT
       ,text TEXT
       ,FOREIGN KEY (tid) REFERENCES NETranslation(id)
);

-------------------------------------------------------------------------------------
-- INDICES - JMneDict
-------------------------------------------------------------------------------------

CREATE INDEX NEKanji_idseq ON NEKanji(idseq);
CREATE INDEX NEKanji_text ON NEKanji(text);

CREATE INDEX NEKana_idseq ON NEKana(idseq);
CREATE INDEX NEKana_text ON NEKana(text);

CREATE INDEX NETranslation_idseq ON NETranslation(idseq);
CREATE INDEX NETransType_tid ON NETransType(tid);
CREATE INDEX NETransType_text ON NETransType(text);
CREATE INDEX NETransXRef_tid ON NETransXRef(tid);
CREATE INDEX NETransXRef_text ON NETransXRef(text);
CREATE INDEX NETransGloss_tid ON NETransGloss(tid);
CREATE INDEX NETransGloss_lang ON NETransGloss(lang);
CREATE INDEX NETransGloss_text ON NETransGloss(text);

