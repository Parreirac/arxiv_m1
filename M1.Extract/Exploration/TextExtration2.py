# import pdfminer.high_level
# file = "1101.0309.pdf"
# txt = pdfminer.high_level.extract_text(file)
# print(txt)
import logging
#######
from io import BytesIO
import pprint

from pdfreader import PDFDocument, SimplePDFViewer
from pdfrw import PdfReader

file =  "./../.././Files/1008.1333.pdf"
reader = PdfReader(file)
# print(reader.keys())   #['/Size', '/Root', '/Info', '/ID']
logger = logging.getLogger()
# print(reader.values())

# pprint.pprint(reader.Info) # retourne les métadonnées du pdf


with open(file, "rb") as f:
    # stream = BytesIO(f.read())
    # doc2 = PDFDocument(stream)
    # t = doc2.root.Outlines.First['Title'] #b'1 Background'
    # print(t)
    # page_one = next(doc2.pages())
    # page_one.Contents.strings
    # print ( page_one.Contents)

    viewer = SimplePDFViewer(f)

    # for canvas in viewer:
    #     page_images = canvas.images
    #     page_forms = canvas.forms
    #     page_text = canvas.text_content
    #     page_inline_images = canvas.inline_images
    #     page_strings = canvas.strings
    #     print("pi", page_images)
    #     print("pf", page_forms)
    #     print("pt", page_text)
    #     print("pii", page_inline_images)
    #     print("ps", page_strings)

    viewer.navigate(2)
    viewer.render()
    viewer.canvas
    page_images = viewer.canvas.images
    page_forms = viewer.canvas.forms
    page_text = viewer.canvas.text_content
    page_inline_images = viewer.canvas.inline_images
    page_strings = viewer.canvas.strings
    # print("pi", page_images)
    # print("pf", page_forms)
    # print("".join( page_text))
    # print("pii", page_inline_images)
    # print("ps", "".join(page_strings))
    # print(viewer.annotations)

    print("".join(page_strings))
    # viewer.render()
    #
    # print(viewer.canvas.text_content)
