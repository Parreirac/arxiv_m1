"""
si le fichier.pdf n'est pas en local, le charger.

Ajouter a la DBB des colonnes :
- l'outil de production du pdf
- les mots cles
- l'entete des auteurs (auteurs & labo)
- la biblio en html

Prendre une ligne de la DB et remplir les données manquantes
"""
import settings  # TODO PRA si je le commente cela ne donne pas le meme resultat
import logging
import sqlite3
from os.path import exists
# from typing import Dict

import requests as requests

from ExtractDataFromPDF import ExtractDataFrom

pdfRepository = "./Files/"  # directory must exist... TODO ?

dataBase = 'myArXive.db'
logger = logging.getLogger()
downloadMissingFile = False  # To allow download of missing file
AllowRecompute = True  # set to True to recompute additional Data


def createDict(string: str) -> dict[str, str] | None:
    if not string.startswith('{'):
        return None
    tab = string[1: len(string) - 1].split("'")

    returnValue = dict()
    for i in range(0, len(tab) - 1, 4):
        returnValue[tab[i + 1]] = tab[i + 3]

    return returnValue


def createList(string: str) -> list[str] | None:
    if not string.startswith('['):
        return None
    tab = string[1: len(string) - 1].split("'")

    returnValue = list()
    for i in range(1, len(tab), 2):
        returnValue.append(tab[i])
    return returnValue


logger.info('Start !')

con = sqlite3.connect(dataBase)  #: crée une connection.  # TODO PRA  quitter proprement si pas de BDD ou si déjà bloquée
cur = con.cursor()

cur.execute('''PRAGMA table_info(arXive)''')
records = cur.fetchall()

ColumnAlreadyAdded = False

for element in records:
    if element[1] == 'mCOMMENTS':
        ColumnAlreadyAdded = True
        break

if not ColumnAlreadyAdded:
    cur.execute('''ALTER TABLE arXive ADD COLUMN mCOMMENTS TEXT''')
    cur.execute('''ALTER TABLE arXive ADD COLUMN cFIRST_CAT TEXT''')
    cur.execute('''ALTER TABLE arXive ADD COLUMN eSUBTITLE TEXT''')
    cur.execute('''ALTER TABLE arXive ADD COLUMN eKEYWORDS TEXT''')
    cur.execute('''ALTER TABLE arXive ADD COLUMN eREFERENCES TEXT''')  #REFERENCES est un mot clé j'ajoute un prefixe m manuel, c calculé, e extrait
    cur.execute('''ALTER TABLE arXive ADD COLUMN ePDF_METADATA TEXT''')
    # cur.execute('''ALTER TABLE arXive ADD COLUMN APPLICATION TEXT''')

    '''
Pour supprimer faire dans le DB browser:
ALTER table arXive drop SUBTITLE
ALTER table arXive drop FirstCat
ALTER table arXive drop KEYWORDS
ALTER table arXive drop REFERENCES
ALTER table arXive drop PDF_METADATA
ALTER table arXive drop APPLICATION
'''

cur.execute('''SELECT * from arXive''')
# For debug purpose, filter database
# cur.execute('''SELECT * from arXive where pdate like '___January__2010' ''')

records = cur.fetchall()

for row in records:
    entry_id = row[0]
    link = row[1]
    dlLinks = row[2]
    dlLinks = createDict(dlLinks)
    tags = row[3]
    tags = createList(tags)
    title = row[4]
    authors = row[5]
    authors = createList(authors)
    summary = row[6]
    pdate = row[7]
    extraData = row[8]
    COMMENTS = row[9]
    FirstCat = row[10]
    SUBTITLE = row[11]
    KEYWORDS = row[12]
    REFERENCES = row[13]
    PDF_METADATA = row[14]


    if (not AllowRecompute) and FirstCat is not None:
        continue
    FirstCat = tags[0]

    var = ""

    if "pdf" not in dlLinks:
        logger.warning("ArXIve gives no pdf for {}".format(entry_id))
        continue

    url = dlLinks['pdf']

    tmpTab = url.split('/')

    fileName = tmpTab[len(tmpTab) - 1] + ".pdf"

    if not exists(pdfRepository + fileName):  # download file
        if downloadMissingFile:
            logger.info("download file {}".format(fileName))
            r = requests.get(url)
            # Retrieve HTTP meta-data

            logger.debug("status_code {}".format(r.status_code))
            logger.debug("headers {}".format(r.headers['content-type']))
            logger.debug("encoding {}".format(r.encoding))

            if r.status_code != 200:
                logger.warning("Error downloading {}, status_code = {}".format(fileName, r.status_code))
                continue  # TODO PRA a tester

            with open(pdfRepository + fileName, 'wb') as f:
                f.write(r.content)
        else:
            continue
    try:

        # rv_creator, rv_producer, rv_subtitle, rv_keywords, rv_reference_list, rv_reference_ctrl_set
        rv_fileMetadata, rv_subtitle, rv_keywords, rv_reference_list = ExtractDataFrom(
            pdfRepository + fileName, title, authors, summary)

    except Exception:  # TODO PRA etre plus explicite
        logger.error("file {} not extracted ".format(pdfRepository + fileName), exc_info=True)
    else:
        sql = ''' UPDATE arXive
                      SET cFIRST_CAT = ? ,
                          eSUBTITLE = ? ,
                          eKEYWORDS = ? ,
                          eREFERENCES = ? ,    
                          ePDF_METADATA = ?
                      WHERE entry_id = ?'''  # TODO PRA avec un s a reference!

        data = (
            FirstCat, rv_subtitle, rv_keywords, rv_reference_list.__repr__(), rv_fileMetadata.__repr__(),
            entry_id)
        cur.execute(sql, data)
        records = cur.fetchall()

cur.close()
con.commit()  # committe les transactions.
con.close()  # ferme la connection.
