
'''Extract Data from pdf using arXiv metadata'''

import logging
import re
import string

from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from PyPDF2.types import OutlineType

from MyPyPDF2 import MyExtractTxtFromPdfPage
from MyStringSearch import Myfind


ref_list = ["REFERENCES", "References", "Bibliography",
            "REFERENCE", "Références", "R´ ef´ erences",
            "REFRENCES", "REFERENCIAS",
            "Источники",  # russe
            "DAFTAR REFERENSI"]  # indonesie

keywords = ["index terms","keywords and phrases","keywords-component",
            "Keywords-IRC","Keyword for classification","Key-Words","keywords",
            "Mots-clés","Kata kunci"]

firstBlock = ["introduction","motivation","outline","preliminaries","the history","background"]


logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

def checkNumericalReferencesValidity(data: list):
    """Check if list seems to be a valid references list"""
    int_list = []
    for dat in data:
        if isinstance(dat, int):
            int_list.append(dat)
        if isinstance(dat, str):
            if dat.isnumeric() or dat.strip(" .").isnumeric():
                int_list.append(int(float(dat.strip())))

    if len(int_list) == 0:  # not an integer list
        return True

    minref = 10000000
    maxref = -10000000

    for i in int_list:
        minref = min(minref, i)
        maxref = max(maxref, i)

    if minref == 1 and maxref == len(int_list):
        return True

    if minref == maxref:
        return False

    if minref == 0:  # problem is not only page number
        return False

    #  compter les trous, si plus d'un certain % => faux sinon vrai
    iprev = minref
    error = 0
    for i in int_list:
        if (i - iprev) <= 1:
            iprev = i
        else:
            error += 1
            iprev = i

    retv = error <= .077 * len(int_list)
    if not retv:
        logger.debug("list rejected %s s= %s", int_list, 100. * float(error) / float(len(int_list)))
    return retv


def checkReferencesDict(data: dict):
    """Check if list seems to be a valid references list"""
    if len(data.keys()) < 2:
        return False

    for k_it, v_it in data.items():
        if len(k_it) == 0 or len(v_it) == 0:
            return False

    if not checkNumericalReferencesValidity(list(data.keys())):
        return False

    return True


def get_info_from_outlines(pdf):
    """try to get pdf's outline (~bookmark) to catch some information"""

    _outline: OutlineType
    try:
        _outline = pdf.outline

    except TypeError as _e:  # catch error with "./Files/0603080.pdf" (and others)
        logger.error(
            "Error in pdf {} :TypeError on outline : {}")  # .format(filename, repr(e)))
        _outline = []
    finally:
        pass
    return _outline

def complexRSearch(buff: str, sub: str):  # TODO mettre un start ?
    ret_v = buff.rfind(sub)
    if ret_v != -1:
        return True, ret_v, ret_v + len(sub)

    return Myfind(buff, sub, caseSensitive=False, Reverse=True)


def clean_keyword(buff:str):
    # Pour corriger les Ligatures et autres caractères spéciaux
    transform = {  chr(0x0152): 'OE', chr(0x0153): 'oe', chr(0x0132): 'IJ', chr(0x0133): 'ij', chr(0x1d6b): 'ue',
                   chr(0xfb00): 'ff', chr(0xfb01): 'fi', chr(0xfb02): 'fl', chr(0xfb03): 'ffi', chr(0xfb04): 'ffl',
                   chr(0xfb05): 'ft', chr(0xfb06): 'st', '·': '; ', ',':'; '}

    #for c in buff:
    #    print(c,repr(c))
    #print('\n')

    buff = buff.strip()

    if len(buff)==0:
        return ''

    for key, value in transform.items():
        #print((key),value)
        #if str(key) in buff:
            #print((key), value)
            #buff = buff.replace()
        ##buff = re.sub((key), value, buff, 0)
        buff = buff.replace(key,value)

    i_start = 0
    to_remove = string.punctuation +' '+ '—'+'\n' + '–' # +'' + '' + '|'
    while buff[i_start] in to_remove:
        i_start = i_start + 1
    buff = buff[i_start:]
    to_replace = '|' + '–' +'' + ''# +'\n'

    buff2 =""
    for c in buff:# buff2 = [c for c in buff if c not in to_replace else '; ']
        if c in to_replace:
            buff2 = buff2 + ';'
        else:
            buff2 = buff2 + c


    return buff2

# indonesie !   Keywords-IRC -> 1001.2665.pdf
# Categories and Subject Descriptors  mais parfois on a ca ET KW


def addspaces(texte:str):
    res = ""
    for charactere in texte:
        res = res + charactere+" *"
    return res
def search_keywords(buffer_text,current_start):
    '''search keyword in into a pdf2txt buffer'''

    index_kw = -1
    for mot in keywords:
        pattern = ""+addspaces(mot)+""
        match = re.search(pattern, buffer_text[current_start:], re.IGNORECASE)

        if match != None:
            index_kw = current_start+ match.end()
            #i1 = match.start()
            # i2 = match.end()
            #index_kw_end = min(index_kw_end, index_kw + match.start() - 1)
            break



    if index_kw == -1:
        return -1,-1,""

    to_remove = string.punctuation + ' ' + '—' + '\n' + '–'  # +'' + '' + '|'

    while buffer_text[index_kw] in to_remove:
        index_kw+=1

    tmp = buffer_text[index_kw:]

    #index_kw = buffer_text.find("Keywords", current_start)
    #if index_kw == -1:
    #    index_kw = buffer_text.find("KEYWORDS")
    #if index_kw > 0:
    #    index_kw += len("Keywords")

    # index_kw_end = -1

    index_kw_end = buffer_text.find('.\n', index_kw)  # assume keywords end with .\n

    if index_kw_end == -1:
        index_kw_end = buffer_text.find('. \n', index_kw)  # assume keywords end with . \n
    else:
        index_kw_end2 = buffer_text.find('. \n', index_kw)
        if index_kw_end2 != -1:
            index_kw_end = min(index_kw_end, index_kw_end2)

    if index_kw_end == -1:
        index_kw_end = buffer_text.find('.  \n', index_kw)  # assume keywords end with .  \n
    else:
        index_kw_end2 = buffer_text.find('.  \n', index_kw)
        if index_kw_end2 != -1:
            index_kw_end = min(index_kw_end, index_kw_end2)

    if index_kw_end == -1:
        index_kw_end = buffer_text.find('\n\n', index_kw)  # assume keywords end with no final.
    else:
        index_kw_end2 = buffer_text.find('\n\n', index_kw)
        if index_kw_end2 != -1 and index_kw_end2 > index_kw + 4:  # +4 pour les éventuels espaces
            index_kw_end = min(index_kw_end, index_kw_end2)

    if index_kw_end == -1:
        index_kw_end = buffer_text.find('\n \n', index_kw)  # assume keywords end with no final.
    else:
        index_kw_end2 = buffer_text.find('\n \n', index_kw)
        if index_kw_end2 != -1 and index_kw_end2 > index_kw + 4:  # +4 pour les éventuels espaces
            index_kw_end = min(index_kw_end, index_kw_end2)

    if index_kw_end == -1:
        index_kw_end = buffer_text.find('\n', index_kw)  # assume keywords end with no final.

    for block in firstBlock:
        pattern = "(\d|I)*\.*\t*\r* *"+addspaces(block)
        match = re.search(pattern, buffer_text[index_kw+1:], re.IGNORECASE) # +1 pour empecher que le mot soit le 1er mot-cé
        if match != None:
            i1 = match.start()
            # i2 = match.end()
            if index_kw_end == -1:
                index_kw_end = index_kw + match.start()
            else:
                index_kw_end = min(index_kw_end, index_kw + match.start())
            #break

    pattern = addspaces("abstract") # sans numero de rubrique
    match = re.search(pattern, buffer_text[index_kw+1:], re.IGNORECASE)
    if match != None:
        i1 = match.start()
        # i2 = match.end()
        index_kw_end = min(index_kw_end, index_kw + match.start() - 1)



    #match = re.search("(\d|I)*\.*\t*\r* *i *n *t *r *o", buffer_text[index_kw:], re.IGNORECASE)

    #if match != None:
    #    i1 = match.start()
    #    # i2 = match.end()
    #    index_kw_end = min(index_kw_end, index_kw + match.start() - 1)

    # search for ∗Corresponding author

    match = re.search("\∗* *The authors", buffer_text[index_kw:], re.IGNORECASE)
    if match != None:
        i1 = match.start()
        # i2 = match.end()
        index_kw_end = min(index_kw_end, index_kw + match.start() - 1)

    match = re.search("\∗* *Corresponding", buffer_text[index_kw:], re.IGNORECASE)
    if match != None:
        i1 = match.start()
        # i2 = match.end()
        index_kw_end = min(index_kw_end, index_kw + match.start() - 1)

    match = re.search("E-mail", buffer_text[index_kw:], re.IGNORECASE)
    if match != None:
        i1 = match.start()
        # i2 = match.end()
        index_kw_end = min(index_kw_end, index_kw + match.start() - 1)
    match = re.search(" *acknowledgment", buffer_text[index_kw:], re.IGNORECASE)
    if match != None:
        i1 = match.start()
        # i2 = match.end()
        index_kw_end = min(index_kw_end, index_kw + match.start() - 1)

    match = re.search(" *preprint", buffer_text[index_kw:], re.IGNORECASE)
    if match != None:
        i1 = match.start()
        # i2 = match.end()
        index_kw_end = min(index_kw_end, index_kw + match.start() - 1)

    match = re.search(" *submited", buffer_text[index_kw:], re.IGNORECASE)
    if match != None:
        i1 = match.start()
        # i2 = match.end()
        index_kw_end = min(index_kw_end, index_kw + match.start() - 1)

    match = re.search(" *This work is", buffer_text[index_kw:], re.IGNORECASE)
    if match != None:
        i1 = match.start()
        # i2 = match.end()
        index_kw_end = min(index_kw_end, index_kw + match.start() - 1)

    match = re.search("permission to", buffer_text[index_kw:], re.IGNORECASE)
    if match != None:
        i1 = match.start()
        # i2 = match.end()
        index_kw_end = min(index_kw_end, index_kw + match.start() - 1)

    match = re.search("table of contents", buffer_text[index_kw:], re.IGNORECASE)
    if match != None:
        i1 = match.start()
        # i2 = match.end()
        index_kw_end = min(index_kw_end, index_kw + match.start() - 1)

    match = re.search("Figure", buffer_text[index_kw:], re.IGNORECASE)
    if match != None:
        i1 = match.start()
        # i2 = match.end()
        index_kw_end = min(index_kw_end, index_kw + match.start() - 1)

    # tmp_index = buffer_text.find(' Intro', index_kw) # A Intro ou 1 Intro .....
    #    if (tmp_index != -1):
    #        index_kw_end = min(index_kw_end,tmp_index-1)

    #    tmp_index = buffer_text.find(' INTRO', index_kw) # A Intro ou 1 Intro .....
    #    if (tmp_index != -1):
    #        index_kw_end = min(index_kw_end,tmp_index-1)

    tmp_index = buffer_text.find('ACM ', index_kw)  # catégorie de doc ACM
    if (tmp_index != -1):
        index_kw_end = min(index_kw_end, tmp_index)

    if index_kw != -1:
        if index_kw_end - index_kw > 325: # ne pas réduire ce seuil, cela tronque des mots-clés
            logger.debug("truncation of the keywords field (%s)", index_kw_end - index_kw)
            index_kw_end = index_kw + 325
        # TODO PRA max doit etre plus grand que min, et ce n'est pas toujours vrai :(
        rv_keywords = clean_keyword(buffer_text[index_kw:index_kw_end])  # .strip(' \n'))
        logger.debug("rv_keywords :%s", rv_keywords)
        current_start = index_kw_end + 1

    return index_kw,index_kw_end,rv_keywords

def ExtractDataFrom(filename, arXivTitle=None, _arXivAuthors=None, arXivAbstract=None):
    """Fonction principale d'analyse du pdf"""
    pdf = PdfReader(filename, strict=False)  # test file's existence by caller
    logger.info("ExtractDataFrom for %s", filename)
    rv_keywords = ""
    rv_subtitle = ""  # in ordre to extrac affiliation
    rv_file_metadata = {}
    rv_reference_list = {}

    try:
        if pdf.metadata is not None:
            for cle, valeur in pdf.metadata.items():
                rv_file_metadata[cle] = valeur
        # >>>>>>>>>>>>>>>>>>>>>>> AFFICHAGE DES metadata
        #logger.debug("PDF metadata %s", repr(rv_file_metadata))
    except PdfReadError as err:
        logger.error("Error in pdf %s for metadata : %s", filename, str(err))
    finally:
        pass

    buffer_text = ""

    try:

        # tab = range(pdf.numPages)
        for _, page in enumerate(pdf.pages): #  in range(len(pdf.pages)):  # range(pdf.numPages)pdf.numPages):
            #page = pdf.pages[pageNumber]  # .getPage(pageNumber)

            # logger.debug("convert page {} ".format(pageNumber))
            curtext = MyExtractTxtFromPdfPage(page)  # .extract_text(orientations=0)
            buffer_text += curtext

        if len(buffer_text) == 0:
            logger.error("No word in : %s (probably a bitmap !)", filename)
            return rv_file_metadata, rv_subtitle, rv_keywords, rv_reference_list

    except PdfReadError as err:
        logger.error(
            "Error in pdf %s no page : %s", filename, str(err))
        return rv_file_metadata, rv_subtitle, rv_keywords, rv_reference_list

    except Exception as _e:
        logger.error("Error in pdf  (2)")
    finally:
        pass

    current_start = 0
    if arXivTitle is not None:
        # we uses true title to reduce subtitle size (we do not need to assume it from pdf file
        # TODO PRA report this case title from arXiv has an extra uppercase

        rv_b, rv_1, rv_2 = Myfind(buffer_text, arXivTitle, caseSensitive=False)

        if rv_b:  # index == -1:
            current_start = rv_2  # remove title from text buffer (and possible page header)
            # text = text[rv_2:]
        else:
            logger.warning("file %s dont start with complete title", filename)

    # Les mots-clés peuvent être dans un tableau au meme niveau que l'abstract (
    # index_ab = buffer_text.find("Abstract", current_start)
    # i_end = -1
    # if index_ab == -1:
    #     index_ab = buffer_text.find("ABSTRACT", current_start)
    # if index_ab != -1:
    #     i_end = index_ab + len("ABSTRACT")
    #     current_start = i_end
    #     rv_subtitle = buffer_text[current_start:index_ab].strip(' \n')
    #     logger.debug("rv_subtitle %s", rv_subtitle)
    # else:
    #     # logger.debug("file {} dont have abstract, try with arXivAbstract".format(filename))
    #     if arXivAbstract is None:
    #         logger.warning("file %s dont have abstract", filename)
    #     else:
    #         if arXivAbstract is not None:
    #             rv_b, rv_1, i_end = Myfind(buffer_text, arXivAbstract, start=current_start, caseSensitive=False)
    #             if rv_b:
    #                 index_ab = rv_1
    #                 rv_subtitle = buffer_text[current_start:index_ab].strip(' \n')
    #                 logger.debug("file corrected with arXiv DB")
    #                 current_start = index_ab

#    outl = get_info_from_outlines(pdf)
#    titre_1 = ""

    i_start, i_end, rv_keywords =  search_keywords(buffer_text, current_start)
    if i_start!=-1:
        current_start = i_end + 1
    else:
        logger.warning(" No ending mark for keywords in file %s", filename)

    # Work on REFERENCE
    rv_reference_ctrl_set = set()

    # extract text starting with from last Bookmark (if present else skip page 0 )

    index_ref = -1
    for word in ref_list:

        reb, _, re2 = complexRSearch(buffer_text, word)
        if reb:  # match :
            index_ref = re2
            break
    if index_ref == -1:
        logger.error("No references label in file %s", filename)

    if index_ref != -1:
        text = buffer_text[index_ref - 1:]
        # testé avec https://regex101.com/ !!!
        # we assume ref like \n [x] .....
        # en une colonne : '\n\[\d+\]' en 2 : '(\n|\. +)\[\d+\]'

        # 1/ Extract ref sign

        test = re.findall(r'(\[[0-9]*\])', text)

        if len(test) <= 1:
            test = re.findall(r'(\[[a-z]+[0-9]*[a-z]*\])', text, re.IGNORECASE)

        if len(test) <= 1:
            test = re.findall(r'(\[[A-Z][a-z]+.*\d{4} *\])', text)

        if len(test) <= 1:
            test = re.findall(r'( \d{1,3}\.)', text)  # pas de sauts de ligne, juste des espaces :/
            if len(test) > 0:
                rev = checkNumericalReferencesValidity(test)
                if not rev:
                    test = []

        if len(test) <= 1:
            # test = re.findall(r'([0-9]*. )',text,re.IGNORECASE)
            # dans ce cas la on devrait avoir au final 1. 2. 3. .... (avec des numero de pages :()
            test = re.findall(r'(\n\d+\.)', text, re.IGNORECASE)
            if len(test) != 0:
                test = [x[1:] for x in test]
                rev = checkNumericalReferencesValidity(test)
                if not rev:
                    test = []

            # 2/ create dict with references :
        ref_dic = {}

        current = 0
        # todo pra ? tenter des virer les numéro incoherents avant (n° de page)
        for i in range(len(test) - 1):
            k = test[i]
            i1 = text.find(k, current)
            if i1 != -1:
                i1 += len(k)
            kp = test[i + 1]
            i2 = text.find(kp, i1)
            if i1 != -1:
                current = i2  # + len(kp)
            ref_dic[k] = text[i1:i2]

        if len(test) > 0:
            k = test[-1]
            i1 = text.find(k, current) + len(k)
            if i1 != -1:  # TODO et si -1 ?????
                ref_dic[k] = text[i1:]  # TODO PRA on doit trouver mieux pour la fin !

        if not checkReferencesDict(ref_dic):
            logger.debug("invalidate References dict %s", filename)
            ref_dic.clear()

        if len(ref_dic) == 0:  # create own table using end of refence
            test = re.findall(r'(.*\.\n)', text)  # get last full line of ref
            if len(test) > 1:
                current = 1
                # for i, season in enumerate(seasons):
                # print(i, season)

                for i, sub in enumerate(test):  # in range(len(test)):
                    lastcurrent = current
                    k = str(i + 1)
                    # sub = test[i]
                    i1 = text.find(sub, lastcurrent)
                    current = i1 + len(sub)
                    ref_dic[k] = text[lastcurrent:current]

                if not checkReferencesDict(ref_dic):
                    logger.debug("invalidate References dict %s", filename)
                    ref_dic.clear()

        if len(ref_dic) == 0:  # create own table using beginning (no end .)
            test = re.findall(r'(\n[A-Z][a-z]*)', text)  # get last full line of ref
            if len(test) > 1:
                current = 1
                for i in range(len(test) - 1):
                    k = str(i + 1)
                    sub = test[i + 1]
                    i1 = text.find(sub, current)
                    i1 += len(sub)
                    ref_dic[k] = text[current:i1]
                    current = i1

                if not checkReferencesDict(ref_dic):
                    logger.debug("invalidate References dict %s", filename)
                    ref_dic.clear()
        # (\n[A-Z][a-z]*) qui commence

        rv_reference_list = ref_dic

        if len(ref_dic) <= 1:
            logger.error("extraction of ref data failed in %s, try ....", filename)
    # >>>>>>>>>>>>>>>>>>>>>>> AFFICHAGE DES REFERENCES
    #logger.debug("rv_reference_list %s", rv_reference_list)

    # -----------------------------------------
    # for debug purpose, extract REFERENCES from internal PDF goto REFERENCES (in annots)
    # unfortunately only available with LaTEX
    for i, page in enumerate(pdf.pages):  # page in range(len(pdf.pages)):# pdf.numPages):
        # pdfPage = page # pdf.pages[page]
        if '/Annots' in page:
            for item in page['/Annots']:
                obj = item.get_object()
                if '/Dest' in obj:  # obj['/Dest']:
                    res = str(obj['/Dest'])
                    if len(res) != 0 and (res.startswith("cite.") or res.startswith("b'cite.")):
                        rv_reference_ctrl_set.add(res[5:])

    if len(rv_reference_ctrl_set) != 0:
        logger.debug("rv_reference_ctrl_set %s", rv_reference_ctrl_set)

    if len(rv_reference_ctrl_set) != 0 and len(rv_reference_ctrl_set) != len(rv_reference_list):
        logger.error("Error on REFERENCES size, extraction :%s links %s in file %s",
                     len(rv_reference_list),
                     len(rv_reference_ctrl_set),
                     filename)

    # add extra values (computed) to MetaData could also add url (mail)
    rv_file_metadata["_gotoRef"] = len(rv_reference_ctrl_set)

    # if pdf.outline :
    # rv_file_metadata["_outlineSize"] = len(outline)

    return rv_file_metadata, rv_subtitle, rv_keywords, rv_reference_list


FILE = "/home/christophe/mon_depot/Files/1509.03247.pdf"


if __name__ == '__main__':
    print(ExtractDataFrom(FILE))









