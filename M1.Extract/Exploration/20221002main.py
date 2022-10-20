#  Deuxieme tentative, fonctionne si max_results <= 10000

from pyarxiv import query, download_entries
from pyarxiv.arxiv_categories import ArxivCategory, arxiv_category_map

# query(max_results=100, ids=[], categories=[],
#                title='', authors='', abstract='', journal_ref='',
#                querystring='')
entries = query(title='WaveNet') 
titles = map(lambda x: x['title'], entries)

myList = list(titles)
print(len(myList), " ", myList)


#download_entries(entries_or_ids_or_uris=[], target_folder='.',
#                     use_title_for_filename=False, append_id=False,
#                     progress_callback=(lambda x, y: id))

#download_entries(entries)


entries_with_category = query(max_results=10001,categories=[ArxivCategory.cs_AI])
# //print(arxiv_category_map(ArxivCategory.cs_AI))
titles = map(lambda x: x['title'], entries_with_category)
myList = list(titles)
print(len(myList), " ", myList)
