CREATE TABLE Entry (
       idseq INTEGER NOT NULL UNIQUE
);

-- Entry's links (EntryInfo)
CREATE TABLE Link (
       id INTEGER PRIMARY KEY
       ,idseq INTEGER
       ,tag TEXT
       ,desc TEXT
       ,uri TEXT
       ,FOREIGN KEY (idseq) REFERENCES Entry(idseq)
);

-- Entry's bibinfo (EntryInfo)
CREATE TABLE Bib (
       id INTEGER PRIMARY KEY
       ,idseq INTEGER
       ,tag TEXT
       ,text TEXT
       ,FOREIGN KEY (idseq) REFERENCES Entry(idseq)
);

-- Entry's etym (EntryInfo)
CREATE TABLE Etym (
       idseq INTEGER
       ,text TEXT
       ,FOREIGN KEY (idseq) REFERENCES Entry(idseq)
);

-- Entry's audit (EntryInfo)
CREATE TABLE Audit (
       idseq INTEGER
       ,udp_date TEXT
       ,upd_detl TEXT
       ,FOREIGN KEY (idseq) REFERENCES Entry(idseq)
);

-------------------------------------------------------------------------------------
-- Kanji reading(s) of an entry
-------------------------------------------------------------------------------------
CREATE TABLE Kanji (
       id INTEGER PRIMARY KEY
       ,idseq INTEGER
       ,text TEXT
       ,FOREIGN KEY (idseq) REFERENCES Entry(idseq)
);

-- Kanji's info
CREATE TABLE KJI (
       kid INTEGER
       ,text TEXT
       ,FOREIGN KEY (kid) REFERENCES Kanji(id)
);

-- Kanji priority
CREATE TABLE KJP (
       kid INTEGER
       ,text TEXT
       ,FOREIGN KEY (kid) REFERENCES Kanji(id)
);

-------------------------------------------------------------------------------------
-- Kana reading(s) of an entry
-------------------------------------------------------------------------------------
CREATE TABLE Kana (
       id INTEGER PRIMARY KEY
       ,idseq INTEGER
       ,text TEXT
       ,nokanji BOOLEAN
       ,FOREIGN KEY (idseq) REFERENCES Entry(idseq)
);

-- re_restr
CREATE TABLE KNR (
       kid INTEGER
       ,text TEXT
       ,FOREIGN KEY (kid) REFERENCES Kana(id)
);

-- Kana's info
CREATE TABLE KNI (
       kid INTEGER
       ,text TEXT
       ,FOREIGN KEY (kid) REFERENCES Kana(id)
);

-- Kana priority
CREATE TABLE KNP (
       kid INTEGER
       ,text TEXT
       ,FOREIGN KEY (kid) REFERENCES Kana(id)
);

-------------------------------------------------------------------------------------
-- Senses of an entry
-------------------------------------------------------------------------------------
CREATE TABLE Sense (
       id INTEGER PRIMARY KEY
       ,idseq INTEGER
       ,FOREIGN KEY (idseq) REFERENCES Entry(idseq)
);

CREATE TABLE stagk (
       sid INTEGER
       ,text TEXT
       ,FOREIGN KEY (sid) REFERENCES Sense(id)
);

CREATE TABLE stagr (
       sid INTEGER
       ,text TEXT
       ,FOREIGN KEY (sid) REFERENCES Sense(id)
);

CREATE TABLE pos (
       sid INTEGER
       ,text TEXT
       ,FOREIGN KEY (sid) REFERENCES Sense(id)
);

CREATE TABLE xref (
       sid INTEGER
       ,text TEXT
       ,FOREIGN KEY (sid) REFERENCES Sense(id)
);

CREATE TABLE antonym (
       sid INTEGER
       ,text TEXT
       ,FOREIGN KEY (sid) REFERENCES Sense(id)
);

CREATE TABLE field (
       sid INTEGER
       ,text TEXT
       ,FOREIGN KEY (sid) REFERENCES Sense(id)
);

CREATE TABLE misc (
       sid INTEGER
       ,text TEXT
       ,FOREIGN KEY (sid) REFERENCES Sense(id)
);

CREATE TABLE SenseInfo (
       sid INTEGER
       ,text TEXT
       ,FOREIGN KEY (sid) REFERENCES Sense(id)
);

CREATE TABLE SenseSource (
       sid INTEGER
       ,text TEXT
       ,lang TEXT
       ,lstype TEXT
       ,wasei TEXT
       ,FOREIGN KEY (sid) REFERENCES Sense(id)
);

CREATE TABLE dialect (
       sid INTEGER
       ,text TEXT
       ,FOREIGN KEY (sid) REFERENCES Sense(id)
);

CREATE TABLE SenseGloss (
       sid INTEGER
       ,lang TEXT
       ,gend TEXT
       ,text TEXT
       ,FOREIGN KEY (sid) REFERENCES Sense(id)
);
