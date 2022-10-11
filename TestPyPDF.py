# from PyPDF2 import PdfReader
import PyPDF2
from PyPDF2.generic import IndirectObject

def printObj(idnum: int, pdf):
    iobj = IndirectObject(idnum = idnum, generation =0 , pdf= pdf)
    obj = iobj.get_object()
    print(idnum,":",obj)
    return

file = "1101.0309.pdf"
pdf = PyPDF2.PdfFileReader(file)

urls = []
biblio = set()

for page in [0]:  # range(pdf.numPages):
    pdfPage = pdf.getPage(page)

    print("page ",page,pdfPage)

    """ Page a : \
    '/Rotate'
    '/Parent'
    '/Resources' dont '/ExtGState':  et '/Font':
    '/Contents'
    """
    # for key,value  in pdfPage['/Resources'].items():
    #     print(key,value)
    #     print("#",value.get_object().__repr__())
    #

    # print ("'/Contents'",pdfPage['/Contents'])

    #print("'/Resources'", pdfPage['/Resources']['/ExtGState'])
    if True and '/Annots' in pdfPage:
        for item in pdfPage['/Annots']:
            # urls.append(item['/A']['/URI'])
            # print(item,type(item))
            obj = item.get_object()
            print(obj.__repr__())
            if '/A' in obj : #  obj['/A']['/URI']:
                urls.append(obj['/A']['/URI'])

            if '/Dest' in obj:  #  obj['/Dest']:
                res = obj['/Dest']
                # print("&&", obj['/Dest'])
                if True and res.startswith("cite."):
                    biblio.add(res)

    if True and '/AA' in pdfPage:
        for item in pdfPage['/AA']:
            # urls.append(item['/A']['/URI'])
            # print(item,type(item))
            obj = item.get_object()
            print(obj.__repr__())
            if '/A' in obj : #  obj['/A']['/URI']:
                urls.append(obj['/A']['/URI'])

            if '/Dest' in obj:  #  obj['/Dest']:
                res = obj['/Dest']
                # print("&&", obj['/Dest'])
                if True and res.startswith("cite."):
                    biblio.add(res)





print("URL du document", urls) # ne donne pas les mailTo, donc pas tous les liens
print("liens internes (biblio) ",biblio) # ne donne pas necessairement l'intégralité de la biblio

print("#####")
pdf.resolved_objects

for (i,j),v in pdf.resolved_objects.items():
    print(v,type(v))

# for (i,j),v in pdf.resolved_objects.items():
#     if v['/Type'] == '/Catalog':
#         # content = v['/OpenAction']
#         # print("/OA:",content, type(content[0]),type(content[1]))
#         # print(content[0].get_object())
#         print(v)
printObj(1, pdf)
printObj(2, pdf)
printObj(3, pdf)
printObj(4, pdf)
printObj(11, pdf)

printObj(4, pdf)
printObj(3, pdf)
printObj(36, pdf)
printObj(5, pdf)
printObj(7, pdf)

printObj(8, pdf)
printObj(25, pdf)
printObj(27, pdf)
printObj(29,pdf)
printObj(30,pdf)
printObj(31, pdf)

printObj(5, pdf)

# printObj(5,pdf)
# printObj(36,pdf)
# printObj(3,pdf)
# printObj(7,pdf)
# reader = PdfReader(file)
# number_of_pages = len(reader.pages)
# page = reader.pages[9]
# text = page.extract_text()
# print(text)