# -*- coding: utf-8 -*-

# Python library for manipulating Jim Breen's KanjiDic2
# Latest version can be found at https://github.com/neocl/jamdict
# 
# This package uses the [EDICT][1] and [KANJIDIC][2] dictionary files.
# These files are the property of the [Electronic Dictionary Research and Development Group][3], and are used in conformance with the Group's [licence][4].
# 
# [1]: http://www.csse.monash.edu.au/~jwb/edict.html
# [2]: http://www.edrdg.org/kanjidic/kanjd2index.html
# [3]: http://www.edrdg.org/
# [4]: http://www.edrdg.org/edrdg/licence.html
# 
# References:
#     JMDict website:
#         http://www.csse.monash.edu.au/~jwb/edict.html
#         http://www.edrdg.org/kanjidic/kanjd2index.html
# 
# @author: Le Tuan Anh <tuananh.ke@gmail.com>
# @license: MIT

########################################################################

import os
import logging
try:
    from lxml import etree
    _LXML_AVAILABLE = True
except Exception as e:
    # logging.getLogger(__name__).debug("lxml is not available, fall back to xml.etree.ElementTree")
    from xml.etree import ElementTree as etree
    _LXML_AVAILABLE = False

from chirptext import chio
from chirptext.sino import Radical as KangxiRadical

from .krad import KRad

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

krad = KRad()


def getLogger():
    return logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Models
# ------------------------------------------------------------------------------

class KanjiDic2(object):

    def __init__(self, file_version, database_version, date_of_creation):
        """
<!ELEMENT header (file_version,database_version,date_of_creation)>
<!--
    The single header element will contain identification information
    about the version of the file
    -->
<!ELEMENT file_version (#PCDATA)>
<!--
    This field denotes the version of kanjidic2 structure, as more
    than one version may exist.
    -->
<!ELEMENT database_version (#PCDATA)>
<!--
    The version of the file, in the format YYYY-NN, where NN will be
    a number starting with 01 for the first version released in a
    calendar year, then increasing for each version in that year.
    -->
<!ELEMENT date_of_creation (#PCDATA)>
<!--
    The date the file was created in international format (YYYY-MM-DD).
-->"""
        self.file_version = file_version
        self.database_version = database_version
        self.date_of_creation = date_of_creation
        self.characters = []

    def __len__(self):
        return len(self.characters)

    def __getitem__(self, idx):
        return self.characters[idx]


class Character(object):
    """ Represent a kanji character.
    
    <!ELEMENT character (literal,codepoint, radical, misc, dic_number?, query_code?, reading_meaning?)*>"""

    def __init__(self):
        """

        """
        self.ID = None
        self.literal = ''  # <!ELEMENT literal (#PCDATA)> The character itself in UTF8 coding.
        self.codepoints = []  # <!ELEMENT codepoint (cp_value+)>
        self.radicals = []  # <!ELEMENT radical (rad_value+)>
        self.__canon_radical = None
        self.stroke_count = None  # first stroke_count in misc
        self.grade = None  # <misc>/<grade>
        self.stroke_miscounts = []  # <misc>/stroke_count[1:]
        self.variants = []  # <misc>/<variant>
        self.freq = None  # <misc>/<freq>
        self.rad_names = []  # <misc>/<rad_name> a list of strings
        self.jlpt = None  # <misc>/<jlpt>
        self.dic_refs = []  # DicRef[]
        self.query_codes = []  # QueryCode[]
        self.rm_groups = []  # reading_meaning groups
        self.nanoris = []  # a list of strings

    def __repr__(self):
        meanings = self.meanings(english_only=True)
        return "{l}:{sc}:{meanings}".format(l=self.literal, sc=self.stroke_count, meanings=','.join(meanings))

    def __str__(self):
        return self.literal

    def meanings(self, english_only=False):
        ''' Accumulate all meanings as a list of string. Each string is a meaning (i.e. sense) '''
        meanings = []
        for rm in self.rm_groups:
            for m in rm.meanings:
                if english_only and m.m_lang != '':
                    continue
                meanings.append(m.value)
        return meanings

    @property
    def components(self):
        ''' Kanji writing components that compose this character '''
        if self.literal in krad.krad:
            return krad.krad[self.literal]
        else:
            return []

    @property
    def radical(self):
        if self.__canon_radical is None:
            for rad in self.radicals:
                if rad.rad_type == 'classical':
                    self.__canon_radical = KangxiRadical.kangxi()[rad.value]
        return self.__canon_radical

    def to_json(self):
        return {'literal': self.literal,
                'codepoints': [cp.to_json() for cp in self.codepoints],
                'radicals': [r.to_json() for r in self.radicals],
                'stroke_count': self.stroke_count,
                'grade': self.grade if self.grade else '',
                'stroke_miscounts': self.stroke_miscounts,
                'variants': [v.to_json() for v in self.variants],
                'freq': self.freq if self.freq else 0,
                'rad_names': self.rad_names,
                'jlpt': self.jlpt if self.jlpt else '',
                'dic_refs': [r.to_json() for r in self.dic_refs],
                'q_codes': [q.to_json() for q in self.query_codes],
                'rm': [rm.to_json() for rm in self.rm_groups],
                'nanoris': list(self.nanoris)}


class CodePoint(object):

    def __init__(self, cp_type='', value=''):
        """<!ELEMENT cp_value (#PCDATA)>
    <!--
    The cp_value contains the codepoint of the character in a particular
    standard. The standard will be identified in the cp_type attribute.
    -->
        """
        self.cid = None
        self.cp_type = cp_type
        self.value = value

    def __repr__(self):
        if self.r_type:
            return "({t}) {v}".format(t=self.cp_type, v=self.value)
        else:
            return self.value

    def __str__(self):
        return self.value

    def to_json(self):
        return {'type': self.cp_type, 'value': self.value}


class Radical(object):

    def __init__(self, rad_type='', value=''):
        """<!ELEMENT radical (rad_value+)>
        <!ELEMENT rad_value (#PCDATA)>
        <!--
        The radical number, in the range 1 to 214. The particular
        classification type is stated in the rad_type attribute.
        -->"""
        self.cid = None
        self.rad_type = rad_type
        self.value = value

    def __repr__(self):
        if self.rad_type:
            return "({t}) {v}".format(t=self.rad_type, v=self.value)
        else:
            return self.value

    def __str__(self):
        return self.value

    def to_json(self):
        return {'type': self.rad_type, 'value': self.value}


class Variant(object):

    def __init__(self, var_type='', value=''):
        """<!ELEMENT variant (#PCDATA)>
        <!--
        Either a cross-reference code to another kanji, usually regarded as a
        variant, or an alternative indexing code for the current kanji.
        The type of variant is given in the var_type attribute.
        -->
        <!ATTLIST variant var_type CDATA #REQUIRED>
        <!--
        The var_type attribute indicates the type of variant code. The current
        values are:
        jis208 - in JIS X 0208 - kuten coding
        jis212 - in JIS X 0212 - kuten coding
        jis213 - in JIS X 0213 - kuten coding
          (most of the above relate to "shinjitai/kyuujitai"
          alternative character glyphs)
        deroo - De Roo number - numeric
        njecd - Halpern NJECD index number - numeric
        s_h - The Kanji Dictionary (Spahn & Hadamitzky) - descriptor
        nelson_c - "Classic" Nelson - numeric
        oneill - Japanese Names (O'Neill) - numeric
        ucs - Unicode codepoint- hex
        --> """
        self.cid = None
        self.var_type = var_type
        self.value = value

    def __repr__(self):
        if self.var_type:
            return "({t}) {v}".format(t=self.var_type, v=self.value)
        else:
            return self.value

    def __str__(self):
        return self.value

    def to_json(self):
        return {'type': self.var_type, 'value': self.value}


class DicRef(object):

    def __init__(self, dr_type='', value='', m_vol='', m_page=''):
        """<!ELEMENT dic_ref (#PCDATA)>
    <!--
    Each dic_ref contains an index number. The particular dictionary,
    etc. is defined by the dr_type attribute.
    -->
<!ATTLIST dic_ref dr_type CDATA #REQUIRED>
    <!--
    The dr_type defines the dictionary or reference book, etc. to which
    dic_ref element applies. The initial allocation is:
      nelson_c - "Modern Reader's Japanese-English Character Dictionary",
        edited by Andrew Nelson (now published as the "Classic"
        Nelson).
      nelson_n - "The New Nelson Japanese-English Character Dictionary",
        edited by John Haig.
      halpern_njecd - "New Japanese-English Character Dictionary",
        edited by Jack Halpern.
      halpern_kkld - "Kanji Learners Dictionary" (Kodansha) edited by
        Jack Halpern.
      heisig - "Remembering The  Kanji"  by  James Heisig.
      gakken - "A  New Dictionary of Kanji Usage" (Gakken)
      oneill_names - "Japanese Names", by P.G. O'Neill.
      oneill_kk - "Essential Kanji" by P.G. O'Neill.
      moro - "Daikanwajiten" compiled by Morohashi. For some kanji two
        additional attributes are used: m_vol:  the volume of the
        dictionary in which the kanji is found, and m_page: the page
        number in the volume.
      henshall - "A Guide To Remembering Japanese Characters" by
        Kenneth G.  Henshall.
      sh_kk - "Kanji and Kana" by Spahn and Hadamitzky.
      sakade - "A Guide To Reading and Writing Japanese" edited by
        Florence Sakade.
      jf_cards - Japanese Kanji Flashcards, by Max Hodges and
        Tomoko Okazaki. (Series 1)
      henshall3 - "A Guide To Reading and Writing Japanese" 3rd
        edition, edited by Henshall, Seeley and De Groot.
      tutt_cards - Tuttle Kanji Cards, compiled by Alexander Kask.
      crowley - "The Kanji Way to Japanese Language Power" by
        Dale Crowley.
      kanji_in_context - "Kanji in Context" by Nishiguchi and Kono.
      busy_people - "Japanese For Busy People" vols I-III, published
        by the AJLT. The codes are the volume.chapter.
      kodansha_compact - the "Kodansha Compact Kanji Guide".
      maniette - codes from Yves Maniette's "Les Kanjis dans la tete" French adaptation of Heisig.
    -->"""
        self.cid = None
        self.dr_type = dr_type
        self.value = value
        self.m_vol = m_vol
        self.m_page = m_page

    def __repr__(self):
        if self.dr_type:
            return "({t}) {v}".format(t=self.dr_type, v=self.value)
        else:
            return self.value

    def __str__(self):
        return self.value

    def to_json(self):
        return {'type': self.dr_type,
                'value': self.value,
                "m_vol": self.m_vol,
                "m_page": self.m_page}


class QueryCode(object):

    def __init__(self, qc_type='', value='', skip_misclass=""):
        """<!ELEMENT query_code (q_code+)>
    <!--
    These codes contain information relating to the glyph, and can be used
    for finding a required kanji. The type of code is defined by the
    qc_type attribute.
    -->
<!ELEMENT q_code (#PCDATA)>
    <!--
    The q_code contains the actual query-code value, according to the
    qc_type attribute.
    -->
<!ATTLIST q_code qc_type CDATA #REQUIRED>
    <!--
    The qc_type attribute defines the type of query code. The current values
    are:
      skip -  Halpern's SKIP (System  of  Kanji  Indexing  by  Patterns)
        code. The  format is n-nn-nn.  See the KANJIDIC  documentation
        for  a description of the code and restrictions on  the
        commercial  use  of this data. [P]  There are also
        a number of misclassification codes, indicated by the
        "skip_misclass" attribute.
      sh_desc - the descriptor codes for The Kanji Dictionary (Tuttle
        1996) by Spahn and Hadamitzky. They are in the form nxnn.n,
        e.g.  3k11.2, where the  kanji has 3 strokes in the
        identifying radical, it is radical "k" in the SH
        classification system, there are 11 other strokes, and it is
        the 2nd kanji in the 3k11 sequence. (I am very grateful to
        Mark Spahn for providing the list of these descriptor codes
        for the kanji in this file.) [I]
      four_corner - the "Four Corner" code for the kanji. This is a code
        invented by Wang Chen in 1928. See the KANJIDIC documentation
        for  an overview of  the Four Corner System. [Q]

      deroo - the codes developed by the late Father Joseph De Roo, and
        published in  his book "2001 Kanji" (Bonjinsha). Fr De Roo
        gave his permission for these codes to be included. [DR]
      misclass - a possible misclassification of the kanji according
        to one of the code types. (See the "Z" codes in the KANJIDIC
        documentation for more details.)
    -->
<!ATTLIST q_code skip_misclass CDATA #IMPLIED>
    <!--
    The values of this attribute indicate the type if
    misclassification:
    - posn - a mistake in the division of the kanji
    - stroke_count - a mistake in the number of strokes
    - stroke_and_posn - mistakes in both division and strokes
    - stroke_diff - ambiguous stroke counts depending on glyph
S    --> """
        self.cid = None
        self.qc_type = qc_type
        self.value = value
        self.skip_misclass = skip_misclass

    def __repr__(self):
        if self.qc_type:
            return "({t}) {v}".format(t=self.qc_type, v=self.value)
        else:
            return self.value

    def __str__(self):
        return self.value

    def to_json(self):
        return {'type': self.qc_type, 'value': self.value, "skip_misclass": self.skip_misclass}


class RMGroup(object):

    def __init__(self, readings=None, meanings=None):
        """<!ELEMENT reading_meaning (rmgroup*, nanori*)>
        <!--
        The readings for the kanji in several languages, and the meanings, also
        in several languages. The readings and meanings are grouped to enable
        the handling of the situation where the meaning is differentiated by
        reading. [T1]
        -->
        <!ELEMENT rmgroup (reading*, meaning*)>
        """
        self.ID = None
        self.cid = None
        self.readings = readings if readings else []
        self.meanings = meanings if meanings else []

    def __repr__(self):
        return "R: {} | M: {}".format(
            ", ".join([r.value for r in self.readings]),
            ", ".join(m.value for m in self.meanings))

    def __str__(self):
        return repr(self)

    def to_json(self):
        return {'readings': [r.to_json() for r in self.readings],
                'meanings': [m.to_json() for m in self.meanings]}


class Reading(object):

    def __init__(self, r_type='', value='', on_type="", r_status=""):
        """<!ELEMENT reading (#PCDATA)>
        <!--
        The reading element contains the reading or pronunciation
        of the kanji.
        -->
        <!ATTLIST reading r_type CDATA #REQUIRED>
        <!--
        The r_type attribute defines the type of reading in the reading
        element. The current values are:
        pinyin - the modern PinYin romanization of the Chinese reading
        of the kanji. The tones are represented by a concluding
        digit. [Y]
        korean_r - the romanized form of the Korean reading(s) of the
        kanji.  The readings are in the (Republic of Korea) Ministry
        of Education style of romanization. [W]
        korean_h - the Korean reading(s) of the kanji in hangul.
        ja_on - the "on" Japanese reading of the kanji, in katakana.
        Another attribute r_status, if present, will indicate with
        a value of "jy" whether the reading is approved for a
        "Jouyou kanji".
        A further attribute on_type, if present,  will indicate with
        a value of kan, go, tou or kan'you the type of on-reading.
        ja_kun - the "kun" Japanese reading of the kanji, usually in
        hiragana.
        Where relevant the okurigana is also included separated by a
        ".". Readings associated with prefixes and suffixes are
        marked with a "-". A second attribute r_status, if present,
        will indicate with a value of "jy" whether the reading is
        approved for a "Jouyou kanji".
        -->
        <!ATTLIST reading on_type CDATA #IMPLIED>
        <!--
        See under ja_on above.
        -->
        <!ATTLIST reading r_status CDATA #IMPLIED>
        <!--
        See under ja_on and ja_kun above.
        -->"""
        self.gid = None
        self.r_type = r_type
        self.value = value
        self.on_type = on_type
        self.r_status = r_status

    def __repr__(self):
        if self.r_type:
            return "({t}) {v}".format(t=self.r_type, v=self.value)
        else:
            return self.value

    def __str__(self):
        return self.value

    def to_json(self):
        return {'type': self.r_type,
                'value': self.value,
                'on_type': self.on_type,
                'r_status': self.r_status}


class Meaning(object):

    def __init__(self, value='', m_lang=''):
        """<!ELEMENT meaning (#PCDATA)>
        <!--
        The meaning associated with the kanji.
        -->
        <!ATTLIST meaning m_lang CDATA #IMPLIED>
        <!--
        The m_lang attribute defines the target language of the meaning. It
        will be coded using the two-letter language code from the ISO 639-1
        standard. When absent, the value "en" (i.e. English) is implied. [{}]
        -->"""
        self.gid = None
        self.m_lang = m_lang
        self.value = value

    def __repr__(self):
        if self.m_lang:
            return "({l}) {v}".format(l=self.m_lang, v=self.value)
        else:
            return self.value

    def __str__(self):
        return self.value

    def to_json(self):
        return {'m_lang': self.m_lang, 'value': self.value}


class Kanjidic2XMLParser(object):
    '''JMDict XML parser
    '''

    def __init__(self):
        pass

    def get_attrib(self, a_tag, attr_name, default_value=''):
        if attr_name == 'xml:lang':
            attr_name = '''{http://www.w3.org/XML/1998/namespace}lang'''
        if attr_name in a_tag.attrib:
            return a_tag.attrib[attr_name]
        else:
            return default_value

    def parse_file(self, kd2_file_path):
        ''' Parse all characters from Kanjidic2 XML file
        '''
        actual_path = os.path.abspath(os.path.expanduser(kd2_file_path))
        getLogger().debug('Loading data from file: {}'.format(actual_path))

        with chio.open(actual_path, mode='rb') as kd2file:
            tree = etree.iterparse(kd2file)
            kd2 = None
            for event, element in tree:
                if event == 'end':
                    if element.tag == 'header':
                        kd2 = self.parse_header(element)
                        element.clear()
                    elif element.tag == 'character':
                        kd2.characters.append(self.parse_char(element))
                        element.clear()
            return kd2

    def parse_header(self, e):
        fv = None
        dbv = None
        doc = None
        for child in e:
            if child.tag == 'file_version':
                fv = child.text
            elif child.tag == 'database_version':
                dbv = child.text
            elif child.tag == 'date_of_creation':
                doc = child.text
        return KanjiDic2(fv, dbv, doc)

    def parse_char(self, e):
        char = Character()
        for child in e:
            if child.tag == 'literal':
                char.literal = child.text
            elif child.tag == 'codepoint':
                self.parse_codepoint(child, char)
            elif child.tag == 'radical':
                self.parse_radical(child, char)
            elif child.tag == 'misc':
                self.parse_misc(child, char)
            elif child.tag == 'dic_number':
                self.parse_dic_refs(child, char)
            elif child.tag == 'query_code':
                self.parse_query_code(child, char)
            elif child.tag == 'reading_meaning':
                self.parse_reading_meaning(child, char)
            else:
                getLogger().warning("Unknown tag in child: {}".format(child.tag))
        return char

    def parse_codepoint(self, e, char):
        for child in e:
            if child.tag == 'cp_value':
                cp = CodePoint(self.get_attrib(child, 'cp_type'), child.text)
                char.codepoints.append(cp)
            else:
                getLogger().warning("Unknown tag: {}".format(child.tag))

    def parse_radical(self, e, char):
        for child in e:
            if child.tag == 'rad_value':
                rad = Radical(self.get_attrib(child, "rad_type"), child.text)
                char.radicals.append(rad)
            else:
                getLogger().warning("Unknown tag: {}".format(child.tag))

    def parse_misc(self, e, char):
        for child in e:
            # grade?, stroke_count+, variant*, freq?, rad_name*,jlpt?
            if child.tag == 'grade':
                char.grade = child.text
            elif child.tag == 'stroke_count':
                if char.stroke_count is None:
                    char.stroke_count = int(child.text)
                else:
                    char.stroke_miscounts.append(int(child.text))
            elif child.tag == 'variant':
                v = Variant(self.get_attrib(child, "var_type"), child.text)
                char.variants.append(v)
            elif child.tag == 'freq':
                char.freq = child.text
            elif child.tag == 'rad_name':
                char.rad_names.append(child.text)
            elif child.tag == 'jlpt':
                char.jlpt = child.text
            else:
                getLogger().warning("Unknown tag: {}".format(child.tag))

    def parse_dic_refs(self, e, char):
        for child in e:
            if child.tag == 'dic_ref':
                dr_type = self.get_attrib(child, "dr_type")
                m_vol = self.get_attrib(child, "m_vol")
                m_page = self.get_attrib(child, "m_page")
                dr = DicRef(dr_type, child.text, m_vol, m_page)
                char.dic_refs.append(dr)
            else:
                getLogger().warning("Unknown tag: {}".format(child.tag))

    def parse_query_code(self, e, char):
        for child in e:
            if child.tag == "q_code":
                qc_type = self.get_attrib(child, "qc_type")
                skip_misclass = self.get_attrib(child, "skip_misclass")
                char.query_codes.append(QueryCode(qc_type, child.text, skip_misclass))
            else:
                getLogger().warning("Unknown tag: {}".format(child.tag))

    def parse_reading_meaning(self, e, char):
        for child in e:
            if child.tag == "nanori":
                char.nanoris.append(child.text)
            elif child.tag == "rmgroup":
                rmgroup = RMGroup()
                char.rm_groups.append(rmgroup)
                for grandchild in child:
                    if grandchild.tag == 'reading':
                        r_type = self.get_attrib(grandchild, "r_type")
                        on_type = self.get_attrib(grandchild, "on_type")
                        r_status = self.get_attrib(grandchild, "r_status")
                        r = Reading(r_type, grandchild.text, on_type, r_status)
                        rmgroup.readings.append(r)
                    elif grandchild.tag == 'meaning':
                        m = Meaning(grandchild.text, self.get_attrib(grandchild, "m_lang"))
                        rmgroup.meanings.append(m)
                    else:
                        getLogger().warning("Unknown tag: {}".format(grandchild.tag))
            else:
                getLogger().warning("Unknown tag: {}".format(child.tag))
