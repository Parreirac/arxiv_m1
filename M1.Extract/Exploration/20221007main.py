# This is a sample Python script.

import logging.config
import arxiv
import settings
import sqlite3
from typing import Dict,  List


class MySearch(arxiv.Search):
    '''
    On adapte la classe search car la requette évoluée est différente.
    On ajoute egalement l'année de la recherche
    '''

    year = 2009  # todo chercher a mettre automatiquement l'année courante

    def __init__(
        self,
        query: str = "",
        id_list: List[str] = [],
        max_results: float = float('inf'),
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance,
        sort_order: arxiv.SortOrder = arxiv.SortOrder.Descending,
        year: int = None
    ):
        super().__init__(query, id_list, max_results, sort_by, sort_order)
        if year is not None:
            self.year = year  # todo mettre l'année courante

    def _url_args(self) -> Dict[str, str]:
        """
        Redefinition de la methode de classe de base
        Returns a dict of search parameters that should be included in an API
        request for this search.
        """


        '''
https://arxiv.org/search/advanced?
advanced=&
terms-0-term=cs.AI&
terms-0-field=cross_list_category&
date-filter_by=specific_year&date-year=2020&date-from_date=&date-to_date=
&date-date_type=submitted_date&abstracts=show&size=25&order=-announced_date_first
        '''
        if self.year is None:
            return {
                "advanced": "",
                "terms-0-term": self.query,  # "search_query": self.query,
                # "id_list": ','.join(self.id_list),
                "terms-0-field": "cross_list_category",
                "sortBy": self.sort_by.value,
                "sortOrder": self.sort_order.value
            }
        else :
            return {
            "advanced": "",
            "terms-0-term": self.query,  # "search_query": self.query,
            # "id_list": ','.join(self.id_list),
            "terms-0-field": "cross_list_category",#  ajout pra
            "date-filter_by": "specific_year",#  ajout pra
            "date-year": str(self.year), #  ajout pra
            "date-from_date": "", #  ajout pra
            "date-to_date": "", #  ajout pra
            "sortBy": self.sort_by.value,
            "sortOrder": self.sort_order.value
            }




class MyClient(arxiv.Client):

    '''
    On adapte la classe client pour :
    1/ spécifier l'adresse

    '''

    query_url_format = 'https://arxiv.org/search/advanced?{}'  #'http://export.arxiv.org/api/query?{}'

    def __init__(
            self,
            page_size: int = 25,
            delay_seconds: int = 3,
            num_retries: int = 3,
    ):
        super().__init__( page_size , delay_seconds , num_retries )


#     def _format_url(self, search: arxiv.Search, start: int, page_size: int) -> str:
#         """
#         Construct a request API for search that returns up to `page_size`
#         results starting with the result at index `start`.
#         """
#         '''
#         &date-filter_by=specific_year&date-year={str(year)}" \
#                f"&date-from_date=&date-to_date=&date-date_type=submitted_date" \
#                f"&abstracts=show
#
# date-filter_by=specific_year&date-year={str(year)}" \
#                f"&date-from_date=&date-to_date=&date-date_type=submitted_date" \
#                f"&abstracts=show
#                '''
#
#         url_args = search._url_args()
#
#         url_args.update({
#             "start": start,
#             "max_results": page_size,
#         })
#
#         partOfUrl = arxiv.urlencode(url_args)
#         result = self.query_url_format.format(partOfUrl)
#         logger.info("url args " + partOfUrl)
#         logger.info("full url "+result)
#         return result



def printArXiveAutors(authors: list[arxiv.Result.Author]):
    returnValue = ""
    for a in authors:
        if len(returnValue) == 0:
            returnValue = a.name + "\n"
        else:
            returnValue = returnValue + a.name + "\n"

    return returnValue
    # str = ""
    # for personne in authors:
    #     str = str + " " + personne


def printArXiveCategories(categories: list[str]):
    returnValue = ""
    for a in categories:
        if len(returnValue) == 0:
            returnValue = a + "\n"
        else:
            returnValue = returnValue + a + "\n"

    return returnValue


def printArXiveLinks(links: list[arxiv.Result.Link]):
    returnValue = ""
    for a in links:
        if len(returnValue) == 0:
            returnValue = a.href + "\n"
        else:
            returnValue = returnValue + a.href + "\n"

    return returnValue


logger = logging.getLogger()

con = sqlite3.connect('myFile.db')  #: crée une connection.
#: con = sqlite3.connect(':memory:')

'''
    Parameter “query” is used to assign the query word (text format).
    Parameter “max_results” is used to assign the number of results (numeric). If not set, the default value is 10 and the maximum limit is 300,000 results.
    Parameter “sort_by” is used to specify the criteria that would be used to sort the output. The value can submittedDate, lastUpdatedDate, relevance. When set to submittedDate, you can search for latest papers.
    Parameter “sort_order” is used to specify the order in which results will be sorted. The value can be Ascending or Descending.
    There is also an additional parameter called as id_list which can be used in place of query when one wants to get specific set of papers. You can specify the id_list with ids array. It can be in the format such as id_list = [“2107.10495v1”]. 
'''

big_slow_client = MyClient(#) arxiv.Client(##
  page_size = 25,
  delay_seconds =15,#0,
  num_retries =3 #10
)



search = big_slow_client.results(MySearch(query="cs.AI",sort_by=arxiv.SortCriterion.SubmittedDate,year=2009))
#search = big_slow_client.results(arxiv.Search(query="cat:cs.AI&start=20&max_results=10 ",sort_by=arxiv.SortCriterion.SubmittedDate))


#
# search = arxiv.Search(
#     query= "cat:cs.AI",#,&date-year=2020", #"Computer Science",   quantum",
#     max_results=10,
#     sort_by=arxiv.SortCriterion.SubmittedDate)


#logger.info("max_results = "+str(search.max_results))

# REM : on peut logger les exceptions :
# try:
#   c = a / b
# except Exception as e:
#   logging.error(f"Exception occurred: {e}", exc_info=True)



'''
    result.entry_id: A url http://arxiv.org/abs/{id}.
    result.updated: When the result was last updated.
    result.published: When the result was originally published.
    result.title: The title of the result.
    result.authors: The result's authors, as arxiv.Authors.
    result.summary: The result abstract.
    result.comment: The authors' comment if present.
    result.journal_ref: A journal reference if present.
    result.doi: A URL for the resolved DOI to an external resource if present.
         Digital Object Identifier (DOI), ie preprint hav been printed !
    result.primary_category: The result's primary arXiv category. See arXiv: Category Taxonomy.
    result.categories: All of the result's categories. See arXiv: Category Taxonomy.
    result.links: Up to three URLs associated with this result, as arxiv.Links.
    result.pdf_url: A URL for the result's PDF if present. Note: this URL also appears among result.links.

'''
cur = con.cursor()

cur.execute('''PRAGMA foreign_keys = OFF''')
cur.execute('''DROP TABLE SUMMARY''')
cur.execute('''PRAGMA foreign_keys = ON''')



#   entry_id  TEXT PRIMARY KEY UNIQUE,
cur.execute('''CREATE TABLE IF NOT EXISTS SUMMARY( 
  entry_id  TEXT PRIMARY KEY,
  updated  TEXT,
  published  TEXT,
  title TEXT,
  authors  TEXT,
  summary TEXT,
  comment  TEXT,
  journal_ref  TEXT,
  doi TEXT,
  primary_category TEXT,
  categories TEXT,
  links TEXT)''')


"""
data = [[i.entry_id, i.updated, i.published, i.title, printArXiveAutors(i.authors), i.summary,
         i.comment, i.journal_ref, i.doi, i.primary_category, printArXiveCategories(i.categories),
         printArXiveLinks(i.links)] for i in search.results()]
"""


index = 0
try:
    for i in search:#.results():
        # print(d)
        index += 1
       # logger.info(f"Inserting = {index}")
       #  logger.debug(f"avant {i.entry_id}")
        cur.execute('''insert into SUMMARY ( entry_id, updated, published, title, authors, summary, comment, journal_ref,
                    doi, primary_category, categories, links) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', [i.entry_id, i.updated, i.published, i.title, printArXiveAutors(i.authors), i.summary,
             i.comment, i.journal_ref, i.doi, i.primary_category, printArXiveCategories(i.categories),printArXiveLinks(i.links)])
        # logger.debug(f"apres")
        con.commit()
        # logger.debug(f"commit")
except Exception:
    logging.error('Failed.', exc_info=True, stack_info=False)
    # data = [[i.entry_id, i.updated, i.published, i.title, printArXiveAutors(i.authors), i.summary,
    #          i.comment, i.journal_ref, i.doi, i.primary_category, printArXiveCategories(i.categories),
    #          printArXiveLinks(i.links)] for i in search.results()]

    # for d in data:
    #     print(d)
    # data = [[1, 'aaa'], [2, 'bbb'], [3, 'ccc']]
    # for d in data:
    #     print(d)
        # cur.execute('''insert into resume ( entry_id, updated, published, title, authors, summary, comment, journal_ref,
        #             doi, primary_category, categories, links) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', d)



cur.close()
con.commit()  # committe les transactions.
con.close()  # ferme la connection.
