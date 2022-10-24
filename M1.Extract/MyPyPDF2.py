import logging

import PyPDF2
from PyPDF2.errors import PdfReadWarning
from PyPDF2.generic import RectangleObject
from typing import List

"""
overload overload PyPDF2.extract_text to have 2 basics filter
- read horizontal text only
- remove footer and header on each page => failed
- remove artifacts (eg footer/header) 

"""

# from PyPDF2 import PageObject

parts = []
" todo pra adapter les valeurs ? au depart 50 & 720 sur ./Files/1001.4405.pdf ne fonctionne pas"

footer = 50.  # value used to remove footer default value
header = 720.  # value used to remove header
hideText = False
opb = b' '
opa = b' '

logger = logging.getLogger(__name__)
import logging

logger2 = logging.getLogger("PyPDF2")
logger2.setLevel(logging.INFO)


# cela permettrait de virer (si c'est ca) explicitement les bas de page
# sur 1001.1653 on ne peut couper parfaitement :(
# actuellement quelques numero de page sont dans les references


def my_mult(m: List[float], n: List[float]) -> List[float]:  # cp from _page.py
    return [
        m[0] * n[0] + m[1] * n[2],
        m[0] * n[1] + m[1] * n[3],
        m[2] * n[0] + m[3] * n[2],
        m[2] * n[1] + m[3] * n[3],
        m[4] * n[0] + m[5] * n[2] + n[4],
        m[4] * n[1] + m[5] * n[3] + n[5],
    ]


def visitor_body(text, cm, tm, _fontDict, _fontSize):
    # print("body ", cm, tm, fontDict, fontSize, "\n", text)
    global footer, header, hideText
    if not isinstance(cm, list):
        logger.error("wrong type in visitor_body 1")
    if len(cm) < 6:
        logger.error("wrong type in visitor_body 2")
    if not isinstance(tm, list):
        logger.error("wrong type in visitor_body 3")
    if len(tm) < 6:
        logger.error("wrong type in visitor_body 4")

    _y_tm = tm[5]
    y_cm = cm[5]

    m = my_mult(tm, cm)  # , cm)

    if len(text) > 0:
        if y_cm != 0.0:  # and (y_cm != 0 and footer < y_cm < header)
            pass
    #
    # if len(text) > 1 :
    #     print(y_tm, y_cm,m[5],footer,header, text)

    if text.find("AP2PC") != -1:  # startswith("1") :
        pass  # print(y_tm, y_cm, footer, header, text)

    # if text.startswith("NSF grant No"):
    #     print(y_tm, y_cm, footer, header, text)

    # if y_tm < 100 and text == "1" or  text == "2" or  text == "3" or text == "4" or  text == "5" or  text == "6" or text == "7":
    #     print(y_tm, y_cm, footer, header, text)
    # if y_tm < 100 and text == "8" or  text == "9" or  text == "10":
    #     print(y_tm, y_cm, footer, header, text)
    # if y_tm < 100 and text == "11" or  text == "12" or  text == "13" or text == "14" or  text == "15" or  text == "16" or text == "17":
    #     print(y_tm, y_cm, footer, header, text)
    # if y_tm < 100 and text == "18" or  text == "19" or  text == "20":
    #     print(y_tm, y_cm, footer, header, text)

    # if text=="21": # "PDF 32000-1:2008":
    #     print(y_tm, y_cm, footer, header,hideText, text,opb,opa)

    if footer < m[5] < header and not hideText:
        # if y_cm == 0.0 or (y_cm != 0.0 and footer < y_cm):
        parts.append(text)

    # if y_cm == 0.0:
    #     parts.append(text)


def visitor_before(op, _args, _cm, _tm):
    global opb, hideText

    # if (not args is None) and isinstance(args, List):
    # print(op,'*',_args)
    # if len(args) > 0:
    #     if isinstance(args[0],List):
    # l2 =(args[0][::2])
    # l3 = [x.decode('utf-8') for x in l2]
    # r= ""
    # for l in args[0]:
    #     if type(l)==type(bytes):
    #         r = r + bytes(l).decode('utf-16')
    # print("###",(args[0]),"###", l2)
    # and isinstance(args[0],str): # is == "/Artifact":

    # print(args)
    # hideText = True
    # opb = op
    if False and op == "BDC" or op == "BMC":  # or op == "BMC":
        logger.warning(">NO ERROR just hinding TEXT<")
        hideText = True
    # print("before :",op)
    pass


def visitor_after(op, _args, _cm, _tm):
    global opa, hideText
    opa = op
    if False and hideText and op == "EMC":
        logger.error(">NO ERROR just hinding TEXT END<")
        hideText = False

    # print("after :", op)
    pass


def MyExtractTxtFromPdfPage(page: PyPDF2.PageObject, clean=True) -> str:
    global header, footer, parts
    parts.clear()
    rv: RectangleObject = page.trimbox
    h = rv.top - rv.bottom
    # print("h :",h)
    # "./Files/1003.0034.pdf" donne 70. 729.
    header = h  # - 10 #729 #0.690495*float(h) + 163.3 +.003 # valeur calculee .6905 # seuil pour 1001.2813
    footer = 40.  # 89.4002000000001# float(rv.bottom) + .083 * float(h)

    try:
        page.extract_text(orientations=0, visitor_text=visitor_body, visitor_operand_before=visitor_before, visitor_operand_after=visitor_after)

    except TypeError as e:
        logging.error("erreur {}".format(repr(e)))  # ,exc_info=True)
        # logging.exception(e)
    except AttributeError as e:
        logging.error("erreur AttributeError{}".format(repr(e)))
        # logging.exception(e)
    except PdfReadWarning as e:  # toto pra a sortir d'un cran ?
        logging.warning("erreur : {}".format(repr(e)))
        # logging.exception(e)
    except Exception as e:
        logging.error("erreur {}".format(repr(e)))
        # logging.exception(e)
    finally:
        pass

    if clean:  # handle lines
        for i in range(len(parts)):
            parts[i] = MyTxtCleaner(parts[i], hyphenation=True, ligature=True)

    if clean:  # handle jonction
        for i in range(len(parts) - 1):
            line = parts[i]
            if len(line) == 0:
                continue
            lastChar = line[-1]
            if False and lastChar == '-':
                parts[i] = ''
                parts[i + 1] = line[:-1] + parts[i + 1]  # pour tester à la prochaine boucle la fin de la ligne
    #
    # res = ""
    # for i in parts:
    #     if len(i) > 0:
    #         res=res+'\n'+i
    # return res
    return "".join(parts)# TODO PRA ? peut etre le rendre optionnel pour faciliter les traitements


# pour virer la ligature (ligation)
# les tirets de césure (hyphenation) les sauts de ligne sans ., ou ; ou : avant
def MyTxtCleaner(src: str, hyphenation=True, ligature=True) -> str:
    txt = src
    i1 = len(txt)
    if ligature:  # TODO PRA faire les autres cas !
        txt = txt.replace('ﬁ', 'fi')
        txt = txt.replace('ﬂ', 'fl')
    _i2 = len(txt) - i1

    i10 = len(txt)
    if hyphenation:
        txt = txt.replace(r'-\n', '')
    i20 = len(txt) - i10

    if i20 > 0:
        pass
    # txt = txt.replace(r' *\n *',' ')

    return txt
