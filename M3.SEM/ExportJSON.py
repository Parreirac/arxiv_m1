"""
Extrait de la base de données des fichiers JSON pour des imports MongoDB ou Neo4j
"""
import json
import logging
import sqlite3

import jsonlines

import settings

filenameDocs: str = "dbDocs.json"
filenameDocs2: str = "dbDocs2.json"
filenameAuthors: str = "dbAuthors.json"
filenameAuthors2: str = "dbAuthors2.json"
filenameAffiliations: str = "dbAffiliations.json"
filenameTopics: str = "dbTopics.json"
filenameFields: str = "dbFields.json"


# LIMIT a 15 permet d'avoir une affiliation ou un topic
sql_request: str = '''SELECT JSON, eLanguage, summary, tags,entry_id \
        from arXive where eLanguage like 'en_%' and cFIRST_CAT like '%cs.AI%' ''' # LIMIT 2000'''
logger = logging.getLogger()


def create_dict(string: str) -> dict[str, str] | None:
    if not string.startswith('{'):
        return None
    tab = string[1: len(string) - 1].split("'")

    return_value = {}
    for i in range(0, len(tab) - 1, 4):
        return_value[tab[i + 1]] = tab[i + 3]

    return return_value


def getS2Dict(obj):
    try:  # How to check whether this exists or not
        obj2 = obj.__dict__
        # Method exists and was used.
        obj3 = {}

        for cle, valeur in obj2.items():
            cle2 = cle
            if cle2[0] == '_':
                cle2 = cle2[1:]  # remove first character (_)
            obj3[cle2] = valeur

        return obj3

    except AttributeError:
        return None


def extractNumPages(_txt: str):
    """Chercher par le pdf, ou par les commentaires le nombre de pages"""



def create_list(string: str) -> list[str] | None:
    if not string.startswith('['):
        return None
    tab = string[1: len(string) - 1].split("'")

    return_value = []
    for ii in range(1, len(tab), 2):
        return_value.append(tab[ii])
    return return_value

def clearPaper(cdata: dict):
    cdata.pop('url', None)
    cdata.pop('intent', None)
    cdata.pop('isInfluential', None)

    value = cdata.get("authors", None)

    if value is not None and isinstance(value, list):
        l2 = []
        for i in value:
            l2.append(clearAuthor(i))
        cdata["authors"] = l2

    value = cdata.get("citations", None)
    if value is not None and isinstance(value, list):
        l2 = []
        for i in value:
            cit = clearPaper(i)
            cit.pop("abstract", None)
            l2.append(cit)
        data["citations"] = l2

    value = cdata.get("references", None)
    if value is not None and isinstance(value, list):
        l2 = []
        for i in value:
            ref = clearPaper(i)
            ref.pop("abstract", None)
            l2.append(ref)
        cdata["references"] = l2

    return cdata


def clearAuthor(data: dict):
    """Filtrage de certaines informations qui ne servent pas """
    aff = data.get('affiliations', None)
    if aff is None or len(aff) == 0:
        data.pop('affiliations', None)

    ids = data.get('externalIds', None)
    if ids is None or len(ids) == 0:
        data.pop('externalIds', None)
    hp = data.get('homepage', None)
    if hp is None or len(hp) == 0:
        data.pop('homepage', None)
    data.pop('paperCount', None)
    data.pop('papers', None)
    data.pop('url', None)
    return data


logger.info('Start !')
con = sqlite3.connect(settings.STARTDIRECTORY + settings.DATABASE)
cur = con.cursor()


cur.execute(sql_request)

records = cur.fetchall()
logger.debug("%s records to handle",(len(records)))

# last_request_dt = datetime.min  # .now()
# identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)


# First identifie first level (papers and authors) in order to get smaller files.
# and extrac data as topics or affiliation for the same reason


fieldsOfStudySet = set()
firstLevelPaperSet = set()
firstLevelAuthorSet = set()
topicsDict = {}
affilationsSet = set()
affiliations = []

with jsonlines.open(settings.STARTDIRECTORY + filenameDocs, 'w') as writer:
    # writer.write_all(items)
    # with open(startDirectory+filename, 'w') as f:
    # data = json.load(f)

    # Output: {'name': 'Bob', 'languages': ['English', 'French']}
    # print(data)
    # do the job
    i = 0
    for row in records:
        i = i + 1

        # if i> 100:
        #    break

        JSON = row[0]
        eLanguage = row[1]
        summary = row[2]
        tags = row[3]
        tags = create_list(tags)
        entry_id = row[4]
        if JSON is not None and len(JSON) > 2:
            data = json.loads(JSON)

            # update sets
            for tag in tags:
                fieldsOfStudySet.add(tag)

            paperId = data.get("paperId", None)
            firstLevelPaperSet.add(paperId)

            authors = data.get("authors", None)
            # print(entry_id)

            year = data["year"]
            for aut in authors:
                autId = aut.get("authorId", None)

                firstLevelAuthorSet.add(autId)
                aff = aut.get("affiliations", None)
                if aff is not None and len(aff) > 0:
                    for aff_name in aff:
                        # print(aff_name,year,autId,paperId)
                        affiliations.append([aff_name, year, autId, paperId])
                        affilationsSet.add(aff_name)

            # handle topics :
            topics = data.get("topics", None)

            if topics is not None and len(topics) > 0:
                for t in topics:
                    tId = t.get("topicId", None)
                    tName = t.get("topic", None)
                    topicsDict[tId] = tName

# Save Affiliations
with jsonlines.open(settings.STARTDIRECTORY + filenameAffiliations, 'w') as writer:
    logger.info("there are %s affiliations",(len(affilationsSet)))

    for aff in affilationsSet:
        # print (aff)
        d = {"Name": aff, "year": {}}
        for l in affiliations:
            if l[0] == aff:
                data = d.get("year", {})
                dataByYear = data.get(l[1], {})
                authors = dataByYear.get("authors", set())
                papers = dataByYear.get("papers", set())
                authors.add(l[2])
                papers.add(l[3])
                data[l[1]] = {"authors": authors, "papers": papers}
        d["year"] = data

        newdic = {}

        for k, v in d["year"].items():
            newdic[k] = {"authors": list(v["authors"]), "papers": list(v["papers"])}
        d["year"] = newdic

        writer.write(d)

# Save Topics
with jsonlines.open(settings.STARTDIRECTORY + filenameTopics, 'w') as writer:
    logger.info("there are %s topics",(len(topicsDict)))

    writer.write(topicsDict)

# Save fields
with jsonlines.open(settings.STARTDIRECTORY + filenameFields, 'w') as writer:
    logger.info("there are %s Fields",(len(fieldsOfStudySet)))

    writer.write(list(fieldsOfStudySet))

firstLevelAuthorDict = {}
secondLevelAuthorDict = {}

secondLevelPapersDict = {}

with jsonlines.open(settings.STARTDIRECTORY + filenameDocs, 'w') as writer:
    # writer.write_all(items)
    # with open(startDirectory+filename, 'w') as f:
    # data = json.load(f)

    # Output: {'name': 'Bob', 'languages': ['English', 'French']}
    # print(data)
    # do the job
    i = 0
    for row in records:
        i = i + 1

        # if i> 100:
        #    break

        JSON = row[0]
        eLanguage = row[1]
        summary = row[2]
        tags = row[3]
        tags = create_list(tags)
        entry_id = row[4]
        if JSON is not None and len(JSON) > 2:
            data = json.loads(JSON)

            data = clearPaper(data)
            # add fieldsOfStudy from arXiv metadata
            data["fieldsOfStudy"] = tags
            # add fieldsOfStudy from arXiv metadata
            data["abstract"] = summary
            # add Language from arXiv metadata
            data["Language"] = eLanguage[:2]
            data["LanguageProbability"] = int(eLanguage[3:])

            authors = data.get("authors", None)
            listAuthors = []
            year = data["year"]
            for aut in authors:
                autId = aut.get("authorId", None)

                if firstLevelAuthorDict.get(autId, None) is None:
                    firstLevelAuthorDict[autId] = aut

                listAuthors.append(autId)
                aff = aut.get("affiliations", None)
                if aff is not None and len(aff) > 0:
                    for aff_name in aff:
                        # print(aff_name,year,autId,paperId)
                        affiliations.append([aff_name, year, autId, paperId])
                        affilationsSet.add(aff_name)

            data["authors"] = listAuthors

            # handle topics :
            topics = data.get("topics", None)
            newTopicsList = []
            if topics is not None and len(topics) > 0:
                for t in topics:
                    tId = t.get("topicId", None)
                    tName = t.get("topic", None)
                    topicsDict[tId] = tName
                    newTopicsList.append(tId)
            if len(newTopicsList) > 0:
                data["topics"] = newTopicsList

            # references
            references = data.get("references", [])

            newReferences = []
            for r in references:
                rId = r["paperId"]
                newReferences.append(rId)
                if rId not in firstLevelPaperSet:
                    secondLevelPapersDict[rId] = r
            data["references"] = newReferences

            # citations
            citations = data.get("citations", [])

            newCitations = []
            for r in citations:
                rId = r["paperId"]
                newCitations.append(rId)
                if rId not in firstLevelPaperSet:
                    secondLevelPapersDict[rId] = r
            data["citations"] = newCitations

            # clearedPaper = clearPaper(data)
            # print(clearedPaper)
            writer.write(data)

            logger.info("save %s/%s ",i, len(records))
            # break
cur.close()
# con.commit()  # committe les transactions.
con.close()  # ferme la connection.

# create first level authors
with jsonlines.open(settings.STARTDIRECTORY + filenameAuthors, 'w') as writer:
    logger.info("there are %s first level authors",(len(firstLevelAuthorDict)))

    for k, v in firstLevelAuthorDict.items():
        if v.get("aliases", None) is None:
            v.pop("aliases", None)
        writer.write(v)

# create second level papers
#secondLevelPapersDict = {}

with jsonlines.open(settings.STARTDIRECTORY + filenameDocs2, 'w') as writer:
    logger.info("there are %s second level documents",(len(secondLevelPapersDict)))

    for k, v in secondLevelPapersDict.items():
        # ~~~~
        listAuthors = []
        authors = v.get("authors", [])
        for aut in authors:
            autId = aut.get("authorId", None)
            if autId not in firstLevelAuthorSet:
                secondLevelAuthorDict[autId] = aut
            listAuthors.append(autId)
        v["authors"] = listAuthors

        if v.get("arxivId", None) is None:
            v.pop("arxivId", None)
        # ~~~~

        writer.write(v)

# create second level authors
with jsonlines.open(settings.STARTDIRECTORY + filenameAuthors2, 'w') as writer:
    logger.info("there are %s second level authors",(len(secondLevelAuthorDict)))

    for k, v in secondLevelAuthorDict.items():
        writer.write(v)
