"""
Create sqlite3 database using "https://arxiv.org/search/advanced" in order to get ArXiv Metedata
for [cs.AI] from START_YEAR to END_YEAR.
"""

import logging
import sqlite3
import time
from datetime import datetime, timedelta
from sqlite3 import Cursor
from urllib.request import urlopen

from bs4 import BeautifulSoup
import settings

BASE_URL = "https://arxiv.org/search/advanced"

# Search parameters

# start at the first result
START = 0
# le max exploitable actuellement par le moteur de recherche
TOTAL_RESULTS = 10000
# /!\ Must be in the range from arXive search UI
RESULTS_PER_ITERATION = 200
# number of seconds to wait beetween calls
WAIT_TIME = 3

# START_DIRECTORY: str = "D:/mon_depot/"

# PDF_REPOSITORY = "D:/mon_depot/Files/"  # directory must exist... TODO ?
# DATABASE = 'myArXive.db'

START_YEAR = 1991  # 1991 première année de publication arXiv
END_YEAR = 2022

logger = logging.getLogger(__name__)


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

    :return: a tuple str,str, dict()"""
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
    result = []
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

    ii = ii + len("Submitted ")
    iend = stringData.find(';', ii)
    iend2 = stringData.find('\n', ii)

    if iend2 < iend:
        iend = iend2

    return stringData[ii:iend]


#: crée une connection.  # TODO PRA  quitter proprement si pas de BDD ou si déjà bloquée
con = sqlite3.connect(settings.STARTDIRECTORY + settings.DATABASE)
cur: Cursor = con.cursor()

# noinspection SqlNoDataSourceInspection
cur.execute('CREATE TABLE IF NOT EXISTS arXive ( \n'
            '  entry_id  TEXT PRIMARY KEY,\n'
            '  link  TEXT,\n'
            '  dlLinks  TEXT,\n'
            '  tags TEXT,\n'
            '  title TEXT,\n'
            '  authors  TEXT,\n'
            '  summary TEXT,\n'
            '  pdate  TEXT,\n'
            '  extraData  TEXT)')

for year in range(END_YEAR, START_YEAR, -1):

    # la date de fin n'est pas prise, mais la date de début si ! bug 28 fev ?
    datefrom = [str(year) + "-01-1",
                str(year) + "-07-01"]
    dateto = [str(year) + "-07-01", str(year + 1) + "-1-1"]
    for index in range(len(dateto)): # TODO PRA tres laid ! c'est fixe !
        values = (datefrom[index], dateto[index], RESULTS_PER_ITERATION)
        search_query = f"?advanced=&terms-0-operator=AND&terms-0-term=cs.AI" \
                       "&terms-0-field=all&classification-physics_archives=all" \
                       "&classification-include_cross_list=include&date-year=" \
                       "&date-filter_by=date_range&date-from_date={values[0]}&date-to_date" \
                       "={values[1]}&date-date_type=submitted_date&abstracts=show&" \
                       "size={values[2]}&order=-announced_date_first"

        logger.info('Searching arXiv for %s', BASE_URL + search_query)

        last_request_dt = datetime.min  # .now()
        required = timedelta(seconds=WAIT_TIME)
        for i in range(START, TOTAL_RESULTS, RESULTS_PER_ITERATION):
            logger.info("Results %s - %s", i + 1, i + RESULTS_PER_ITERATION)

            since_last_request = datetime.now() - last_request_dt
            if since_last_request < required:
                to_sleep = (required - since_last_request).total_seconds()
                logger.info("Sleeping for %f seconds before urlopen", to_sleep)
                time.sleep(to_sleep)

            last_request_dt = datetime.now()
            data = []
            try:
                with urlopen(BASE_URL + search_query + "&start=" + str(i)) as url:

                    since_last_request = datetime.now() - last_request_dt
                    if since_last_request < required:
                        to_sleep = (required - since_last_request).total_seconds()
                        logger.info("Sleeping for %f seconds before url.read()", to_sleep)
                        time.sleep(to_sleep)

                    last_request_dt = datetime.now()
                    response = url.read()

                    soup = BeautifulSoup(response, "html.parser")

                    res = soup.find_all('li', {'class': 'arxiv-result'})

                    if len(res) == 0:
                        logger.info("No result for period")

                    for element in res:  # ,{'class' : 'arxiv-result'}):
                        currentList = []

                        currentSoup = BeautifulSoup(str(element), "html.parser")
                        element = currentSoup.find('p')
                        ide, idLink, Links = extractIdAndLinks(element)
                        currentList.append(ide)
                        currentList.append(idLink)
                        currentList.append(str(Links))

                        # print("Id=", ide, idLink, Links)

                        element = currentSoup.find('div', {'class': 'tags'})
                        # print("Tags: ", extractArXiveTags(element))

                        currentList.append(str(extractArXiveTags(element)))

                        element = currentSoup.find_all('p', {'class': 'title'})

                        currentList.append(BeautifulSoup(str(element), "html.parser").find('p').getText().strip())

                        element = currentSoup.find_all('p', {'class': 'authors'})

                        # print("authors=", element.__str__())
                        authorsList = []
                        for a in BeautifulSoup(str(element), "html.parser").find_all('a'):
                            authorsList.append(a.getText())

                        currentList.append(str(authorsList))

                        element = currentSoup.find('span', {'class': 'abstract-full'})

                        # print("Abstract-full=", element.contents[0])

                        currentList.append(element.contents[0])  # .strip())

                        elem = currentSoup.findAll('p', {'class': 'is-size-7'})

                        # for ele in elem:
                        #     print("*",ele.__str__())

                        arXivExtraData = ""
                        for el in elem:
                            arXivExtraData = arXivExtraData + (el.getText())

                        # print("date:", extractDate(arXivExtraData))

                        currentList.append(extractDate(arXivExtraData))
                        currentList.append(arXivExtraData)

                        data.append(currentList)

                        logger.debug(currentList)
                        cur.execute('''insert into arXive \
                        ( entry_id,link,dlLinks,tags,title,authors,summary,pdate,extraData) values
                     (?, ?, ?, ?, ?, ?, ?, ?, ?)''', currentList)
                        con.commit()
                        records = cur.fetchall()
                        logger.debug("commit of current list: %s", str(records))

                    if len(res) < RESULTS_PER_ITERATION:
                        break  # no needs to continue "&start="  loop
            finally:
                pass
            # except urllib.error.URLError as e:
            #     logger.error(e.reason)
            # now = datetime.now()
            #
            # required = timedelta(seconds=WAIT_TIME)
            # since_last_request = datetime.now() - last_request_dt
            # if since_last_request < required:
            #     to_sleep = (required - since_last_request).total_seconds()
            #     logger.info("Sleeping for %f seconds", to_sleep)
            #     time.sleep(to_sleep)

cur.close()
con.commit()  # committe les transactions.
con.close()  # ferme la connection.
