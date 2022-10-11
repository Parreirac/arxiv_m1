from pdfminer.high_level import extract_text
from io import StringIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

file = "1101.0309.pdf"
#text = extract_text(file)
#print(text)

output_string = StringIO()
with open(file, 'rb') as fin:  # normal,exact -> trop long mais mieux ,loose -> pire
    extract_text_to_fp(fin, output_string, laparams=LAParams(),page_numbers = [0], layoutmode ="exact", output_type='html', codec=None, debug = True)

    print(output_string.getvalue())