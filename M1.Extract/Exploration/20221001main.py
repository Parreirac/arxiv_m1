# Extraction de la base CS.AI d'arXive en utilisant l'API arxiv
# le paramettre num_retries =3 permet de relancer pour les echecs sporadiques de la requette
# mais sur l'integralité de la base, les echecs ne sont plus sporadiques!
# Avec une recherche directe sur le site, on peut remarquer que dès qu'il y a plus de 10000 resultats
# alors le serveur ne retournera pas les valeurs au dela de 10000.
# il convient donc de segmenter au prealable la requette pour ne pas depasser les 10000 resultats
# pour memoire, sur cette année le nombre d'article est déjà de plus de 10 000!



import logging.config
import arxiv
import sqlite3


def printArXiveAutors(authors: list[arxiv.Result.Author]):
    returnValue = ""
    for a in authors:
        if len(returnValue) == 0:
            returnValue = a.name + "\n"
        else:
            returnValue = returnValue + a.name + "\n"

    return returnValue

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

big_slow_client = arxiv.Client(##
  page_size = 1000,
  delay_seconds =15,#0,
  num_retries =3 #10
)


search = big_slow_client.results(arxiv.Search(query="cat:cs.AI",sort_by=arxiv.SortCriterion.SubmittedDate))

cur = con.cursor()

cur.execute('''PRAGMA foreign_keys = OFF''')
cur.execute('''DROP TABLE SUMMARY''')
cur.execute('''PRAGMA foreign_keys = ON''')


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


index = 0
try:
    for i in search:
        index += 1
        cur.execute('''insert into SUMMARY ( entry_id, updated, published, title, authors, summary, comment, journal_ref,
                    doi, primary_category, categories, links) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', [i.entry_id, i.updated, i.published, i.title, printArXiveAutors(i.authors), i.summary,
             i.comment, i.journal_ref, i.doi, i.primary_category, printArXiveCategories(i.categories),printArXiveLinks(i.links)])

        con.commit()

except Exception:
    logging.error('Failed.', exc_info=True, stack_info=False)

cur.close()
con.commit()  # committe les transactions.
con.close()  # ferme la connection.
