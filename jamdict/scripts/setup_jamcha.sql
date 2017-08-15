/* Add meta info */
CREATE TABLE meta (
       file_version TEXT,  -- from source XML
       database_version TEXT,  -- from source XML
       date_of_creation TEXT,  -- from source XML
       generator TEXT,
       generator_version TEXT,
       generator_url TEXT
);

CREATE TABLE character (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       stroke_count INTEGER,
       grade TEXT,
       freq TEXT,
       jlpt TEXT
);

CREATE TABLE codepoint (
       cid INTEGER
       ,cp_type TEXT
       ,value TEXT
       ,FOREIGN KEY (cid) REFERENCES character(id)
);

CREATE TABLE radical (
       cid INTEGER
       ,rad_type TEXT
       ,value TEXT
       ,FOREIGN KEY (cid) REFERENCES character(id)
);

CREATE TABLE stroke_miscount (
       cid INTEGER
       ,value INTEGER
       ,FOREIGN KEY (cid) REFERENCES character(id)
);

CREATE TABLE variants (
       cid INTEGER
       ,var_type TEXT
       ,value TEXT
       ,FOREIGN KEY (cid) REFERENCES character(id)
);

CREATE TABLE rad_names (
       cid INTEGER
       ,value TEXT
       ,FOREIGN KEY (cid) REFERENCES character(id)
);

CREATE TABLE dic_refs (
       cid INTEGER
       ,dr_type TEXT
       ,value TEXT
       ,m_vol TEXT
       ,m_page TEXT
       ,FOREIGN KEY (cid) REFERENCES character(id)
);

CREATE TABLE query_codes (
       cid INTEGER
       ,qc_type TEXT
       ,value TEXT
       ,skip_misclass TEXT
       ,FOREIGN KEY (cid) REFERENCES character(id)
);

CREATE TABLE nanoris (
       cid INTEGER
       ,value TEXT
       ,FOREIGN KEY (cid) REFERENCES character(id)
);

CREATE TABLE rm_group (
       id INTEGER PRIMARY KEY AUTOINCREMENT
       ,cid INTEGER
       ,FOREIGN KEY (cid) REFERENCES character(id)
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

