# from setuptools import logging
import urllib
from datetime import datetime, timedelta

import settings  # TODO PRA si je le commente cela ne donne pas le meme resultat existe un setuptools logging
import sqlite3
import time
from urllib.request import urlopen

# /!\ Ne fonctionne que si results_per_iteration = 25
from bs4 import BeautifulSoup

import logging


# import logging
# import logging


# to add dict in set, we need to freeze them
# def freeze(d):
#     if isinstance(d, dict):
#         return frozenset((key, freeze(value)) for key, value in d.items())
#     elif isinstance(d, list):
#         return tuple(freeze(value) for value in d)
#     return d

def freeze(d):  # todo PRA pas propre et peu utile
    return d.__str__()


def extractIdAndLinks(bs: BeautifulSoup):
    """ Extrait l'id, son link principal, et les exports disponibles dans une requete arXive

    :param bs: BeautifulSoup

    extrait les champs de
    <p class="list-title is-inline-block">
    <a href="https://arxiv.org/abs/1012.2713">arXiv:1012.2713</a>
    <span> [<a href="https://arxiv.org/pdf/1012.2713">pdf</a>] </span>

    en typiquement
    arXiv:1006.3035 https://arxiv.org/abs/1006.3035
        {'pdf': 'https://arxiv.org/pdf/1006.3035', 'other': 'https://arxiv.org/format/1006.3035'}

    :return: a tuple str,str, dict()

    """
    myLinks = {}
    tag_a = bs.find('a')
    myId = tag_a.contents[0]
    myIdLink = tag_a.get('href')
    tag_span = bs.find('span')  # .contents[0]

    for aa in tag_span.find_all("a"):
        myLinks[aa.getText(strip=True)] = aa.get('href')

    return myId, myIdLink, myLinks


def extractArXiveTags(bs: BeautifulSoup):
    """
    :param bs: BeautifulSoup
    :return: a list of Tags arXive categories

    <div class="tags is-inline-block">
    <span class="tag is-small is-link tooltip is-tooltip-top">cs.CL</span>
    <span class="tag is-small search-hit tooltip is-tooltip-top">cs.AI</span>
    <span class="tag is-small is-grey tooltip is-tooltip-top">cs.IR</span>
    </div>
    """
    result = list()
    for tag in bs.find_all("span"):
        result.append(tag.getText())
    return result


def extractDate(stringData: str):
    """
    :param stringData extra data string
    :return: date
    Typical set is ' ... Submitted 31 December, 2010; '
    """
    ii = stringData.find("Submitted ")
    if ii == -1:
        return ""
    else:
        ii = ii + len("Submitted ")
        iend = stringData.find(';', ii)
        iend2 = stringData.find('\n', ii)

        if iend2 < iend:
            iend = iend2
        return stringData[ii:iend]


logger = logging.getLogger(__name__)
# logger.setLevel('WARNING')



# base_url = "http://export.arxiv.org/api/query?"
base_url = "https://arxiv.org/search/advanced"

# Search parameters
start = 0  # start at the first result
total_results = 10000  # le max exploitable actuellement par le moteur de recherche
results_per_iteration = 200  # 5 results at a time
wait_time = 3  # number of seconds to wait beetween calls

startDirectory: str = "./../"
pdfRepository = "./Files/"  # directory must exist... TODO ?
dataBase = 'myArXive.db'


# logger.info('INFO !')

con = sqlite3.connect(startDirectory + dataBase)  #: crée une connection.  # TODO PRA  quitter proprement si pas de BDD ou si déjà bloquée
cur = con.cursor()

try:  # TODO PRA faire plus propre en vidage de la base ?
    cur.execute('''PRAGMA foreign_keys = OFF''')
    cur.execute('''DROP TABLE arXive''')
    cur.execute('''PRAGMA foreign_keys = ON''')
    records = cur.fetchall()
    logger.debug(records)
except:
    pass


cur.execute('''CREATE TABLE IF NOT EXISTS arXive ( 
  entry_id  TEXT PRIMARY KEY,
  link  TEXT,
  dlLinks  TEXT,
  tags TEXT,
  title TEXT,
  authors  TEXT,
  summary TEXT,
  pdate  TEXT,
  extraData  TEXT)''')

# toute requette arXive est limitee a 10000 ^^

for year in range(2022, 1991, -1):  # 1991 permière année de publication arXive

    datefrom = [ str(year)+"-01-1",str(year)+"-07-01"]  # la date de fin n'est pas precise, mais la date de début si ! bug 28 fev ?
    dateto = [ str(year)+"-07-01",str(year+1)+"-1-1"   ]
    for index in range(len(dateto)):
        search_query = "?advanced=&terms-0-operator=AND&terms-0-term=cs.AI" \
                       "&terms-0-field=all&classification-physics_archives=all" \
                       "&classification-include_cross_list=include&date-year=&date-filter_by=date_range" \
                       "&date-from_date={0}&date-to_date={1}&date-date_type=submitted_date" \
                       "&abstracts=show&size={2}&order=-announced_date_first".format(datefrom[index], dateto[index],
                                                                                     results_per_iteration)

        logger.info(f'Searching arXiv for {base_url+search_query}')

        last_request_dt = datetime.min # .now()
        required = timedelta(seconds=wait_time)
        for i in range(start, total_results, results_per_iteration):
            logger.info("Results {} - {}".format(i + 1, i + results_per_iteration))
            # logger.info("# pouet " + base_url + search_query + "&start=" + str(i))

            since_last_request = datetime.now() - last_request_dt
            if since_last_request < required:
                to_sleep = (required - since_last_request).total_seconds()
                logger.info("Sleeping for %f seconds before urlopen", to_sleep)
                time.sleep(to_sleep)

            last_request_dt = datetime.now()
            data = []
            try:
                with urlopen(base_url + search_query + "&start=" + str(i)) as url:

                    since_last_request = datetime.now() - last_request_dt
                    if since_last_request < required:
                        to_sleep = (required - since_last_request).total_seconds()
                        logger.info("Sleeping for %f seconds before url.read()", to_sleep)
                        time.sleep(to_sleep)

                    last_request_dt = datetime.now()
                    response = url.read()

                    # parse the response using feedparser
                    #  feed = feedparser.parse(response)
                    # print("MMMMM: ",feedparser.parse(response))
                    # feed['feed']['summary']
                    soup = BeautifulSoup(response, "html.parser")

                    # print("@@",feed['feed']['summary'])
                    # print("########",soup.contents)

                    res = soup.find_all('li', {'class': 'arxiv-result'})

                    if len(res) == 0:
                        logger.info("No result for period")


                    for element in res:  # ,{'class' : 'arxiv-result'}):
                        currentList = list()
                        # print("####",element.__str__())
                        # res= BeautifulSoup('<pre>%s</pre>' % element.getText())
                        # print("##",element.__str__())#.text) # .getText())
                        currentSoup = BeautifulSoup(element.__str__(), "html.parser")
                        element = currentSoup.find('p')
                        ide, idLink, Links = extractIdAndLinks(element)
                        currentList.append(ide)
                        currentList.append(idLink)
                        currentList.append(freeze(Links))

                        # print("Id=", ide, idLink, Links)

                        element = currentSoup.find('div', {'class': 'tags'})
                        # print("Tags: ", extractArXiveTags(element))

                        currentList.append(freeze(extractArXiveTags(element)))

                        element = currentSoup.find_all('p', {'class': 'title'})
                        # print("Title=", BeautifulSoup(element.__str__(), "html.parser").find('p').getText().strip())

                        currentList.append(BeautifulSoup(element.__str__(), "html.parser").find('p').getText().strip())

                        element = currentSoup.find_all('p', {'class': 'authors'})
                        # print("authors=", BeautifulSoup(element.__str__(), "html.parser").find('a').getText().strip())
                        # print("authors=", element.__str__())
                        authorsList = list()
                        for a in BeautifulSoup(element.__str__(), "html.parser").find_all('a'):
                            # print("authors2=",BeautifulSoup(a.__str__(), "html.parser").find('a').getText)
                            # print("authors", a.getText())
                            authorsList.append(a.getText())

                        currentList.append(freeze(authorsList))

                        element = currentSoup.find('span', {'class': 'abstract-full'})

                        # print("Abstract-full=", element.contents[0])

                        currentList.append(element.contents[0].strip())

                        elem = currentSoup.findAll('p', {'class': 'is-size-7'})

                        # for ele in elem:
                        #     print("*",ele.__str__())

                        arXiveExtraData = ""
                        for el in elem:
                            arXiveExtraData = arXiveExtraData + (el.getText())

                        # print("date:", extractDate(arXiveExtraData))

                        currentList.append(extractDate(arXiveExtraData))
                        currentList.append(arXiveExtraData)

                        data.append(currentList)

                        logger.debug(currentList)
                        cur.execute('''insert into arXive ( entry_id,link,dlLinks,tags,title,authors,summary,pdate,extraData) values
                     (?, ?, ?, ?, ?, ?, ?, ?, ?)''', currentList)
                        con.commit()
                        records = cur.fetchall()
                        logger.debug("commit of current list: "+str(records))

                    if len(res) < results_per_iteration:
                        break # no needs to continue "&start="  loop
            finally:
                pass
            # except urllib.error.URLError as e:
            #     logger.error(e.reason)
            # now = datetime.now()
            #
            # required = timedelta(seconds=wait_time)
            # since_last_request = datetime.now() - last_request_dt
            # if since_last_request < required:
            #     to_sleep = (required - since_last_request).total_seconds()
            #     logger.info("Sleeping for %f seconds", to_sleep)
            #     time.sleep(to_sleep)


cur.close()
con.commit()  # committe les transactions.
con.close()  # ferme la connection.
