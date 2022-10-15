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

# parts = []
# def visitor_body(text, cm, tm, fontDict, fontSize):
#     print("body ", cm, tm, fontDict, fontSize, "\n", text)
#     parts.append(text)
#
# def printObj(idnum: int, pdf):
#     iobj = IndirectObject(idnum=idnum, generation=0, pdf=pdf)
#     obj = iobj.get_object()
#     print(idnum, ":", obj)
#     return


"""
sur 1101.0309 il semble qu'il y a un pb sur les fonts (qui donne l'espacement)
d'ou un bug sur les mots qui sont mals découpés
"""


def ExtractDataFrom(filename, arXiveTitle=None, arXiveAuthors=None, arXiveAbstract=None):
    pdf = PdfFileReader(filename)
    logger.info("ExtractDataFrom for {}".format(filename))
    rv_keywords = ""
    rv_subtitle = ""

    # rv_producer = pdf.documentInfo.producer

    def addValue(dico: dict, key: str, src: Optional[DocumentInformation]):
        dico[key] = src.getText(key)

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

    rv_reference_ctrl_set = set()
    rv_reference_list = list()

    # for debug purpose, extract REFERENCES from internal goto (in annots)
    for page in range(pdf.numPages):
        pdfPage = pdf.getPage(page)

        if '/Annots' in pdfPage:
            for item in pdfPage['/Annots']:
                obj = item.get_object()
                if '/Dest' in obj:  # obj['/Dest']:
                    res = obj['/Dest']
                    if res.startswith("cite."):
                        rv_reference_ctrl_set.add(res[5:])

    logger.debug("rv_reference_ctrl_set {}".format(rv_reference_ctrl_set))

    """Work on page[0] for subtitle """
    page = pdf.getPage(0)  # pdf.pages[0]
    # del page['/Resources']['/Font']

    # search for title

    text = MyExtractText(page)  # page.extract_text(orientations=0)  # we remove any non-horizontal text

    if arXiveTitle is not None:  # we uses true title to reduce subtitle size (we do not need to assume it from pdf file
        # TODO PRA report this case title from arXive has an extra uppercase

        rv_b, rv_1, rv_2 = Myfind(text, arXiveTitle, caseSensitive=False)

        # index = text.lower().find(arXiveTitle.lower())

        if rv_b:  # index == -1:
            text = text[rv_2:]   # remove title from text buffer
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
        logger.debug("file {} dont dont have abstract, try with arXiveAbstract".format(filename))
        if arXiveAbstract is None:
            logger.warning("file {} dont dont have abstract".format(filename))
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

    firstTitle = ""
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

    # rv_keywords = rv_keywords

    """Work on REFERENCE """

    "extract text starting with from last Bookmark (if present else skip page 0 )"

    finalText = ""

    # startPage = pdf.pages[min(1, len(pdf.pages))]
    # if len(pdf.outline) != 0:
    #     iv = len(pdf.outline)
    #     Last = pdf.outline[len(pdf.outline) - 1]  # ['/Title']
    #     startPage = Last['/Page']

    myrange = [i for i in range(pdf.numPages) if i >= min(1, pdf.numPages - 1)]
    for pageNumber in myrange:
        text = MyExtractText(pdf.getPage(pageNumber))  # .extract_text(orientations=0)
        finalText = finalText + text

    indexRef = finalText.find("References")

    if indexRef == -1:
        indexRef = finalText.find("REFERENCES")

    if False and indexRef != -1:  # ne fonctionne pas si la biblio n'est pas de la forme [i]
        indexRef = finalText.find('[', indexRef)  # remove text before first [

    if indexRef == -1:
        logger.error("No reference in text")
    else:
        indexRef += len("REFERENCES")
        text = finalText[indexRef:]
        # tempoList = text.split('[')
        # TODO PRA premier element en trop ('') le retrait actuel est laid
        # tempoList = re.split('\[+\d+\]+', text)
      #  tempoList = re.split('(\[|\n)\d(\]|(\. ))',text)
      #   if re.match('\n\d\. ',text):
      #       tempoList = re.split('(\n\d\. )', text)
      #   else:
      #       tempoList = re.split('(\[\d\])', text)

        tempoList = re.findall()
        # tempoList = re.split('(\[\d\])|(\n\d\. )', text)

        # del tempoList[0] If there are capturing groups in the separator and it matches at the start of the string, the result will start with an empty string. The same holds for the end of the string:

        rv_reference_list = tempoList  # .add(finalText[indexRef:])

    logger.debug("rv_reference_list {}".format(rv_reference_list))

    if len(rv_reference_ctrl_set) != 0 and len(rv_reference_ctrl_set) != len(rv_reference_list):
        logger.warning("Error on REFERENCES size, links differes from extraction in file {}".format(filename))

    # add extra values (computed) to MetaData on pourrait ajouter les url
    rv_fileMetadata["_gotoRef"] = len(rv_reference_ctrl_set)
    rv_fileMetadata["_outlineSize"] = len(pdf.outline)

    return rv_fileMetadata, rv_subtitle, rv_keywords, rv_reference_list


# def visitor_after(op, args, cm, tm):
#     print("after: ", op)


""" Page a : \
'/Rotate'
'/Parent'
'/Resources' dont '/ExtGState':  et '/Font':
'/Contents'
"""

# file = "1101.0309.pdf"  # "2209.14299.pdf"
# file = "./Files/1001.2277.pdf"
# file = "./Files/1001.4251.pdf"
file = "./Files/0905.3830.pdf"
if __name__ == '__main__':
    print(ExtractDataFrom(file, "Tag Clouds for Displaying Semantics: The Case of Filmscripts"))
