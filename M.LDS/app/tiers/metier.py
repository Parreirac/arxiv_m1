"""Requests HTTP Library"""
import requests
from bs4 import BeautifulSoup


def get_true_arxive_id(watermark):
    """Recent files have a watermark giving the arxive identifier \
    of the file (its version, its categories and a date)"""
    if len(watermark) == 0:
        return "",""

    tab = watermark.split(" ")  # et dans le cas d'une classification multiple ? TODO PRA

    i = tab[0].find("arXiv:")
    if i == -1:
        return "",""

    ide = tab[0][:]
    version = "unk"
    i = ide.find("v", 6)
    if i != -1:
        version = ide[i:]
        ide = ide[0:i]

    return ide, version  # todo garder les autres informations


def get_content_from_semanticscholar(ide):
    """You can use the API endpoint up to 100 requests per 5 minutes to test your application idea.
    To access a higher rate limit, complete the form to request authentication for your project.
    Authenticated partners have access to higher rate limits, personalized support,\
     and co-marketing opportunities."""
    url = "https://api.semanticscholar.org/" + ide
    # data = requests.get(url).text
    # soup = BeautifulSoup(data, "html.parser")
    # tag = soup.body

    # from  https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
    html = requests.get(url,timeout=2).text  # . urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    # for script in soup(["script", "style"]):
    #    script.extract()  # rip it out

    # get text
    # text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    # lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    # chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    # text = '\n'.join(chunk for chunk in chunks if chunk)

    # print(text)

    # result = soup.find(class_="card-container")
    results = soup.find(id="extracted")  # "div", class_="extracted")#""card-container")
    text_extracted = results.prettify()
    # Print each string recursively
    # for string in tag.strings:
    #   print(string)
    # text = tag.get_text()
    # break into lines and remove leading and trailing space on each
    # lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    # chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    # text = '\n'.join(chunk for chunk in chunks if chunk)

    # references ->
    results = soup.find(class_="citation-list__citations")
    text_references = results.prettify()

    # htmltext = data.text
    # print(htmltext)
    return text_extracted, text_references
