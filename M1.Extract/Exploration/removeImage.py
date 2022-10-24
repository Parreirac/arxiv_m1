from pathlib import Path
from typing import Union, Literal, List

from PyPDF2 import PdfWriter, PdfReader
from PyPDF2 import PdfReader
path = "./../../Files/"
myFile = "1008.1333.pdf"  #_repaired-Copier.pdf"
reader = PdfReader(path+myFile)

page = reader.pages[1]
count = 0

for image_file_object in page.images:
    with open(path + str(count) + image_file_object.name, "wb") as fp:
        print("ouverture de ",path + str(count) + image_file_object.name)
        fp.write(image_file_object.data)
        count += 1
print("--")
# print(page.extractText())
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
# page.images.clear()
# # print("--")
# print(page.extractText())
# print("--")

# print("--")
# print(page.extractText())
# print("~~~~~~~~~~~~~~~~~~~~~~")

# def stamp(
#     content_pdf: Path,
#     stamp_pdf: Path,
#     pdf_result: Path,
#     page_indices: Union[Literal["ALL"], List[int]] = "ALL",
# ):
#     reader = PdfReader(stamp_pdf)



# image_page = reader.pages[1]

# if len(image_page) > 0:
#     obj = image_page[0].getObject()
# reader.cacheIndirectObject()
print("l=",len(reader.getPage(1).images))
writer = PdfWriter()

writer.cloneDocumentFromReader(reader)
writer.removeImages()
# reader = PdfReader(content_pdf)
# if page_indices == "ALL":
page_indices = list(range(0, len(reader.pages)))
# for index in page_indices:
#     content_page = reader.pages[index]
#     # mediabox = content_page.mediabox
#     # content_page.merge_page(image_page)
#     # content_page.mediabox = mediabox
#     writer.add_page(content_page)

with open(path+ "pdf_result.pdf", "wb") as fp:
    writer.write(fp)