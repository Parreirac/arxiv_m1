"""
si le fichier.pdf n'est pas en local, le charger.

Ajouter a la DBB des colonnes :
- l'outil de production du pdf
- les mots cles
- l'entete des auteurs (auteurs & labo)
- la biblio en html

Prendre une ligne de la DB et remplir les données manquantes
"""
import json
import logging
import sqlite3
import time
# import s2 as toto
from datetime import datetime, timedelta
from os.path import exists

# from semanticscholar import SemanticScholar
import requests as requests
from langid.langid import LanguageIdentifier, model
from semanticscholar import SemanticScholar
from semanticscholar.SemanticScholarException import ObjectNotFoundExeception

import settings  # TODO PRA si je le commente cela ne donne pas le meme resultat
from ExtractDataFromPDF import ExtractDataFrom

#from urllib.request import urlopen

#toto.api

# from typing import Dict
S2APIKEY = "VANqk2Qb0k2qFa9u4S4NK9iphWDa47429E6XGC04"
startDirectory: str = "D:\mon_depot\\"
pdfRepository = "./Files/"  # directory must exist... TODO ?
dataBase = 'myArXive.db'
downloadMissingFile = False
# To allow download of missing file
AllowRecompute = False  # set to True to recompute additional Data
wait_time = 3
# sql_request = '''SELECT * from arXive '''
sql_request: str = '''SELECT * from arXive''' # where pdate like '%2001' '''

logger = logging.getLogger()
sch = SemanticScholar(api_key=S2APIKEY,api_url="https://partner.semanticscholar.org/v1") #  "https://api.semanticscholar.org/v1")

def create_dict(string: str) -> dict[str, str] | None:
    if not string.startswith('{'):
        return None
    tab = string[1: len(string) - 1].split("'")

    return_value = dict()
    for i in range(0, len(tab) - 1, 4):
        return_value[tab[i + 1]] = tab[i + 3]

    return return_value


valuesToRemove = ["citationVelocity", "corpusId", "fieldsOfStudy", "influentialCitationCount",
                      "isOpenAccess", "isPublisherLicensed", "is_open_access", "is_publisher_licensed",
                      "numCitedBy", "numCiting", "s2FieldsOfStudy", "citationCount",'embedding','openAccessPdf',
                  "referenceCount","tldr","data","hIndex","raw_data"]

def getS2Dict(obj):
    try: # How to check whether this exists or not
        obj2 = obj.__dict__
    # Method exists and was used.
        obj3 = dict()

        for cle, valeur in obj2.items():
            cle2 = cle
            if cle2[0] == '_':
                cle2 = cle2[1:]  # remove first character (_)
            obj3[cle2] = valeur

        return obj3

    except AttributeError:
        return None


def simplifyS2Objetc(obj:object):
    if  not isinstance(obj, dict): # search a hidden dictionary
        obj2 = getS2Dict(obj)
        if obj2 is None:
            return obj
        obj = obj2

    # first level filter
    d2 = dict()
    for k,v in obj.items():
        if k not in valuesToRemove:
            d2[k] = v

    #update sub dict
    for cle, valeur in d2.items():
        if isinstance(valeur, dict):
            value_to_keep = []
            if cle == 'externalIds':
                value_to_keep = ['ArXiv','DOI']
            if cle == 'journal':
                value_to_keep = ['name', 'pages','Volume']

            if len(value_to_keep) > 0:
                d3 = dict()
                for sub_cle, sub_valeur in valeur.items():
                    if sub_cle in value_to_keep:
                        d3[sub_cle] = sub_valeur
                d2[cle] = d3
            else:
                d2[cle] = valeur

            d2[cle] = simplifyS2Objetc(d2[cle])
            continue
        else:
            valeur2 = getS2Dict(valeur)
            if valeur2 is not None:
                value_to_keep = [] # TODO factoriser le code avec la brique du dessus
                if cle == 'externalIds':
                    value_to_keep = ['ArXiv', 'DOI']
                if cle == 'journal':
                    value_to_keep = ['name', 'pages', 'Volume']

                if len(value_to_keep) > 0:
                    d3 = dict()
                    for sub_cle, sub_valeur in valeur2.items():
                        if sub_cle in value_to_keep:
                            d3[sub_cle] = sub_valeur
                    d2[cle] = d3
                else:
                    d2[cle] = valeur2

                d2[cle] = simplifyS2Objetc(d2[cle])

        if isinstance(valeur, list):
            valeur2 = []
            for elem in valeur:
                if isinstance(elem, dict):
                    valeur2.append(simplifyS2Objetc(elem))
                else:
                    elem2 = getS2Dict(elem)
                    if elem2 is not None:
                        valeur2.append(simplifyS2Objetc(elem2))

            if len(valeur2) == len (valeur) and len (valeur) > 0:
                d2[cle] = valeur2
            continue

    return d2


def extractNumPages(txt: str):  # TODO pra chercher par le pdf ou les commentaires
    pass



#session = requests.Session()

#session.headers['x-api-key'] = S2APIKEY
api_url="https://api.semanticscholar.org/v1" #"https://api.semanticscholar.org/graph/v1/paper/batch" #"https://api.semanticscholar.org/v1"
#api_url="https://api.semanticscholar.org/graph/v1" # adresse de base  refuse topics
#api_url="https://partner.semanticscholar.org/v1" # si j'ai une clé
#https://api.semanticscholar.org/v1/paper/arXiv:1705.10311?&field=Topics.topic
# citationStyles

FIELDS = [
    #'abstract',
    'authors',
    ##'authors.affiliations',
    ##'authors.aliases',
    ##'authors.authorId',
    #'authors.citationCount',
    ##'authors.externalIds',
    #'authors.hIndex',
    ##'authors.homepage',
    ##'authors.name',
    #'authors.paperCount',
    ##'authors.url',
    #'citationCount',
    #'citations',
    #'citations.abstract',
    ##'citations.authors',
    #'citations.citationCount',
    #'citations.corpusId',
    ##'citations.externalIds',
    #'citations.fieldsOfStudy',
    #'citations.influentialCitationCount',
    #'citations.isOpenAccess',
    ##'citations.journal',
    #'citations.openAccessPdf',
    ##'citations.paperId',
    ##'citations.publicationDate',
    ##'citations.publicationTypes',
    ##'citations.publicationVenue',
    #'citations.referenceCount',
    #'citations.s2FieldsOfStudy',
    ##'citations.title',
    #'citations.url',
    ##'citations.venue',
    ##'citations.year',
    #"'corpusId',
    #'embedding',
    ##'externalIds',
    #'fieldsOfStudy',
    #'influentialCitationCount',
    #'isOpenAccess',
    #'journal',
    #'openAccessPdf',
    'paperId',
    ##'publicationDate',
    'publicationTypes',
    #'publicationVenue',
    #'referenceCount',
    #'references',
    #'references.abstract',
    ##'references.authors',
    #'references.citationCount',
    #'references.citationStyles',
    #'references.corpusId',
    ##'references.externalIds',
    #'references.fieldsOfStudy',
    #'references.influentialCitationCount',
    #'references.isOpenAccess',
    ##'references.journal',
    #'references.openAccessPdf',
    ##'references.paperId',
    ##'references.publicationDate',
    ##'references.publicationTypes',
    ##'references.publicationVenue',
    #'references.referenceCount',
    #'references.s2FieldsOfStudy',
    ##'references.title',
    #'references.url',
    ##'references.venue',
    ##'references.year',
    #'s2FieldsOfStudy',
    'title',
    #'tldr',
    #'url',
    'venue',
    'year',
    'topics',
    'topics.topic',
    'topics.topicId'

]



def myGetPapers(ids:list):

    ids = [ids[0]]
    if len(ids) <2:
        base_url = api_url+"/paper/{}".format(ids[0])
    else:
        base_url = api_url+"/paper/batch" # {\"ids\":[\""+ '\",\"'.join(ids)+"\"]}"
    #/batch?fields=title,isOpenAccess,openAccessPdf,authors{"ids":["649def34f8be52c8b66281af98ae884c09aef38b", "ARXIV:2106.15928"]}

    print(base_url) #https://api.semanticscholar.org/graph/v1/paper/batch

    #fields = ','.join(fields)
    #parameters = f'&fields={fields}'

    fields = ','.join(FIELDS)
    parameters = f'&fields={fields}'


    base_url = f'{base_url}?{parameters}'

    #with urlopen(base_url) as url:
        #response = url.read()

        #~~
    data = {'ids': ids}
        #data_json = simplejson.dumps(data)
    jd = json.dumps(data)
    payload = {'json_payload': jd}
    #response = requests.post(base_url, json=payload)
    #'Accept': 'text/plain',
    headers = {"charset": "utf-8",'Content-type': 'application/json', 'x-api-key': S2APIKEY, 'Accept': 'text/plain'}
    #response = requests.post(base_url, json=data, headers=headers)

    #methode = "GET"
    method = 'POST' if len(ids) > 1 else 'GET'
    #payload = json.dumps({'ids': ids}) if len(ids)>1 else None
    payload = {'ids': ids} if len(ids) > 1 else None

    #if len(ids) > 1:
    #    response = session.put(base_url, timeout=10, headers=headers, json=payload)

    #url = "http://localhost:8080"
    #data = {'sender': 'Alice', 'receiver': 'Bob', 'message': 'We did it!'}
    #headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    #r = requests.post(url, data=json.dumps(data), headers=headers)
    #if len(ids) > 1:
    #    response = session.put(base_url,timeout=10, headers=headers, data=payload) # **kwargs)
    #else:
    #    response = session.get(base_url,timeout=10, headers=headers)

    dataToSend = json.dumps(payload)  if len(ids) > 1 else None
    response = requests.request(method, base_url, timeout=10, headers=headers, data=dataToSend)
        #response = requests.post(base_url, data=payload) json={'json_payload': data}    json.dumps(payload)
        #~~

    #md = json.loads(response)
    data = {}
    if response.status_code == 200:
        data = response.json()
        if len(data) == 1 and 'error' in data:
            data = {}
    elif response.status_code == 400:
        data = response.json()
        raise Exception(data['message']) #BadQueryParametersException(data['error'])
    elif response.status_code == 403:
        raise PermissionError('HTTP status 403 Forbidden.')
    elif response.status_code == 404:
        data = response.json()
        raise ObjectNotFoundExeception(data['error'])
    elif response.status_code == 429:
        raise ConnectionRefusedError('HTTP status 429 Too Many Requests.')
    elif response.status_code in [500, 504]:
        data = response.json()
        raise Exception(data['message'])

    return data

    #return md


def create_list(string: str) -> list[str] | None:
    if not string.startswith('['):
        return None
    tab = string[1: len(string) - 1].split("'")

    return_value = list()
    for i in range(1, len(tab), 2):
        return_value.append(tab[i])
    return return_value

logger.info('Start !')
con = sqlite3.connect(
    settings.STARTDIRECTORY + settings.DATABASE)  #: crée une connection.  # TODO PRA  quitter proprement si pas de BDD ou si déjà bloquée
cur = con.cursor()

cur.execute('''PRAGMA table_info(arXive)''')
records = cur.fetchall()
required = timedelta(seconds=wait_time)


ListColumn = [e[1] for e in records]

ColumnToAdd = ['mCOMMENTS','cFIRST_CAT','eSUBTITLE','eKEYWORDS','eREFERENCES','ePDF_METADATA','ePDF_METADATA',
               'eLanguage','eNumpages','JSON']

for elem in ColumnToAdd:
    if elem in ListColumn:
        continue
    command = '''ALTER TABLE arXive ADD COLUMN '''+elem+''' TEXT'''
    cur.execute(command)

'''
Pour supprimer faire dans le DB browser:
ALTER table arXive drop SUBTITLE
ALTER table arXive drop FirstCat
ALTER table arXive drop KEYWORDS
ALTER table arXive drop REFERENCES
ALTER table arXive drop PDF_METADATA
ALTER table arXive drop APPLICATION
'''

# cur.execute('''SELECT * from arXive''')
# For debug purpose, filter database
cur.execute(sql_request)

records = cur.fetchall()
logger.debug("{} records to handle".format(len(records)))

last_request_dt = datetime.min  # .now()
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

# Download missing files
if downloadMissingFile:
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
        eNumpages = row[16]
        JSON = row[17]
    
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
    
        if not exists(startDirectory + pdfRepository + fileName):  # download file
            if downloadMissingFile:
                since_last_request = datetime.now() - last_request_dt
                if since_last_request < required:
                    to_sleep = (required - since_last_request).total_seconds()
                    logger.info("Sleeping for %f seconds before urlopen", to_sleep)
                    time.sleep(to_sleep)
    
                last_request_dt = datetime.now()
                logger.info("download file {}".format(fileName))
                r = requests.get(url)
                # Retrieve HTTP meta-data
    
                logger.debug("status_code {}".format(r.status_code))
                logger.debug("headers {}".format(r.headers['content-type']))
                logger.debug("encoding {}".format(r.encoding))
    
                if r.status_code != 200:
                    logger.warning("Error downloading {}, status_code = {}".format(fileName, r.status_code))
                    continue  # TODO PRA a tester
    
                with open(startDirectory + pdfRepository + fileName, 'wb') as f:
                    f.write(r.content)
# do the job
i = 0

paperToGet = []
paperLanguage = []
for row in records:
    i = i+1
    #if i == 1000:
    #    break
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
    eNumpages = row[16]
    JSON = row[17]

    #if (not AllowRecompute) and JSON is not None:
    #    continue
    FirstCat = tags[0]

    var = ""

    if "pdf" not in dlLinks:
        logger.warning("ArXIve gives no pdf for {}".format(entry_id))
        continue

    url = dlLinks['pdf']

    tmpTab = url.split('/')

    fileName = tmpTab[len(tmpTab) - 1] + ".pdf"

    try:

        if AllowRecompute and exists(startDirectory + pdfRepository + fileName):
        # rv_creator, rv_producer, rv_subtitle, rv_keywords, rv_reference_list, rv_reference_ctrl_set
            rv_fileMetadata, rv_subtitle, rv_keywords, rv_reference_list = ExtractDataFrom(
                startDirectory + pdfRepository + fileName, title, authors, summary)
            sql = ''' UPDATE arXive
            SET cFIRST_CAT = ? ,
            eSUBTITLE = ? ,
            eKEYWORDS = ? ,
            eREFERENCES = ? ,    
            ePDF_METADATA = ?,
            eLanguage = ?
            WHERE entry_id = ?'''

            res = identifier.classify(title + '. ' + summary)  # pour le cas ou summary est trop court // TODO EXPLIQUER

            langue = res[0] + '_' + str(int(100 * res[1]))
            data = (FirstCat, rv_subtitle, rv_keywords, repr(rv_reference_list),
                    repr(rv_fileMetadata), langue, entry_id)
            cur.execute(sql, data)  # TODO PRA ajouter un test avant sur un verrou sur la BDD !

    except Exception:  # TODO PRA etre plus explicite
        logger.error("file {} not extracted ".format(pdfRepository + fileName), exc_info=True)


        # records = cur.fetchall() # ??

    # extra data :

    # extraction from S2

    if (True  or  JSON is None or len(JSON)==0):
        res = identifier.classify(title + '. ' + summary)  # pour le cas ou summary est trop court // TODO EXPLIQUER
        langue = res[0] + '_' + str(int(100 * res[1]))


        paperLanguage.append(langue)
        paperToGet.append(str(entry_id))

        if len(paperToGet) == 2: # handle request

            papers = myGetPapers(paperToGet)
            try:
                #papers = []
                #p =sch.get_paper(paperToGet[0],['topics'])  # ,fields=['topics'])
                # print(paper)

                for paper in []:
                    d = simplifyS2Objetc(dict(paper))

                    JSON = json.dumps(d, default=str)
                    # TODO remettre le bon abstract
                    logger.info("file {} updated from S2 {}/{} ".format(str(entry_id), i, len(records)))
                    sql = ''' UPDATE arXive
                          SET JSON = ?,
                          cFIRST_CAT = ?,
                          eLanguage = ? 
                          WHERE entry_id = ?'''
                    data = (JSON, FirstCat, langue, entry_id)
                    cur.execute(sql, data)  # TODO PRA ajouter un test avant sur un verrou sur la BDD !

            except ObjectNotFoundExeception as inst:
                logger.error("file {} not found in S2 ".format(str(entry_id)), exc_info=False)
            except Exception as inst:
                logger.error("file {} error {} with S2 ".format(str(entry_id), inst.args), exc_info=False)

            paperLanguage.clear()
            paperToGet.clear()






cur.close()
con.commit()  # committe les transactions.
con.close()  # ferme la connection.



