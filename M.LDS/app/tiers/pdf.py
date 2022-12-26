from PyPDF2 import PdfFileReader
import logging


logger = logging.getLogger(__name__)
# https://pypi.org/project/PyPDF2/
def getWatermark(filename):
    pdf = PdfFileReader(filename)  #, strict=False ??? test file's existence by caller todo with ????
    logger.info("getWatermark for {}".format(filename))
    page = pdf.getPage(0)  # T

    text =page.extract_text(90)

    return text

def getMetadata(filename):
    document = PdfFileReader(filename) #   open(myFile, 'rb'))
    metadata = document.getDocumentInfo()
    print(metadata)

    print(document.getNumPages())

    print(document.getFields())

    return metadata

#    Le type d’affichage avec getPageLayout()
#    Le mode d’affichage avec getPageMode()