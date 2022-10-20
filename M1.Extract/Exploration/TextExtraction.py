import pdfminer




from io import StringIO

from Scripts.dumppdf import dumppdf, dumpoutline
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser



myFile = "1101.0309.pdf"
output_string = StringIO()

with open(myFile, 'rb') as in_file:
    parser = PDFParser(in_file)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    i = 0
    for page in PDFPage.create_pages(doc):
        i+=1
        if (i ==10):
            interpreter.process_page(page)


print(output_string.getvalue())

"""
dumppdf(output_string,myFile,dumpall =T rue
    outfp: TextIO,
    fname: str,
    objids: Iterable[int],
    pagenos: Container[int],
    password: str = "",
    dumpall: bool = False,
    codec: Optional[str] = None,
    extractdir: Optional[str] = None,
    show_fallback_xref: bool = False,
)"""
# dumppdf
#test =dumppdf(output_string,myFile,objids = None, pagenos=None, dumpall =True)
#test =dumppdf(output_string,myFile,objids = None, pagenos=None)

#dumpoutline(output_string,myFile,objids = None, pagenos=None)#, dumpall =True)

#print(output_string.getvalue())