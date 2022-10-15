# from PyPDF2 import PdfReader
import re
import logging
from typing import Optional

# from MyStringSearch import My
from MyPyPDF2 import MyExtractText
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

faire un clean sur les mots clés :   TODO PRA 
1001.2279 : "Keywords-component: Mamdani fuzzy model, fuzzy logic, auto\nzoom, digital camera"


1101.0309 (latex) j'ai la biblio en lien, mais pas les mails to
2209.14299 (word) j'ai les 2 mails mais pas la biblio
"""


def addValue(dico: dict, key: str, src: Optional[DocumentInformation]):
    dico[key] = src.getText(key)


def ExtractDataFrom(filename, arXiveTitle=None, arXiveAuthors=None, arXiveAbstract=None):
    pdf = PdfFileReader(filename)
    logger.info("ExtractDataFrom for {}".format(filename))
    rv_keywords = ""
    rv_subtitle = ""


    rv_fileMetadata = dict()

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


    """Work on page[0] for subtitle """
    page = pdf.getPage(0)

    # del page['/Resources']['/Font']

    # search for title

    text = MyExtractText(page)  # page.extract_text(orientations=0)  # we remove any non-horizontal text

    if arXiveTitle is not None:  # we uses true title to reduce subtitle size (we do not need to assume it from pdf file
        # TODO PRA report this case title from arXive has an extra uppercase

        rv_b, rv_1, rv_2 = Myfind(text, arXiveTitle, caseSensitive=False)

        if rv_b:  # index == -1:
            text = text[rv_2:]   # remove title from text buffer (and possible page header)
        else:
            logger.warning("file {} dont start with complete title".format(filename))  # probably title have been cut in text (with an '\n') TODO PRA create another function


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
                    logger.warning("file corrected with arXive DB")

    indexKW = text.find("Keywords", iEnd)
    if indexKW == -1:
        indexKW = text.find("KEYWORDS")

    if indexKW > 0:
        indexKW += len("Keywords")

    indexKW_end = -1
    if len(pdf.outline) != 0:
        firstTitle = pdf.outline[0]['/Title']  # TODO PRA on suppose ici que outline[0] est le titre de l'article
        # mais cela peut être autre chose par exemple une partie 1 (voir par exemple ./Files/1001.2813.pdf)
        # dans ce cas (a verifier !) [0] est la partie 1 et [1] contient la "vraie" arbo
        indexKW_end = text.find(firstTitle, indexKW)  # start of 1er BookMark gives an end for keywords

    if indexKW_end == -1:
        indexKW_end = text.find('.\n', indexKW)  # assume keywords end with .\n

    if indexKW_end == -1:
        indexKW_end = text.find('. \n', indexKW)  # assume keywords end with . \n

    if indexKW_end == -1:
        indexKW_end = text.find('.  \n', indexKW)  # assume keywords end with .  \n

    if indexKW != -1:
        rv_keywords = text[indexKW:indexKW_end + 1].strip(' \n')  # TODO PRA max doit etre plus grand que min, et ce n'est pas toujours vrai :(
        logger.debug("rv_keywords {}".format(rv_keywords))
    else:
        logger.warning("file {} No ending mark for keywords in".format(filename))


    """Work on REFERENCE """
    rv_reference_ctrl_set = set()
    rv_reference_list = list()

    "extract text starting with from last Bookmark (if present else skip page 0 )"

    finalText = ""

    myrange = [i for i in range(pdf.numPages) if i >= min(1, pdf.numPages - 1)]
    for pageNumber in myrange:
        text = MyExtractText(pdf.getPage(pageNumber))  # .extract_text(orientations=0)
        finalText = finalText + text

    indexRef = finalText.find("References")

    if indexRef == -1:
        indexRef = finalText.find("REFERENCES")

    if indexRef != -1:
        indexRef += len("REFERENCES")

    if indexRef == -1:
        rv_b, rv_1, iEnd = Myfind(finalText, "REFERENCES", caseSensitive=False)  #probably we have Re\nferences in text !
        if rv_b:
            indexRef = iEnd
        else:
            logger.error("No reference in text")

    if indexRef != -1:
        text = finalText[indexRef:]
        # testé avec https://regex101.com/ !!!
        # we assume ref like \n [x] .....
        # en une colonne : '\n\[\d+\]' en 2 : '(\n|\. +)\[\d+\]'

        tempoList = re.split(r'(\n|\. +)\\[\d+\\]', text)
        if len(tempoList) == 1: # previous split failed assume \n x. ....
            tempoList = re.split(r'\n\d+\.', text)

        del tempoList[0]  # If there are capturing groups in the separator and it matches at the start of the string, the result will start with an empty string. The same holds for the end of the string:

        rv_reference_list = tempoList  # .add(finalText[indexRef:])

    logger.debug("rv_reference_list {}".format(rv_reference_list))

    # for debug purpose, extract REFERENCES from internal PDF goto REFERENCES (in annots)
    # unfortunately only available with LaTEX
    for page in range(pdf.numPages):
        pdfPage = pdf.getPage(page)

        if '/Annots' in pdfPage:
            for item in pdfPage['/Annots']:
                obj = item.get_object()
                if '/Dest' in obj:  # obj['/Dest']:
                    res = str(obj['/Dest'])
                    if len(res) != 0 and  res.startswith("cite."):
                        rv_reference_ctrl_set.add(res[5:])

    if len(rv_reference_ctrl_set) != 0:
        logger.debug("rv_reference_ctrl_set {}".format(rv_reference_ctrl_set))

    if len(rv_reference_ctrl_set) != 0 and len(rv_reference_ctrl_set) != len(rv_reference_list):
        logger.warning("Error on REFERENCES size, links differes from extraction in file {}".format(filename))

    # add extra values (computed) to MetaData could also add url (mail)
    rv_fileMetadata["_gotoRef"] = len(rv_reference_ctrl_set)
    rv_fileMetadata["_outlineSize"] = len(pdf.outline)

    return rv_fileMetadata, rv_subtitle, rv_keywords, rv_reference_list


# file = "1101.0309.pdf"  # "2209.14299.pdf"
# file = "./Files/1001.2277.pdf"
# file = "./Files/1001.4251.pdf"
file = "./Files/1001.1653.pdf"
if __name__ == '__main__':
    print(ExtractDataFrom(file, "Tag Clouds for Displaying Semantics: The Case of Filmscripts"))
