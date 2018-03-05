/* Add meta info */
CREATE TABLE IF NOT EXISTS meta (
       key TEXT UNIQUE,
       value TEXT NOT NULL
);

-------------------------------------------------------------------------------------
-- KanjiDic2 tables
-------------------------------------------------------------------------------------

CREATE TABLE character (
       ID INTEGER PRIMARY KEY AUTOINCREMENT,
       literal TEXT NOT NULL,
       stroke_count INTEGER,
       grade TEXT,
       freq TEXT,
       jlpt TEXT
);

CREATE TABLE codepoint (
       cid INTEGER
       ,cp_type TEXT
       ,value TEXT
       ,FOREIGN KEY (cid) REFERENCES character(ID)
);

CREATE TABLE radical (
       cid INTEGER
       ,rad_type TEXT
       ,value TEXT
       ,FOREIGN KEY (cid) REFERENCES character(ID)
);

CREATE TABLE stroke_miscount (
       cid INTEGER
       ,value INTEGER
       ,FOREIGN KEY (cid) REFERENCES character(ID)
);

CREATE TABLE variant (
       cid INTEGER
       ,var_type TEXT
       ,value TEXT
       ,FOREIGN KEY (cid) REFERENCES character(ID)
);

CREATE TABLE rad_name (
       cid INTEGER
       ,value TEXT
       ,FOREIGN KEY (cid) REFERENCES character(ID)
);

CREATE TABLE dic_ref (
       cid INTEGER
       ,dr_type TEXT
       ,value TEXT
n       ,m_vol TEXT
       ,m_page TEXT
       ,FOREIGN KEY (cid) REFERENCES character(ID)
);

CREATE TABLE query_code (
       cid INTEGER
       ,qc_type TEXT
       ,value TEXT
       ,skip_misclass TEXT
       ,FOREIGN KEY (cid) REFERENCES character(ID)
);

CREATE TABLE nanori (
       cid INTEGER
       ,value TEXT
       ,FOREIGN KEY (cid) REFERENCES character(ID)
);

CREATE TABLE rm_group (
       ID INTEGER PRIMARY KEY AUTOINCREMENT
       ,cid INTEGER
       ,FOREIGN KEY (cid) REFERENCES character(ID)
);

CREATE TABLE reading (
       gid INTEGER
       ,r_type TEXT
       ,value TEXT
       ,on_type TEXT
       ,r_status TEXT
       ,FOREIGN KEY (gid) REFERENCES rm_group(id)
);

CREATE TABLE meaning (
       gid INTEGER
       ,value TEXT
       ,m_lang TEXT
       ,FOREIGN KEY (gid) REFERENCES rm_group(id)
);

-------------------------------------------------------------------------------------
-- INDICES - KanjiDic2
-------------------------------------------------------------------------------------

CREATE INDEX character_literal ON character(literal);
CREATE INDEX character_stroke_count ON character(stroke_count);
CREATE INDEX character_grade ON character(grade);
CREATE INDEX character_jlpt ON character(jlpt);

CREATE INDEX codepoint_value ON codepoint(value);
CREATE INDEX radical_value ON radical(value);
CREATE INDEX variant_value ON variant(value);
CREATE INDEX rad_name_value ON rad_name(value);
CREATE INDEX dic_ref_value ON dic_ref(value);
CREATE INDEX query_code_value ON query_code(value);
CREATE INDEX nanori_value ON nanori(value);
CREATE INDEX rm_group_cid ON rm_group(cid);
CREATE INDEX reading_r_type ON reading(r_type);
CREATE INDEX reading_value ON reading(value);
CREATE INDEX meaning_value ON meaning(value);
CREATE INDEX meaning_m_lang ON meaning(m_lang);
