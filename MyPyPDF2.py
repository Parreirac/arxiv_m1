import PyPDF2


"""
overload overload PyPDF2.extract_text to have 2 basics filter
- read horizontal text only
- remove footer and header on each page
"""


# from PyPDF2 import PageObject

parts = []

def visitor_body(text, cm, tm, fontDict, fontSize):
    # print("body ", cm, tm, fontDict, fontSize, "\n", text)
    y = tm[5]
    if y > 76  and y < 820:  # todo pra adapter les valeurs ? au depart 50 & 720 sur ./Files/1001.4405.pdf ne fonctionne pas
        parts.append(text)

def visitor_before(op, args, cm, tm):
    # if op == b'TJ':
    pass
# print("before: ", op)


def MyExtractText(page: PyPDF2.PageObject ) -> str:
    parts.clear()
    page.extract_text(orientations = 0,visitor_text=visitor_body)
    return "".join(parts)

# print("###")
# text = page.extract_text(orientations = 0,visitor_operand_before = visitor_before,visitor_operand_after = visitor_after,
#     visitor_text=visitor_body)
# print("###")
# text_body = "".join(parts)
