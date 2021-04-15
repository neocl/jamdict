# -*- coding: utf-8 -*-

# Python library for manipulating Jim Breen's JMdict
# Latest version can be found at https://github.com/neocl/jamdict
# 
# This package uses the [EDICT][1] and [KANJIDIC][2] dictionary files.
# These files are the property of the [Electronic Dictionary Research and Development Group][3], and are used in conformance with the Group's [licence][4].
# 
# [1]: http://www.csse.monash.edu.au/~jwb/edict.html
# [2]: http://www.csse.monash.edu.au/~jwb/kanjidic.html
# [3]: http://www.edrdg.org/
# [4]: http://www.edrdg.org/edrdg/licence.html
# 
# References:
#     JMDict website:
#         http://www.csse.monash.edu.au/~jwb/edict.html
#     Python documentation:
#         https://docs.python.org/
#     PEP 257 - Python Docstring Conventions:
#         https://www.python.org/dev/peps/pep-0257/
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

logger = logging.getLogger(__name__)

########################################################################


class JMDEntry(object):
    ''' Represents a dictionary Word entry.

    Entries consist of kanji elements, reading elements,
    general information and sense elements. Each entry must have at
    least one reading element and one sense element. Others are optional.

    XML DTD <!ELEMENT entry (ent_seq, k_ele*, r_ele+, info?, sense+)>'''

    def __init__(self, idseq=''):
        # A unique numeric sequence number for each entry
        self.idseq = idseq     # ent_seq
        self.kanji_forms = []  # k_ele*  => KanjiForm[]
        self.kana_forms = []   # r_ele+  => KanaForm[]
        self.info = None       # info?   => EntryInfo
        self.senses = []       # sense+

    def __len__(self):
        return len(self.senses)

    def __getitem__(self, idx):
        return self.senses[idx]

    def set_info(self, info):
        if self.info:
            logging.warning("WARNING: multiple info tag")
        self.info = info

    def text(self, compact=True, separator=' ', no_id=False):
        tmp = []
        if not compact and not no_id:
            tmp.append('[id#%s]' % self.idseq)
        if self.kana_forms:
            tmp.append(self.kana_forms[0].text)
        if self.kanji_forms:
            tmp.append("({})".format(self.kanji_forms[0].text))
        if self.senses:
            tmp.append(':')
            if len(self.senses) == 1:
                tmp.append(self.senses[0].text(compact=compact))
            else:
                for sense, idx in zip(self.senses, range(len(self.senses))):
                    tmp.append('{i}. {s}'.format(i=idx + 1, s=sense.text(compact=compact)))
        return separator.join(tmp)

    def __repr__(self):
        return self.text(compact=True)

    def __str__(self):
        return self.text(compact=False)

    def to_json(self):
        ed = {'idseq': self.idseq,
              'kanji': [x.to_json() for x in self.kanji_forms],
              'kana': [x.to_json() for x in self.kana_forms],
              'senses': [x.to_json() for x in self.senses]}
        if self.info:
            ed['info'] = self.info.to_json()
        return ed


class KanjiForm(object):
    ''' The kanji element, or in its absence, the reading element, is
    the defining component of each entry.
    The overwhelming majority of entries will have a single kanji
    element associated with a word in Japanese. Where there are
    multiple kanji elements within an entry, they will be orthographical
    variants of the same word, either using variations in okurigana, or
    alternative and equivalent kanji. Common "mis-spellings" may be
    included, provided they are associated with appropriate information
    fields. Synonyms are not included; they may be indicated in the
    cross-reference field associated with the sense element.
    DTD <!ELEMENT k_ele (keb, ke_inf*, ke_pri*)>
    text --- a kanji written form of an entry, string
    info --- coded information field, a list of strings
    pri --- relative priority of the entry, a list of strings
    '''

    def __init__(self, text=''):
        '''This element will contain a word or short phrase in Japanese
        which is written using at least one non-kana character (usually kanji,
        but can be other characters). The valid characters are
        kanji, kana, related characters such as chouon and kurikaeshi, and
        in exceptional cases, letters from other alphabets.
        '''
        self.text = text  # <!ELEMENT keb (#PCDATA)>

        '''This is a coded information field related specifically to the
        orthography of the keb, and will typically indicate some unusual
        aspect, such as okurigana irregularity.'''
        self.info = []  # <!ELEMENT ke_inf (#PCDATA)>*

        '''This and the equivalent re_pri field are provided to record
        information about the relative priority of the entry,  and consist
        of codes indicating the word appears in various references which
        can be taken as an indication of the frequency with which the word
        is used. This field is intended for use either by applications which
        want to concentrate on entries of  a particular priority, or to
        generate subset files.
        The current values in this field are:
        - news1/2: appears in the "wordfreq" file compiled by Alexandre Girardi
        from the Mainichi Shimbun. (See the Monash ftp archive for a copy.)
        Words in the first 12,000 in that file are marked "news1" and words
        in the second 12,000 are marked "news2".
        - ichi1/2: appears in the "Ichimango goi bunruishuu", Senmon Kyouiku
        Publishing, Tokyo, 1998.  (The entries marked "ichi2" were
        demoted from ichi1 because they were observed to have low
        frequencies in the WWW and newspapers.)
        - spec1 and spec2: a small number of words use this marker when they
        are detected as being common, but are not included in other lists.
        - gai1/2: common loanwords, based on the wordfreq file.
        - nfxx: this is an indicator of frequency-of-use ranking in the
        wordfreq file. "xx" is the number of the set of 500 words in which
        the entry can be found, with "01" assigned to the first 500, "02"
        to the second, and so on. (The entries with news1, ichi1, spec1 and
        gai1 values are marked with a "(P)" in the EDICT and EDICT2
        files.)
        The reason both the kanji and reading elements are tagged is because
        on occasions a priority is only associated with a particular
        kanji/reading pair.'''
        self.pri = []  # <!ELEMENT ke_pri (#PCDATA)>*

    def set_text(self, text):
        if self.text:
            logging.warning("WARNING: duplicated text for k_ele")
        self.text = text

    def to_json(self):
        kjd = {'text': self.text}
        if self.info:
            kjd['info'] = self.info
        if self.pri:
            kjd['pri'] = self.pri
        return kjd

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.text


class KanaForm(object):
    '''<!ELEMENT r_ele (reb, re_nokanji?, re_restr*, re_inf*, re_pri*)>
    The reading element typically contains the valid readings
    of the word(s) in the kanji element using modern kanadzukai.
    Where there are multiple reading elements, they will typically be
    alternative readings of the kanji element. In the absence of a
    kanji element, i.e. in the case of a word or phrase written
    entirely in kana, these elements will define the entry.
    text --- a kana written form of an entry, string
    nokanji --- True means this entry cannot be regarded as a true reading of the kanji, boolean
    restr --- use to restrict the reading to a subset of the available kanji forms, list of string
    info --- coded information field, a list of strings
    pri --- relative priority of the entry, a list of strings
    '''

    def __init__(self, text='', nokanji=False):
        '''this element content is restricted to kana and related
        characters such as chouon and kurikaeshi. Kana usage will be
        consistent between the keb and reb elements; e.g. if the keb
        contains katakana, so too will the reb.'''
        self.text = text  # <!ELEMENT reb (#PCDATA)>

        '''This element, which will usually have a null value, indicates
        that the reb, while associated with the keb, cannot be regarded
        as a true reading of the kanji. It is typically used for words
        such as foreign place names, gairaigo which can be in kanji or
        katakana, etc.'''
        self.nokanji = nokanji  # <!ELEMENT re_nokanji (#PCDATA)>?

        '''This element is used to indicate when the reading only applies
        to a subset of the keb elements in the entry. In its absence, all
        readings apply to all kanji elements. The contents of this element
        must exactly match those of one of the keb elements.'''
        self.restr = []  # <!ELEMENT re_restr (#PCDATA)>*

        '''General coded information pertaining to the specific reading.
        Typically it will be used to indicate some unusual aspect of
        the reading.'''
        self.info = []  # <!ELEMENT re_inf (#PCDATA)>*

        '''See the comment on ke_pri above.'''
        self.pri = []  # <!ELEMENT re_pri (#PCDATA)>*

    def set_text(self, text):
        if self.text:
            logging.warning("WARNING: duplicated text for k_ele")
        self.text = text

    def to_json(self):
        knd = {'text': self.text,
               'nokanji': self.nokanji}
        if self.restr:
            knd['restr'] = self.restr
        if self.info:
            knd['info'] = self.info
        if self.pri:
            knd['pri'] = self.pri
        return knd

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.text


class EntryInfo(object):
    '''General coded information relating to the entry as a whole.
    DTD: <!ELEMENT info (links*, bibl*, etym*, audit*)>
    '''
    def __init__(self):
        self.links = []    # link* => Link[]
        self.bibinfo = []  # bibl* => BibInfo[]
        '''This field is used to hold information about the etymology
        of the kanji or kana parts of the entry. For gairaigo,
        etymological information may also be in the <lsource> element.'''
        self.etym = []     # <!ELEMENT etym (#PCDATA)>*
        self.audit = []    # audit* => Audit[]

    def to_json(self):
        return {'links': [x.to_json() for x in self.links],
                'bibinfo': [x.to_json() for x in self.bibinfo],
                'etym': self.etym,
                'audit': [x.to_json() for x in self.audit]}


class Link(object):
    '''This element holds details of linking information to
    entries in other electronic repositories. The link_tag will be
    coded to indicate the type of link (text, image, sound), the
    link_desc will provided a textual label for the link, and the
    link_uri contains the actual URI.
    <!ELEMENT links (link_tag, link_desc, link_uri)>'''
    def __init__(self, tag, desc, uri):
        self.tag = tag    # <!ELEMENT link_tag (#PCDATA)>
        self.desc = desc  # <!ELEMENT link_desc (#PCDATA)>
        self.uri = uri    # <!ELEMENT link_uri (#PCDATA)>

    def to_json(self):
        return {'tag': self.tag,
                'desc': self.desc,
                'uri': self.uri}


class BibInfo(object):
    '''Bibliographic information about the entry. The bib_tag will a
    coded reference to an entry in an external bibliographic database.
    The bib_txt field may be used for brief (local) descriptions.
    <!ELEMENT bibl (bib_tag?, bib_txt?)>
    <!ELEMENT bib_tag (#PCDATA)>
    <!ELEMENT bib_txt (#PCDATA)>
    '''
    def __init__(self, tag='', text=''):
        self.tag = tag
        self.text = text

    def set_tag(self, tag):
        if self.tag:
            logging.warning("WARNING: duplicate tag in bibinfo")
        self.tag = tag

    def set_text(self, text):
        if self.text:
            logging.warning("WARNING: duplicate text in bibinfo")
        self.text = text

    def to_json(self):
        return {'tag': self.tag, 'text': self.text}


class Audit(object):
    '''The audit element will contain the date and other information
    about updates to the entry. Can be used to record the source of
    the material.
    <!ELEMENT audit (upd_date, upd_detl)>'''
    def __init__(self, upd_date, upd_detl):
        self.upd_date = upd_date  # <!ELEMENT upd_date (#PCDATA)>
        self.upd_detl = upd_detl  # <!ELEMENT upd_detl (#PCDATA)>

    def to_json(self):
        return {'upd_date': self.upd_date, 'upd_detl': self.upd_detl}


class Sense(object):
    '''The sense element will record the translational equivalent
    of the Japanese word, plus other related information. Where there
    are several distinctly different meanings of the word, multiple
    sense elements will be employed.
    <!ELEMENT sense (stagk*, stagr*, pos*, xref*, ant*, field*, misc*, s_inf*, lsource*, dial*, gloss*, example*)>
    '''
    def __init__(self):
        '''These elements, if present, indicate that the sense is restricted
        to the lexeme represented by the keb and/or reb.'''
        self.stagk = []  # <!ELEMENT stagk (#PCDATA)>
        self.stagr = []  # <!ELEMENT stagr (#PCDATA)>

        '''Part-of-speech information about the entry/sense. Should use
        appropriate entity codes. In general where there are multiple senses
        in an entry, the part-of-speech of an earlier sense will apply to
        later senses unless there is a new part-of-speech indicated.'''
        self.pos = []   # <!ELEMENT pos (#PCDATA)>

        '''This element is used to indicate a cross-reference to another
        entry with a similar or related meaning or sense. The content of
        this element is typically a keb or reb element in another entry. In some
        cases a keb will be followed by a reb and/or a sense number to provide
        a precise target for the cross-reference. Where this happens, a JIS
        "centre-dot" (0x2126) is placed between the components of the
        cross-reference.
        <!ELEMENT xref (#PCDATA)*>'''
        self.xref = []  # xref

        '''This element is used to indicate another entry which is an
        antonym of the current entry/sense. The content of this element
        must exactly match that of a keb or reb element in another entry.'''
        self.antonym = []  # <!ELEMENT ant (#PCDATA)*>

        '''Information about the field of application of the entry/sense.
        When absent, general application is implied. Entity coding for
        specific fields of application.'''
        self.field = []  # <!ELEMENT field (#PCDATA)>

        '''This element is used for other relevant information about
        the entry/sense. As with part-of-speech, information will usually
        apply to several senses.'''
        self.misc = []  # <!ELEMENT misc (#PCDATA)>

        '''The sense-information elements provided for additional
        information to be recorded about a sense. Typical usage would
        be to indicate such things as level of currency of a sense, the
        regional variations, etc.'''
        self.info = []  # <!ELEMENT s_inf (#PCDATA)>

        self.lsource = []  # <!ELEMENT lsource (#PCDATA)>

        '''For words specifically associated with regional dialects in
        Japanese, the entity code for that dialect, e.g. ksb for Kansaiben.'''
        self.dialect = []  # <!ELEMENT dial (#PCDATA)>

        self.gloss = []  # <!ELEMENT gloss (#PCDATA | pri)*>

        '''The example elements provide for pairs of short Japanese and
        target-language phrases or sentences which exemplify the usage of the
        Japanese head-word and the target-language gloss. Words in example
        fields would typically not be indexed by a dictionary application.'''
        # It seems that this field is not used anymore!
        self.examples = []  # <!ELEMENT example (#PCDATA)>

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.text(compact=False)

    def text(self, compact=True):
        tmp = [str(x) for x in self.gloss]
        if not compact and self.pos:
            return '{gloss} ({pos})'.format(gloss='/'.join(tmp), pos=('(%s)' % '|'.join(self.pos)))
        else:
            return '/'.join(tmp)

    def to_json(self):
        sd = {}
        if self.stagk:
            sd['stagk'] = self.stagk
        if self.stagr:
            sd['stagr'] = self.stagr
        if self.pos:
            sd['pos'] = self.pos
        if self.xref:
            sd['xref'] = self.xref
        if self.antonym:
            sd['antonym'] = self.antonym
        if self.field:
            sd['field'] = self.field
        if self.misc:
            sd['misc'] = self.misc
        if self.info:
            sd['SenseInfo'] = self.info
        if self.lsource:
            sd['SenseSource'] = [x.to_json() for x in self.lsource]
        if self.dialect:
            sd['dialect'] = self.dialect
        if self.gloss:
            sd['SenseGloss'] = [x.to_json() for x in self.gloss]
        return sd


class Translation(Sense):
    ''' The trans element will record the translational equivalent
    of the Japanese name, plus other related information. (JMendict)
    <!ELEMENT trans (name_type*, xref*, trans_det*)>'''
    def __init__(self):
        super().__init__()
        self.name_type = []  # mapped to name_type*
        self.xref = []  # mapped to xref
        self.gloss = []  # mapped to trans_det

    def name_type_human(self):
        return [JMENDICT_TYPE_MAP[x] if x in JMENDICT_TYPE_MAP else x for x in self.name_type]

    def text(self, compact=True):
        tmp = [str(x) for x in self.gloss]
        types = "/".join(self.name_type) if compact else "/".join(self.name_type_human())
        return '{gloss} ({types})'.format(gloss='/'.join(tmp), types=types)

    def to_json(self):
        sd = super().to_json()
        sd['name_type'] = self.name_type
        return sd


class SenseGloss(object):
    '''Within each sense will be one or more "glosses", i.e.
        target-language words or phrases which are equivalents to the
        Japanese word. This element would normally be present, however it
        may be omitted in entries which are purely for a cross-reference.
        DTD: <!ELEMENT gloss (#PCDATA | pri)*>

        <!ATTLIST gloss xml:lang CDATA "eng">
        The xml:lang attribute defines the target language of the
        gloss. It will be coded using the three-letter language code from
        the ISO 639 standard. When absent, the value "eng" (i.e. English)
        is the default value.
        <!ATTLIST gloss g_gend CDATA #IMPLIED>
        The g_gend attribute defines the gender of the gloss (typically
        a noun in the target language. When absent, the gender is either
        not relevant or has yet to be provided.
        <!ELEMENT pri (#PCDATA)>
        These elements highlight particular target-language words which
        are strongly associated with the Japanese word. The purpose is to
        establish a set of target-language words which can effectively be
        used as head-words in a reverse target-language/Japanese relationship.'''
    def __init__(self, lang, gend, text):
        self.lang = lang
        self.gend = gend
        self.text = text

    def __repr__(self):
        return str(self)

    def __str__(self):
        tmp = [self.text]
        if self.lang and self.lang != 'eng':
            # lang = eng is trivial
            tmp.append('(lang:%s)' % self.lang)
        if self.gend:
            tmp.append('(gend:%s)' % self.gend)
        return ' '.join(tmp)

    def to_json(self):
        gd = {}
        if self.lang:
            gd['lang'] = self.lang
        if self.gend:
            gd['gend'] = self.gend
        if self.text:
            gd['text'] = self.text
        return gd


class LSource:
    '''This element records the information about the source
    language(s) of a loan-word/gairaigo. If the source language is other
    than English, the language is indicated by the xml:lang attribute.
    The element value (if any) is the source word or phrase.
    <!ATTLIST lsource xml:lang CDATA "eng">
    The xml:lang attribute defines the language(s) from which
    a loanword is drawn.  It will be coded using the three-letter language
    code from the ISO 639-2 standard. When absent, the value "eng" (i.e.
    English) is the default value. The bibliographic (B) codes are used.
    <!ATTLIST lsource ls_type CDATA #IMPLIED>
    The ls_type attribute indicates whether the lsource element
    fully or partially describes the source word or phrase of the
    loanword. If absent, it will have the implied value of "full".
    Otherwise it will contain "part".
    <!ATTLIST lsource ls_wasei CDATA #IMPLIED>
    The ls_wasei attribute indicates that the Japanese word
    has been constructed from words in the source language, and
    not from an actual phrase in that language. Most commonly used to
    indicate "waseieigo".'''

    def __init__(self, lang, lstype, wasei, text):
        self.lang = lang
        self.lstype = lstype
        self.wasei = wasei
        self.text = text

    def to_json(self):
        return {'lang': self.lang,
                'lstype': self.lstype,
                'wasei': self.wasei,
                'text': self.text}


JMENDICT_TYPES = (("surname", "family or surname"),
                  ("place", "place name"),
                  ("unclass", "unclassified name"),
                  ("company", "company name"),
                  ("product", "product name"),
                  ("work", "work of art, literature, music, etc. name"),
                  ("masc", "male given name or forename"),
                  ("fem", "female given name or forename"),
                  ("person", "full name of a particular person"),
                  ("given", "given name or forename, gender not specified"),
                  ("station", "railway station"),
                  ("organization", "organization name"),
                  ("ok", "old or irregular kana form"))
JMENDICT_TYPE_MAP = dict(JMENDICT_TYPES)
JMENDICT_TYPE_MAP_DECODE = {v: k for k, v in JMENDICT_TYPES}


class Meta(object):

    def __init__(self, key='', value=''):
        self.key = key
        self.value = value

    def __repr__(self):
        return "{{{}: {}}}".format(self.key, self.value)

    def __str__(self):
        return repr(self)


class JMDictXMLParser(object):
    '''JMDict XML parser
    '''

    def __init__(self):
        pass

    def parse_file(self, jmdict_file_path):
        ''' Parse JMDict_e.xml file and return a list of JMDEntry objects
        '''
        actual_path = os.path.abspath(os.path.expanduser(jmdict_file_path))
        logger.debug('Loading data from file: {}'.format(actual_path))

        with chio.open(actual_path, mode='rb') as jmfile:
            tree = etree.iterparse(jmfile)
            entries = []
            for event, element in tree:
                if event == 'end' and element.tag == 'entry':
                    entries.append(self.parse_entry_tag(element))
                    # and then we can clear the element to save memory
                    element.clear()
            return entries

    def parse_entry_tag(self, etag):
        '''Parse a lxml XML Node and generate a JMDEntry entry'''
        entry = JMDEntry()
        # parse ent_seq
        for child in etag:
            if child.tag == 'ent_seq':
                self.parse_ent_seq(child, entry)
            elif child.tag == 'k_ele':
                self.parse_k_ele(child, entry)
            elif child.tag == 'r_ele':
                self.parse_r_ele(child, entry)
            elif child.tag == 'info':
                self.parse_info(child, entry)
            elif child.tag == 'sense':
                self.parse_sense(child, entry)
            elif child.tag == 'trans':
                # JMendict support
                self.parse_ne_translation(child, entry)
            else:
                raise Exception("Invalid tag: %s" % child.tag)
        return entry

    def parse_ent_seq(self, seq_tag, entry):
        idseq = seq_tag.text
        if entry.idseq:
            raise Exception("WARNING: duplicated ent_seq tag")
        entry.idseq = idseq

    def get_single(self, tag_name, a_tag):
        children = a_tag.findall(tag_name)
        if len(children) == 0:
            return None
        elif len(children) > 1:
            raise Exception("There are %s %s tags in %s" % (len(children), tag_name, a_tag.tag))
        else:
            return children[0]

    def parse_k_ele(self, k_ele, entry):
        kr = KanjiForm()
        for child in k_ele:
            if child.tag == 'keb':
                kr.set_text(child.text)
            elif child.tag == 'ke_inf':
                kr.info.append(child.text)
            elif child.tag == 'ke_pri':
                kr.pri.append(child.text)
            else:
                raise Exception("WARNING: invalid tag %s in k_ele" % child.tag)
        # parse kebs
        entry.kanji_forms.append(kr)
        return kr

    def parse_r_ele(self, r_ele, entry):
        kr = KanaForm()
        for child in r_ele:
            if child.tag == 'reb':
                kr.set_text(child.text)
            elif child.tag == 're_nokanji':
                kr.nokanji = True
            elif child.tag == 're_restr':
                kr.restr.append(child.text)
            elif child.tag == 're_inf':
                kr.info.append(child.text)
            elif child.tag == 're_pri':
                kr.pri.append(child.text)
            else:
                raise Exception("WARNING: invalid tag %s in r_ele" % child.tag)
        # parse kebs
        entry.kana_forms.append(kr)
        return kr

    def parse_info(self, info_tag, entry):
        einfo = EntryInfo()
        for child in info_tag:
            if child.tag == 'links':
                self.parse_link(child, einfo)
            elif child.tag == 'bibl':
                self.parse_bibinfo(child, einfo)
            elif child.tag == 'etym':
                einfo.etym.append(child.text)
            elif child.tag == 'audit':
                self.parse_audit(child, einfo)
            else:
                raise Exception("WARNING: invalid tag in info tag (child.tag = %s)" % child.tag)
        entry.set_info(einfo)
        return einfo

    def parse_link(self, link_tag, entry_info):
        tag = self.get_single('link_tag', link_tag).text
        desc = self.get_single('link_desc', link_tag).text
        uri = self.get_single('link_uri', link_tag).text
        link = Link(tag, desc, uri)
        entry_info.links.append(link)
        return link

    def parse_bibinfo(self, bib_tag, entry_info):
        bib = BibInfo()
        for child in bib_tag:
            if child.tag == 'bib_tag':
                bib.set_tag(child.text)
            elif child.tag == 'bib_txt':
                bib.set_text(child.text)
            else:
                raise Exception("WARNING: invalid tag in bibinfo (child.tag = %s)" % child.tag)
        entry_info.bibinfo.append(bib)
        return bib

    def parse_ne_translation(self, trans_tag, entry):
        translation = Translation()
        for child in trans_tag:
            if child.tag == 'name_type':
                _name_type = JMENDICT_TYPE_MAP_DECODE[child.text] if child.text in JMENDICT_TYPE_MAP_DECODE else child.text
                translation.name_type.append(_name_type)
            elif child.tag == 'trans_det':
                # add sensegloss
                lang = self.get_attrib(trans_tag, 'xml:lang', default_value='eng')
                gloss = SenseGloss(lang=lang, gend='', text=child.text)
                translation.gloss.append(gloss)
            elif child.tag == 'xref':
                translation.xref.append(child.text)
            else:
                raise Exception("Invalid tag: {} in JMendict/trans tag".format(child.tag))
        entry.senses.append(translation)
        return translation

    def parse_sense(self, sense_tag, entry):
        sense = Sense()
        for child in sense_tag:
            if child.tag == 'stagk':
                sense.stagk.append(child.text)
            elif child.tag == 'stagr':
                sense.stagr.append(child.text)
            elif child.tag == 'pos':
                sense.pos.append(child.text)
            elif child.tag == 'xref':
                sense.xref.append(child.text)
            elif child.tag == 'ant':
                sense.antonym.append(child.text)
            elif child.tag == 'field':
                sense.field.append(child.text)
            elif child.tag == 'misc':
                sense.misc.append(child.text)
            elif child.tag == 's_inf':
                sense.info.append(child.text)
            elif child.tag == 'dial':
                sense.dialect.append(child.text)
            elif child.tag == 'example':
                sense.examples.append(child.text)
            elif child.tag == 'lsource':
                self.parse_lsource(child, sense)
            elif child.tag == 'gloss':
                self.parse_sensegloss(child, sense)
            else:
                raise Exception("WARNING: invalid tag in sense tag (child.tag = %s) content = %s" % (child.tag, etree.tostring(child)))
        entry.senses.append(sense)
        return sense

    def get_attrib(self, a_tag, attr_name, default_value=''):
        if attr_name == 'xml:lang':
            attr_name = '''{http://www.w3.org/XML/1998/namespace}lang'''
        if attr_name in a_tag.attrib:
            return a_tag.attrib[attr_name]
        else:
            return default_value

    def parse_sensegloss(self, gloss_tag, sense):
        lang = self.get_attrib(gloss_tag, 'xml:lang')
        gend = self.get_attrib(gloss_tag, 'g_gend')
        text = gloss_tag.text  # TODO: pri tag? raw text?
        gloss = SenseGloss(lang, gend, text)
        sense.gloss.append(gloss)
        return gloss

    def parse_lsource(self, lsource_tag, sense):
        lang = self.get_attrib(lsource_tag, 'xml:lang')
        lstype = self.get_attrib(lsource_tag, 'ls_type')
        wasei = self.get_attrib(lsource_tag, 'ls_wasei')
        lsource = LSource(lang, lstype, wasei, lsource_tag.text)
        sense.lsource.append(lsource)
        return lsource
