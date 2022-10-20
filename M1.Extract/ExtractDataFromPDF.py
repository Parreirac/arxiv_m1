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

logger = logging.getLogger(__name__)

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


def addValue(dico: dict, key: str, src: Optional[DocumentInformation]):
    dico[key] = src.getText(key)


def ExtractDataFrom(filename, arXiveTitle = None, arXiveAuthors = None, arXiveAbstract = None):
    pdf = PdfFileReader(filename)  # test file's existence by caller
    logger.info("ExtractDataFrom for {}".format(filename))
    rv_keywords = ""
    rv_subtitle = "" # in ordre to extrac affiliation


    rv_fileMetadata = dict()
    rv_reference_list = dict()

    try:
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

    # la supposition page[0] est trop restrictive !
    """Work on page[0] for subtitle """
    try:
        page = pdf.getPage(0)

    except PdfReadError as e:
        logger.error("Error in pdf {} no page : {}".format(filename, str(e)))    # exc_info, stack_info, stacklevel and extra.
        return rv_fileMetadata, rv_subtitle, rv_keywords, rv_reference_list

    except Exception as e:
        logger.error("Error in pdf {} (2)") # todo pra
    finally:
        pass
    # del page['/Resources']['/Font']

    # search for title

    text = MyExtractTxtFromPdfPage(page)

    if len(text) == 0:
        logger.warning("No word in 1e page in : {} (probably a bitmap !".format(filename ))
        return rv_fileMetadata, rv_subtitle, rv_keywords, rv_reference_list

        # print("@@\n", text, "\n@@\n")

    if arXiveTitle is not None:  # we uses true title to reduce subtitle size (we do not need to assume it from pdf file
        # TODO PRA report this case title from arXive has an extra uppercase

        rv_b, rv_1, rv_2 = Myfind(text, arXiveTitle, caseSensitive=False)

        if rv_b:  # index == -1:
            text = text[rv_2:]  # remove title from text buffer (and possible page header)
        else:
            logger.warning("file {} dont start with complete title".format(
                filename))  # probably title have been cut in text (with an '\n') TODO PRA create another function

    indexAB = text.find("Abstract")
    iEnd = -1
    if indexAB == -1:
        indexAB = text.find("ABSTRACT")
    if indexAB != -1:
        iEnd = indexAB + len("ABSTRACT")
        rv_subtitle = text[0:indexAB].strip(' \n')
        logger.debug("rv_subtitle {}".format(rv_subtitle))
    else:
        logger.debug("file {} dont have abstract (in first page), try with arXiveAbstract".format(filename))
        if arXiveAbstract is None:
            logger.warning("file {} dont have abstract (in first page),".format(filename))
        else:
            if arXiveAbstract is not None:
                rv_b, rv_1, iEnd = Myfind(text, arXiveAbstract, caseSensitive=False)
                if rv_b:
                    indexAB = rv_1
                    rv_subtitle = text[0:indexAB].strip(' \n')
                    logger.debug("file corrected with arXive DB")

    indexKW = text.find("Keywords", iEnd)
    if indexKW == -1:
        indexKW = text.find("KEYWORDS")
    if indexKW > 0:
        indexKW += len("Keywords")

    indexKW_end = -1

    # try to get pdf's outline (~bookmark) to catch some information
    # TODO a separer : lire en 1 fois tout le pdf
    # en cas d'échec ; tenter l'outline!
    outline:OutlineType
    try:
        outline = pdf.outline

    except TypeError as e:    # catch error with "./Files/0603080.pdf" (and others)
        logger.error("Error in pdf {} :TypeError on outline : {}".format(filename, repr(e)))    # exc_info, stack_info, stacklevel and extra.
        outline = []
    finally:
        pass

    if len(outline) != 0:  # not ( outline is None):
        firstTitle = str(outline[0]['/Title'])  # TODO PRA on suppose ici que outline[0] est le titre de l'article
        # mais cela peut être autre chose par exemple une partie 1 (voir par exemple ./Files/1001.2813.pdf)
        # dans ce cas (a verifier !) [0] est la partie 1 et [1] contient la "vraie" arbo
        indexKW_end = text.find(firstTitle, indexKW)  # start of 1er BookMark gives an end for keywords

    if indexKW_end == -1:
        indexKW_end = text.find('.\n', indexKW)  # assume keywords end with .\n

    if indexKW_end == -1:
        indexKW_end = text.find('. \n', indexKW)  # assume keywords end with . \n

    if indexKW_end == -1:
        indexKW_end = text.find('.  \n', indexKW)  # assume keywords end with .  \n

    if indexKW_end == -1:
        indexKW_end = text.find('\n', indexKW)  # assume keywords end with no final.

    if indexKW != -1:
        rv_keywords = text[indexKW:indexKW_end + 1].strip(
            ' \n')  # TODO PRA max doit etre plus grand que min, et ce n'est pas toujours vrai :(
        logger.debug("rv_keywords {}".format(rv_keywords))
    else:
        logger.warning("file {} No ending mark for keywords in".format(filename))

    """Work on REFERENCE """
    rv_reference_ctrl_set = set()


    "extract text starting with from last Bookmark (if present else skip page 0 )"

    finalText = ""

    myrange = [i for i in range(pdf.numPages) if i >= min(1, pdf.numPages - 1)]
    # myrange = [7]
    for pageNumber in myrange:
        text = MyExtractTxtFromPdfPage(pdf.getPage(pageNumber))  # .extract_text(orientations=0)
        finalText = finalText + text

    if len(text) == 0:
        logger.error("No word in : {} (probably a bitmap !".format(filename ))

    indexRef = finalText.rfind("References")

    if indexRef == -1:
        indexRef = finalText.rfind("REFERENCES")

    if indexRef == -1:
        indexRef = finalText.rfind("Références")  # TODO PRA ...
        if indexRef != -1:
            logger.warning("file {} correction from Références to REFERENCES".format(filename))

    if indexRef != -1:
        indexRef += len("REFERENCES")

    # try different corrections :
    if indexRef == -1:
        indexRef = finalText.rfind("REFRENCES") # patch ./Files/1001.1979.pdf"
        if indexRef != -1:
            logger.warning("file {} correction from REFRENCES to REFERENCES".format(filename))
            indexRef += len("REFERENCES")



        # indexRef += len("Références")

    if indexRef == -1:
        indexRef = finalText.rfind("REFERENCIAS")  # TODO PRA ...
        if indexRef != -1:
            logger.warning("file {} correction from REFERENCIAS to REFERENCES".format(filename))
            indexRef += len("REFERENCIAS")

    if indexRef == -1:
        indexRef = finalText.rfind("Bibliography")  # TODO PRA ...
        if indexRef != -1:
            logger.warning("file {} correction from Bibliography to REFERENCES".format(filename))
            indexRef += len("Bibliography")

    if indexRef == -1:
        indexRef = finalText.rfind("Источники")  # TODO PRA ...
        if indexRef != -1:
            logger.warning("file {} correction from Источники to REFERENCES".format(filename))
            indexRef += len("Источники")




    if indexRef == -1:  # TODO PRA tester si ce bloc sert encore
        # probably we have something like Re\nferences in text !
        rv_b, rv_1, iEnd = Myfind(finalText, "REFERENCES", caseSensitive=False) # todo handle multiple search (MyRfind ?)
        if rv_b:
            indexRef = iEnd
        else:
            logger.error("No reference in file {}".format(filename))

    if indexRef != -1:
        text = finalText[indexRef:]
        # testé avec https://regex101.com/ !!!
        # we assume ref like \n [x] .....
        # en une colonne : '\n\[\d+\]' en 2 : '(\n|\. +)\[\d+\]'

        # 1/ Extract ref sign
        test = re.findall(r'(\[[a-z]*[0-9]*[a-z]*\])',text,re.IGNORECASE)

        if len(test)  <= 1 :
            # test = re.findall(r'([0-9]*. )',text,re.IGNORECASE)
            test = re.findall(r'(\n\d+\..)', text, re.IGNORECASE)

            if len(test) != 0:
                test = [ x[1:] for x in test]

        if len(test) <= 1:
            logger.error("extraction of ref failed in {}".format(filename))


        # 2/ create dict with references :
        ref_dic = dict()

        current = 0
        for i in range(len(test)-1):
            k = test[i]
            i1 = text.find(k,i)
            if (i1 != -1):
                i1 += len(k)
            kp = test[i+1]
            i2 = text.find(kp, i1)
            if (i1 != -1):
                current = i2 + len(kp)
            ref_dic[k] = text[i1:i2]

        if len(test) > 0:
            k = test[-1]  # todo pra rechercher dans mon code les test[len(test)-1] pour mettre test[-1]
            i1 = text.find(k)
            if (i1 != -1):
                ref_dic[k] = text[i1:]  # TODO PRA on doit trouver mieux pour la fin !


        rv_reference_list = ref_dic
# old version
#         tempoList = re.split(r'\n\[[A-Za-z]+\d+[a-z]*\]', text)
#
#         # re.split(r'(\n|\. +)\\[\d+\\]', text)
#         if len(tempoList) == 1:
#             tempoList = re.split(r' *\[\d+\]', text)
#         if len(tempoList) == 1:  # previous split failed assume \n x. ....
#             tempoList = re.split(r' *\d+. +', text)  #  re.split(r'\n\d+\.', text)
#
#         del tempoList[0]  # If there are capturing groups in the separator and it matches at the start of the string, the result will start with an empty string. The same holds for the end of the string:
#
#         rv_reference_list = tempoList  # .add(finalText[indexRef:])

    logger.debug("rv_reference_list {}".format(rv_reference_list))
#-----------------------------------------



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
                                                                                           len(rv_reference_ctrl_set), filename))

    # add extra values (computed) to MetaData could also add url (mail)
    rv_fileMetadata["_gotoRef"] = len(rv_reference_ctrl_set)
    # if pdf.outline :
    rv_fileMetadata["_outlineSize"] = len(outline)

    return rv_fileMetadata, rv_subtitle, rv_keywords, rv_reference_list

# "./Files/1001.4405.pdf"  => pas de rubrique nommée abstract ni keywords.
# "./Files/1001.2279.pdf"  => entete et pied de page, en 2 colonnes
#"./Files/1001.2813.pdf" # decoupage asymetrique : Part I. Algorithm au lieu de Abstract. Plusieurs fois references ! => rfind
#"./Files/1001.1979.pdf" #  REFRENCES
# "./Files/1001.2813.pdf"  # reference dans l'entete -> adaptation du filtre
# "./Files/1001.4405.pdf" adaptation de l'entete
# "./Files/1001.1615.pdf" plus un rapport ! découpage fantaisiste
# file = "./Files/1001.1653.pdf" ajustement pied de page mais il reste des erreurs. [3] cite [4]
# './Files/0908.3162.pdf' texte en deux colonnes, le début des references n'est pas pris.  <<<====================================
# semble trop haut pour un pb de pied de page.

# file = "1101.0309.pdf"  # "2209.14299.pdf"
# file = "./Files/1001.2277.pdf"
# file = "./Files/1001.4251.pdf"
#file = "./Files/1001.1979.pdf" ???

file = "../Files/0905.0197.pdf"  # biblio en [2 a 3 lettres 2 chiffres ] encore de pb de n° de page :(
#file = "./Files/1004.2624.pdf" # biblio de la forme [Benhamou and Sais 1992]
# file = "./PDF32000_2008.pdf"
# file = "test.pdf"
# ./Files/1003.2586. reference de la forme Benhamou and Sais 1992
# file = "./Files/1002.2034.pdf" # en Francais ! => Références
# 0704.0304.pdf Bibliography et non references !
# 0903.3669.pdf references presentes mais dans une rubrique sans nom
# 0605119.pdf biblio de la forme [1]. xxx
# file = "./Files/1001.1653.pdf" <====== la ref ce cite elle meme  TODO PRA
# file = "./Files/1001.2279.pdf"


file = "../Files/0605123.pdf"  # portugais ! image de sein !


if __name__ == '__main__':
    print(ExtractDataFrom(file))
