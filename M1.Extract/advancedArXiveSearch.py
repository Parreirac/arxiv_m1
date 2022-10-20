import sqlite3
import time
from urllib.request import urlopen

import feedparser
from feedparser import FeedParserDict

# /!\ Ne fonctionne que si results_per_iteration = 25
from bs4 import BeautifulSoup


# to add dict in set, we need to freeze them
# def freeze(d):
#     if isinstance(d, dict):
#         return frozenset((key, freeze(value)) for key, value in d.items())
#     elif isinstance(d, list):
#         return tuple(freeze(value) for value in d)
#     return d

def freeze(d):
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


# base_url = "http://export.arxiv.org/api/query?"
base_url = ""  # https://arxiv.org/search/advanced?"

# Search parameters
start = 0  # start at the first result
total_results = 200000000  # want 20 total results
results_per_iteration = 200  # 5 results at a time
wait_time = 3  # number of seconds to wait beetween calls

con = sqlite3.connect('../myArXive.db')  #: crée une connection.
cur = con.cursor()

cur.execute('''PRAGMA foreign_keys = OFF''')
cur.execute('''DROP TABLE arXive''')
cur.execute('''PRAGMA foreign_keys = ON''')



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

# year = 2001

#toute requette arXive est limitee a 10000 ^^

for year in range(2010, 2000, -1):
    for month in range(1, 12, 1):
        search_query = "https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term=cs.AI" \
                       "&terms-0-field=all&classification-physics_archives=all" \
                       "&classification-include_cross_list=include&date-year=&date-filter_by=date_range" \
                       "&date-from_date={0}-{1}&date-to_date={0}-{1}&date-date_type=submitted_date" \
                       "&abstracts=show&size={3}&order=-announced_date_first".format(year,month,month+1,results_per_iteration)

        print(f'Searching arXiv for {search_query}')


        for i in range(start, total_results, results_per_iteration):
            print(f"Results {i + 1} - {i + results_per_iteration}")

            print("# pouet " + base_url + search_query + "&start=" + str(i))

            data = []
            with urlopen(base_url + search_query + "&start=" + str(i)) as url:
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
                    break

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

                    print(currentList)
                    cur.execute('''insert into arXive ( entry_id,link,dlLinks,tags,title,authors,summary,pdate,extraData) values
                 (?, ?, ?, ?, ?, ?, ?, ?, ?)''', currentList)

            print(f"Sleeping for {wait_time} seconds")
            time.sleep(wait_time)

cur.close()
con.commit()  # committe les transactions.
con.close()  # ferme la connection.
