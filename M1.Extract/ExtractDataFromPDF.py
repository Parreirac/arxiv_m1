# from PyPDF2 import PdfReader
import re

from typing import Optional

from PyPDF2.errors import PdfReadError
from PyPDF2.types import OutlineType

import settings  # TODO PRA si je le commente cela ne donne pas le meme resultat
import logging
# from MyStringSearch import My
from MyPyPDF2 import MyExtractTxtFromPdfPage
from PyPDF2.constants import DocumentInformationAttributes
# from PyPDF2.generic import IndirectObject
from PyPDF2 import PdfFileReader, DocumentInformation

from MyStringSearch import Myfind
import logging

# logger2 = logging.getLogger(__name__)
# logger2.setLevel(logging.INFO)  # TODO PRA cela fonctionne ?

ref_list = ["REFERENCES", "References", "Bibliography", "REFERENCE", "Références", "R´ ef´ erences", "REFRENCES",
            "REFERENCIAS", "Источники", "DAFTAR REFERENSI"]  # russe, indonesie

logger = logging.getLogger(__name__)

"""Extract Data from pdf using arXive metadata"""

"""
Extract from arXive PDF : we assumes
TITLE
autors
labs
abstract
keywords
1 bookmark

KEYWORDS (usually below abstract)
application used to create file (debug purpose)
subtitle (in order to extract geographic data)
REFERENCE in txt
REFERENCE set from annotation data (internal links) (debug purpose)
"""

"""
1101.0309 il semble qu'il y a un pb sur les fonts (qui donne l'espacement) d'ou un bug sur les mots qui sont mals découpés
1001.2405 les refences sont de la forme U, J, et n'apparaissent pas explicitement dans le texte  ! (en fait c'est : (année) )
1001.4405 ligature sur fi
1001.1653 n'est pas un article standard mais plutot un rapport de stage (sans etre pejauratif)
faire un clean sur les mots clés :   TODO PRA 
1001.2279 : "Keywords-component: Mamdani fuzzy model, fuzzy logic, auto\nzoom, digital camera"
1101.0309 (latex) j'ai la biblio en lien, mais pas les mails to
2209.14299 (word) j'ai les 2 mails mais pas la biblio
"""

"""Check if list seems to be a valid references list"""


def checkNumericalReferencesValidity(data: list):
    intList = []
    for d in data:
        if isinstance(d, int):
            intList.append(d)
        if isinstance(d, str) :
            if d.isnumeric() or d.strip(" .").isnumeric():  # todo pra strip 00
                intList.append(int(float(d.strip())))

    if len(intList) == 0: # not an integer list
        return True

    minref = 10000000
    maxref = -10000000

    for i in intList:
        minref = min(minref, i)
        maxref = max(maxref, i)

    if minref == 1 and maxref == len(intList):
        return True

    if minref == maxref:
        return False

    if minref == 0:  # problem is not only page number
        return False

    #  compter les trous, si plus d'un certain % => faux sinon vrai
    iprev = minref
    error = 0
    for i in intList:
        if (i - iprev) <= 1:
            iprev = i
        else:
            error += 1
            iprev = i

    rv = (error <= .077 * len(intList))  # TODO PRA ?  we could try to remove errors !
    if not rv:
        logger.debug("list rejected {} s= {}".format(intList, 100. * float(error) / float(len(intList))))
    return rv


def checkReferencesDict(data: dict):
    if len(data.keys()) < 2:
        return False

    for k, v in data.items():
        if len(k) == 0 or len(v) == 0:
            return False

    if not checkNumericalReferencesValidity(list(data.keys())):
        return False

    return True


def addValue(dico: dict, key: str, src: Optional[DocumentInformation]):
    dico[key] = src.getText(key)


def getInfoFromOutlines(pdf, _text):
    # try to get pdf's outline (~bookmark) to catch some information

    _outline: OutlineType
    try:
        _outline = pdf.outline

    except TypeError as _e:  # catch error with "./Files/0603080.pdf" (and others)
        logger.error(
            "Error in pdf {} :TypeError on outline : {}")  # .format(filename, repr(e)))    # exc_info, stack_info, stacklevel and extra.
        _outline = []
    finally:
        pass


def complexRSearch(buff: str, sub: str):  # TODO mettre un start ?
    rv = buff.rfind(sub)
    if rv != -1:
        return True, rv, rv + len(sub)
    else:
        return Myfind(buff, sub, caseSensitive=False, Reverse=True)


def ExtractDataFrom(filename, arXiveTitle=None, _arXiveAuthors=None, arXiveAbstract=None):
    pdf = PdfFileReader(filename, strict=False)  # test file's existence by caller
    logger.info("ExtractDataFrom for {}".format(filename))
    rv_keywords = ""
    rv_subtitle = ""  # in ordre to extrac affiliation
    rv_fileMetadata = dict()
    rv_reference_list = dict()

    try:

        if not pdf.documentInfo is None:
            addValue(rv_fileMetadata, DocumentInformationAttributes.TITLE, pdf.documentInfo)
            addValue(rv_fileMetadata, DocumentInformationAttributes.AUTHOR, pdf.documentInfo)
            addValue(rv_fileMetadata, DocumentInformationAttributes.CREATOR, pdf.documentInfo)
            addValue(rv_fileMetadata, DocumentInformationAttributes.KEYWORDS, pdf.documentInfo)
            addValue(rv_fileMetadata, DocumentInformationAttributes.PRODUCER, pdf.documentInfo)
            addValue(rv_fileMetadata, DocumentInformationAttributes.CREATION_DATE, pdf.documentInfo)
            addValue(rv_fileMetadata, DocumentInformationAttributes.MOD_DATE, pdf.documentInfo)
            addValue(rv_fileMetadata, DocumentInformationAttributes.SUBJECT, pdf.documentInfo)
            addValue(rv_fileMetadata, DocumentInformationAttributes.TRAPPED, pdf.documentInfo)

        logger.debug("PDF metadata {}".format(repr(rv_fileMetadata)))
    except PdfReadError as e:
        logger.error("Error in pdf {} for metadata : {}".format(filename, str(e)))
    finally:
        pass

    BufferText = ""

    try:

        # tab = range(pdf.numPages)
        for pageNumber in range(pdf.numPages):
            page = pdf.getPage(pageNumber)

            # logger.debug("convert page {} ".format(pageNumber))
            curtext = MyExtractTxtFromPdfPage(page)  # .extract_text(orientations=0)
            BufferText += curtext

        if len(BufferText) == 0:
            logger.error("No word in : {} (probably a bitmap !)".format(filename))
            return rv_fileMetadata, rv_subtitle, rv_keywords, rv_reference_list

    except PdfReadError as e:
        logger.error(
            "Error in pdf {} no page : {}".format(filename, str(e)))  # exc_info, stack_info, stacklevel and extra.
        return rv_fileMetadata, rv_subtitle, rv_keywords, rv_reference_list

    except Exception as _e:
        logger.error("Error in pdf  (2)")  # todo pra
    finally:
        pass
    # del page['/Resources']['/Font']

    # search for title

    # text = MyExtractTxtFromPdfPage(page)
    #
    # if len(text) == 0:
    #     logger.warning("No word in 1e page in : {} (probably a bitmap !".format(filename ))
    #     return rv_fileMetadata, rv_subtitle, rv_keywords, rv_reference_list
    #
    # print("@@\n", BufferText, "\n@@\n")

    # TODO PRA  1002.0102  -> c'est un livre il y a un table of content. donc on doit prendre la deuxieme occurence dans
    # ce cas...

    currentStartIndex = 0
    if arXiveTitle is not None:  # we uses true title to reduce subtitle size (we do not need to assume it from pdf file
        # TODO PRA report this case title from arXive has an extra uppercase

        rv_b, rv_1, rv_2 = Myfind(BufferText, arXiveTitle, caseSensitive=False)

        if rv_b:  # index == -1:
            currentStartIndex = rv_2  # remove title from text buffer (and possible page header)
            # text = text[rv_2:]
        else:
            logger.warning("file {} dont start with complete title".format(filename))

    indexAB = BufferText.find("Abstract", currentStartIndex)
    iEnd = -1
    if indexAB == -1:
        indexAB = BufferText.find("ABSTRACT", currentStartIndex)
    if indexAB != -1:
        iEnd = indexAB + len("ABSTRACT")
        currentStartIndex = iEnd
        rv_subtitle = BufferText[currentStartIndex:indexAB].strip(' \n')
        logger.debug("rv_subtitle {}".format(rv_subtitle))
    else:
        # logger.debug("file {} dont have abstract, try with arXiveAbstract".format(filename))
        if arXiveAbstract is None:
            logger.warning("file {} dont have abstract".format(filename))
        else:
            if arXiveAbstract is not None:
                rv_b, rv_1, iEnd = Myfind(BufferText, arXiveAbstract, start=currentStartIndex, caseSensitive=False)
                if rv_b:
                    indexAB = rv_1
                    rv_subtitle = BufferText[currentStartIndex:indexAB].strip(' \n')
                    logger.debug("file corrected with arXive DB")
                    currentStartIndex = indexAB

    indexKW = BufferText.find("Keywords", currentStartIndex)
    if indexKW == -1:
        indexKW = BufferText.find("KEYWORDS")
    if indexKW > 0:
        indexKW += len("Keywords")

    # indexKW_end = -1

    indexKW_end = BufferText.find('.\n', indexKW)  # assume keywords end with .\n

    if indexKW_end == -1:
        indexKW_end = BufferText.find('. \n', indexKW)  # assume keywords end with . \n

    if indexKW_end == -1:
        indexKW_end = BufferText.find('.  \n', indexKW)  # assume keywords end with .  \n

    if indexKW_end == -1:
        indexKW_end = BufferText.find('\n', indexKW)  # assume keywords end with no final.

    if indexKW != -1:
        rv_keywords = BufferText[indexKW:indexKW_end + 1].strip(
            ' \n')  # TODO PRA max doit etre plus grand que min, et ce n'est pas toujours vrai :(
        logger.debug("rv_keywords {}".format(rv_keywords))
        currentStartIndex = indexKW_end + 1
    else:
        logger.warning(" No ending mark for keywords in file {}".format(filename))

    """Work on REFERENCE """
    rv_reference_ctrl_set = set()

    "extract text starting with from last Bookmark (if present else skip page 0 )"

    indexRef = -1
    for word in ref_list:
        rb, r1, r2 = complexRSearch(BufferText, word)
        if rb:  # match :
            indexRef = r2
            break
    if indexRef == -1:
        logger.error("No references label in file {}".format(filename))

    if indexRef != -1:
        text = BufferText[indexRef - 1:]
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
                rv = checkNumericalReferencesValidity(test)
                if not rv:
                    test = []

        if len(test) <= 1:
            # test = re.findall(r'([0-9]*. )',text,re.IGNORECASE)
            test = re.findall(r'(\n\d+\.)', text,
                              re.IGNORECASE)  # dans ce cas la on devrait avoir au final 1. 2. 3. .... (avec des numero de pages :()

            if len(test) != 0:
                test = [x[1:] for x in test]
                rv = checkNumericalReferencesValidity(test)
                if not rv:
                    test = []

            # 2/ create dict with references :
        ref_dic = dict()

        current = 0
        for i in range(len(test) - 1):  # todo pra ? tenter des virer les numéro incoherents avant (n° de page)
            k = test[i]
            i1 = text.find(k, current)
            if i1 != -1:
                i1 += len(k)
            kp = test[i + 1]
            i2 = text.find(kp, i1)
            if i1 != -1:
                current = i2 #+ len(kp)
            ref_dic[k] = text[i1:i2]

        if len(test) > 0:
            k = test[-1]  # todo pra rechercher dans mon code les test[len(test)-1] pour mettre test[-1]
            i1 = text.find(k,current) + len(k)
            if i1 != -1: # TODO et si -1 ?????
                ref_dic[k] = text[i1:]  # TODO PRA on doit trouver mieux pour la fin !

        if not checkReferencesDict(ref_dic):
            logger.debug("invalidate References dict {}".format(filename))
            ref_dic.clear()

        if len(ref_dic) == 0:  # create own table using end of refence
            test = re.findall(r'(.*\.\n)', text)  # get last full line of ref
            if len(test) > 1:
                current = 1
                for i in range(len(test)):
                    lastcurrent = current
                    k = str(i + 1)
                    sub = test[i]
                    i1 = text.find(sub, lastcurrent)
                    current = i1 + len(sub)
                    ref_dic[k] = text[lastcurrent:current]

                if not checkReferencesDict(ref_dic):
                    logger.debug("invalidate References dict {}".format(filename))
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
                    logger.debug("invalidate References dict {}".format(filename))
                    ref_dic.clear()
        # (\n[A-Z][a-z]*) qui commence

        rv_reference_list = ref_dic

        if len(ref_dic) <= 1:
            logger.error("extraction of ref data failed in {}, try ....".format(filename))

    logger.debug("rv_reference_list {}".format(rv_reference_list))

    # -----------------------------------------
    # for debug purpose, extract REFERENCES from internal PDF goto REFERENCES (in annots)
    # unfortunately only available with LaTEX
    for page in range(pdf.numPages):
        pdfPage = pdf.getPage(page)

        if '/Annots' in pdfPage:
            for item in pdfPage['/Annots']:
                obj = item.get_object()
                if '/Dest' in obj:  # obj['/Dest']:
                    res = str(obj['/Dest'])
                    if len(res) != 0 and (res.startswith("cite.") or res.startswith("b'cite.")):
                        rv_reference_ctrl_set.add(res[5:])

    if len(rv_reference_ctrl_set) != 0:
        logger.debug("rv_reference_ctrl_set {}".format(rv_reference_ctrl_set))

    if len(rv_reference_ctrl_set) != 0 and len(rv_reference_ctrl_set) != len(rv_reference_list):
        logger.error("Error on REFERENCES size, extraction :{} links {} in file {}".format(len(rv_reference_list),
                                                                                           len(rv_reference_ctrl_set),
                                                                                           filename))

    # add extra values (computed) to MetaData could also add url (mail)
    rv_fileMetadata["_gotoRef"] = len(rv_reference_ctrl_set)

    # if pdf.outline :
    # rv_fileMetadata["_outlineSize"] = len(outline)

    return rv_fileMetadata, rv_subtitle, rv_keywords, rv_reference_list


# "./Files/1001.4405.pdf"  => pas de rubrique nommée abstract ni keywords.
# "./Files/1001.2279.pdf"  => entete et pied de page, en 2 colonnes
# "./Files/1001.2813.pdf" # decoupage asymetrique : Part I. Algorithm au lieu de Abstract. Plusieurs fois references ! => rfind
# "./Files/1001.1979.pdf" #  REFRENCES
# "./Files/1001.2813.pdf"  # reference dans l'entete -> adaptation du filtre
# "./Files/1001.4405.pdf" adaptation de l'entete
# "./Files/1001.1615.pdf" plus un rapport ! découpage fantaisiste
# file = "./Files/1001.1653.pdf" ajustement pied de page mais il reste des erreurs. [3] cite [4]
# './Files/0908.3162.pdf' texte en deux colonnes, le début des references n'est pas pris.  <<<====================================
# semble trop haut pour un pb de pied de page.

# file = "1101.0309.pdf"  # "2209.14299.pdf"
# file = "./Files/1001.2277.pdf"
# file = "./Files/1001.4251.pdf"
# file = "./Files/1001.1979.pdf" ???

_file = "../Files/0905.0197.pdf"  # biblio en [2 a 3 lettres 2 chiffres ] encore de pb de n° de page :(
# file = "./Files/1004.2624.pdf" # biblio de la forme [Benhamou and Sais 1992]
# file = "./PDF32000_2008.pdf"
# file = "test.pdf"
# ./Files/1003.2586. reference de la forme Benhamou and Sais 1992
# file = "./Files/1002.2034.pdf" # en Francais ! => Références
# 0704.0304.pdf Bibliography et non references !
# 0903.3669.pdf references presentes mais dans une rubrique sans nom
# 0605119.pdf biblio de la forme [1]. xxx
# file = "./Files/1001.1653.pdf" <====== la ref se cite elle meme
# file = "./Files/1001.2279.pdf"


# file = "../Files/0605123.pdf"  # portugais ! image de sein !
#
# file = "./.././Files/0605123.pdf"

# ./.././Files/0605123.pdf   erreur TypeError('replace() argument 1 must be s
file = "./.././Files/1008.1333.pdf"  # 1  bkal 2 hhuiu
file = "./.././Files/1506.05282.pdf"
# a tester arXiv:1506.01432   arXiv:1505.07872  arXiv:1505.07751 arXiv:1505.02729
# ./.././Files/1504.04716.pdf # TODO mal découpé :s encore
# ./.././Files/1502.05974.pdf
# ./.././Files/1509.07897.pdf
# ./.././Files/1507.05895.pdf

file = "./.././Files/1302.4956.pdf"  # ==== > etrangement vide !  ./.././Files/1302.1561.pdf avec une figure dans les ref

file = "./.././Files/1511.07373.pdf"  # preferences apparait apres les references :(
file = "./.././Files/1509.03247.pdf"

# TODO
# arXiv:1506.00366
# arXiv:1508.06235
file = "./.././Files/1506.00366.pdf"

# ./.././Files/1509.07897.pdf # le mot references n'apparait pas :
# ./.././Files/1507.05895.pdf # le mot references n'apparait pas :
if __name__ == '__main__':
    print(ExtractDataFrom(file))
