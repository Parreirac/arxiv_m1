"""Requests HTTP Library"""
import requests
import semanticscholar as sch
from bs4 import BeautifulSoup


def get_true_arxive_id(watermark):
    """Recent files have a watermark giving the arxive identifier \
    of the file (its version, its categories and a date)"""
    if len(watermark) == 0:
        return "", ""

    tab = watermark.split(" ")  # et dans le cas d'une classification multiple ? TODO PRA

    i = tab[0].find("arXiv:")
    if i == -1:
        return "", ""

    ide = tab[0][:]
    version = "unk"
    i = ide.find("v", 6)
    if i != -1:
        version = ide[i:]
        ide = ide[0:i]

    return ide, version  # todo garder les autres informations


def get_content_from_semanticscholar(ide):
    """Get elements from "https://api.semanticscholar.org/" + ide
    WARNING Time consuming ! and ugly (it's better to use semanticscholar api)
    You can use the API endpoint up to 100 requests per 5 minutes to test your application idea.
    To access a higher rate limit, complete the form to request authentication for your project.
    Authenticated partners have access to higher rate limits, personalized support,\
     and co-marketing opportunities."""
    url = "https://api.semanticscholar.org/" + ide

    html = requests.get(url, timeout=2).text  # . urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    # result = soup.find(class_="card-container")
    results = soup.find(id="extracted")  # "div", class_="extracted")#""card-container")
    text_extracted = results.prettify()

    # references ->
    results = soup.find(class_="citation-list__citations")
    text_references = results.prettify()

    return text_extracted, text_references


def get_article_from_semanticscholar(arxive_id):
    """get article info from semanticscholar
    :param : arxive_id
    :returns: dictionary"""
    paper = sch.paper(arxive_id, timeout=6)

    # for i,k in paper.items():
    #    print(i,"\n",k)

    # print(len(paper.get("references")))
    return paper


def handle_final_value(key, value):
    """change value as <a href=value /> if key = 'url'"""
    res = str(value)
    if key.lower() == 'url':
        res = "<a href=" + res + ">" + res + "</a>"
    return res


def tranform_dict_to_html(dictionary, b_o="", b_f="", skip=None):
    """First version of conversion of a dict to be printed in html"""
    res = []
    for key, value in dictionary.items():
        if skip is not None and key in skip:
            continue
        if isinstance(value, list):

            res.append(b_o + str(key) + b_f)
            # if len(value)>1:
            #    res.append("<details open>")
            # res.append("<summary>" + str(key) + "</summary>")

            # res.append("<h2>" + str(key) + "</h2>")
            # res.append("<ul>")
            # res.append("<table>")
            # res.append("<tr>")
            for text in value:
                # res.append("<tr>")
                if isinstance(text, dict):
                    res.append(tranform_dict_to_html(text, "<h2>", "</h2>"))
                # elif type(text) is list:
                #    pass
                else:
                    res.append(b_o + handle_final_value(key, text) + b_f)
                # res.append("</tr>")

            # res.append("</tr>")
            # res.append("</ul>")
            # res.append("</tr>")
            # res.append("</table>")
            # if len(value) > 1:
            #    res.append("</details>")

        elif isinstance(value, dict):
            res.append(tranform_dict_to_html(value, b_o, b_f))
        else:
            res.append(b_o + str(key) + ": " + handle_final_value(key, value) + b_f)

    return "\n".join(res)
