# Généralité 

Ce repository (https://github.com/Parreirac/arxiv_m1.git) décrit les livrables du projet fil rouge (sauf le rapport).
Les repertoires correspondent aux différents modules, sauf :
* M0 qui décrit le programme réalisé dans le cadre de l'évaluation python
* AWS qui décrit les éléments liés aux modules AWS-IAC, conteneurisation.

Certains travaux ont été réalisés vie jupyter notebook.
Sauf pour le module AWS, ils peuvent s'exécuter avec google colab.
(il convient de placer ces fichiers dans son drive google, ainsi que les éventuels fichiers de données au même niveau. Aucune installation n'est nécessaire.)
Sinon, ils peuvent être consultés via le github au lien https://github.com/Parreirac/arxiv_m1.
Malheureusement, dans le cas du notebook de topic modeling, les résultats du SDK LDAvis (pour visualiser un modèle LDA) sont perdu. Le notebook doit être relancé, or il nécessite un temps de calcul de plus de 5h.


# Contenu 
Le fichier settings définit quelques variables globales, dont les chemins d'accès de la BDD, son nom. Le sous-répertoire pour les PDF est également précisé.

* M0 est le livrable pour l'évaluation python. Il est maintenant déployable via docker ;
* M1 est le module de creation d'une base SQL contenant une description des articles intelligence artificielle d'arXiv. Il contient :
  * un notebook qui décrit comment télécharger (en python) un article, comment en lire le texte. Tesseract est également utilisé. (Avec un emploi sous google colab il n'y a aucune installation à faire en local)
  * advancedArXivSearch permet la création du BDD SQLite qui contient l'ensemble des informations (métadonnées arXiv). Ce code utilise l'url "https://arxiv.org/search/advanced" qui permet de spécifier une periode dans la recherche des articles. Cela permet de faire une requête qui a plus de 10 000 réponses. Le téléchargement de l'ensemble des informations (or PDF) se fait en 3 nuits ;
  * EnrichDB télécharge les PDF et les exploite pour enrichir la BDD locale ; 
  * ExtracDataFromPDF pour extraire des informations (actuellement mots-clés, références, métadonnées du fichiers) du PDF ;
  * MyPyPDF2 et MyStringSearch sont des surcharges de PyPDF2 ;
  * EnrichDBFromS2 utilise l'api de semantic scholar pour extraire les informations des pdf. (Bibliographie et citation, affiliation et topics) ;
* M2 explore par deux notebook deux tâches de NLP : la reconnaissance d'entités nommées (avec spaCy) et le topic modeling (avec GENSIM). Attention le topic modeling nécessite plusieurs heures de calcul ;
* M3 produit le fichier RDF d'ensemble des données sémantisées. C'est un notebook utilisant OWLREADY2
* M4 est le module d'exploitation, soit via SPARQL (avec un notebook) soit via Neo4j. 

# Modifications

* 15 avril 23 : 
  * enrichissement de ce readme
  * nombreuses modifications de nettoyage du code
  * correction d'une erreur avec git qui avait écrasé des modifications de ExtractDataFromPDF.py
  * correction suite aux tests sous linux ;
  * ajout du fichier de données pour le notebook de NER





