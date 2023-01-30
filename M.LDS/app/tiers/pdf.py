""" Pdf handling """
import logging

from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


def get_watermark(filename):
    """vertically reads the watermark on the first page """
    pdf = PdfReader(filename)  # , strict=False ??? test file's existence by caller todo with ????
    logger.info("getWatermark for %s", filename)
    page = pdf.pages[0]
    text = page.extract_text(90)

    return text


def get_text(filename):
    """Get full pdf text"""
    pdf = PdfReader(filename)  # , strict=False ??? test file's existence by caller todo with ????
    logger.info("getText for %s", filename)
    text = ""
    for _i, page in enumerate(pdf.pages):
        text = text + page.extract_text()

    return text


def get_metadata(filename):
    """Get pdf metadata"""
    document = PdfReader(filename)  # open(myFile, 'rb'))
    metadata = document.metadata
    # print(metadata)
    # print(len(document.pages))
    # print(document.get_fields())
    #    Le type d’affichage avec getPageLayout()
    #    Le mode d’affichage avec getPageMode()
    return metadata
