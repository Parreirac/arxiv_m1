"""
Si le fichier.pdf n'est pas en local, le charger.

Ajouter a la DBB des colonnes :
- l'outil de production du pdf
- les mots cles
- l'entete des auteurs (auteurs & labo)
- la biblio en html

Prendre une ligne de la DB et remplir les données manquantes
"""
import logging
import sqlite3
import time
from datetime import datetime, timedelta
from os.path import exists

import requests
from langid.langid import LanguageIdentifier, model

from ExtractDataFromPDF import ExtractDataFrom
import settings

# To allow download of missing file
DOWNLOADMISSINGFILE = False

ALLOWRECOMPUTE = True  # set to True to recompute additional Data
WAIT_TIME = 3

sql_request: str = '''SELECT * from arXive'''  # where pdate like '%2007' '''

logger = logging.getLogger()


def create_dict(string: str) -> dict[str, str] | None:
    '''Création d'un dictionnaire à partir d'une string'''
    if not string.startswith('{'):
        return None
    tab = string[1: len(string) - 1].split("'")

    return_value = {}
    for i in range(0, len(tab) - 1, 4):
        return_value[tab[i + 1]] = tab[i + 3]

    return return_value


def create_list(string: str) -> list[str] | None:
    '''Création d'une liste à partir d'une string'''
    if not string.startswith('['):
        return None
    tab = string[1: len(string) - 1].split("'")

    return_value = []
    for i in range(1, len(tab), 2):
        return_value.append(tab[i])
    return return_value


logger.info('Start !')
#: crée une connection.  # TODO PRA  quitter proprement si pas de BDD ou si déjà bloquée

con = sqlite3.connect(settings.STARTDIRECTORY + settings.DATABASE)
cur = con.cursor()

cur.execute('''PRAGMA table_info(arXive)''')
records = cur.fetchall()
required = timedelta(seconds=WAIT_TIME)

COLUMNALREADYADDED = False

for element in records:
    if element[1] == 'mCOMMENTS':
        COLUMNALREADYADDED = True
        break

if not COLUMNALREADYADDED:
    # REFERENCES est un mot clé j'ajoute un prefixe m manuel, c calculé, e extrait
    cur.execute('''ALTER TABLE arXive ADD COLUMN mCOMMENTS TEXT''')
    cur.execute('''ALTER TABLE arXive ADD COLUMN cFIRST_CAT TEXT''')
    cur.execute('''ALTER TABLE arXive ADD COLUMN eSUBTITLE TEXT''')
    cur.execute('''ALTER TABLE arXive ADD COLUMN eKEYWORDS TEXT''')
    cur.execute('''ALTER TABLE arXive ADD COLUMN eREFERENCES TEXT''')
    cur.execute('''ALTER TABLE arXive ADD COLUMN ePDF_METADATA TEXT''')
    cur.execute('''ALTER TABLE arXive ADD COLUMN eLanguage TEXT''')
    # cur.execute('''ALTER TABLE arXive ADD COLUMN APPLICATION TEXT''')

cur.execute(sql_request)

records = cur.fetchall()
logger.debug("%s records to handle",len(records))

last_request_dt = datetime.min  # .now()

identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

for row in records:
    entry_id = row[0]
    link = row[1]
    dlLinks = row[2]
    dlLinks = create_dict(dlLinks)
    tags = row[3]
    tags = create_list(tags)
    title = row[4]
    authors = row[5]
    authors = create_list(authors)
    summary = row[6]
    pdate = row[7]
    extraData = row[8]
    COMMENTS = row[9]
    FirstCat = row[10]
    SUBTITLE = row[11]
    KEYWORDS = row[12]
    REFERENCES = row[13]
    PDF_METADATA = row[14]
    eLanguage = row[15]

    if not ALLOWRECOMPUTE:  # or  FirstCat is not None:
        continue
    # FirstCat = tags[0]

    #var = ""

    if "pdf" not in dlLinks:
        logger.warning("ArXIve gives no pdf for %s",entry_id)
        continue

    url = dlLinks['pdf']

    tmpTab = url.split('/')

    fileName = tmpTab[len(tmpTab) - 1] + ".pdf"

    if not exists(settings.STARTDIRECTORY + settings.PDFREPOSITORY + fileName):  # download file
        if DOWNLOADMISSINGFILE:
            since_last_request = datetime.now() - last_request_dt
            if since_last_request < required:
                to_sleep = (required - since_last_request).total_seconds()
                logger.info("Sleeping for %f seconds before urlopen", to_sleep)
                time.sleep(to_sleep)

            last_request_dt = datetime.now()
            logger.info("download file %s",fileName)
            r = requests.get(url)
            # Retrieve HTTP meta-data

            logger.debug("status_code %s", r.status_code)
            logger.debug("headers %s", r.headers['content-type'])
            logger.debug("encoding %s", r.encoding)

            if r.status_code != 200:
                logger.warning("Error downloading %s, status_code = %s", fileName, r.status_code)
                continue  # TODO PRA a tester

            with open(settings.STARTDIRECTORY + settings.PDFREPOSITORY + fileName, 'wb') as f:
                f.write(r.content)
        else:
            continue

    try:

        rv_fileMetadata, rv_subtitle, rv_keywords, rv_reference_list = ExtractDataFrom(
            settings.STARTDIRECTORY + settings.PDFREPOSITORY + fileName, title, authors, summary)

    except Exception:  # TODO PRA etre plus explicite
        logger.error("file %s not extracted ", settings.PDFREPOSITORY + fileName, exc_info=True)
    else:
        SQL = ''' UPDATE arXive
                      SET cFIRST_CAT = ? ,
                          eSUBTITLE = ? ,
                          eKEYWORDS = ? ,
                          eREFERENCES = ? ,    
                          ePDF_METADATA = ?
                      WHERE entry_id = ?'''

        #                          eLanguage = ?

        # b = TextBlob(summary)
        # langue = b.detect_language()


        # langue = res[0]+'_'+str(int(100*res[1]))
        data = (
            FirstCat, rv_subtitle, rv_keywords, repr(rv_reference_list), repr(rv_fileMetadata),
            # langue,
            entry_id)
        cur.execute(SQL, data)  # TODO PRA ajouter un test avant sur un verrou sur la BDD !
        records = cur.fetchall()

cur.close()
con.commit()  # committe les transactions.
con.close()  # ferme la connection.
