# Description
M1 est le module de creation d'une base SQL contenant une description des articles intelligence artificielle d'arXiv. 
Il contient :
  * un notebook qui décrit comment télécharger (en python) un article, comment en lire le texte. Tesseract est également utilisé. (Avec un emploi sous google colab il n'y a aucune installation à faire en local.)
    L'objectif de ce notebook est de montrer que le résultat de l'extraction du texte est très variable. (Ce n'est pas flagrant dans l'exemple 1 utilisé.)
  * un ensemble de code python pour initialiser une base, l'enrichir avec le contenu des pdf téléchargés.

Mais pour disposer d'un résultat exploitable c'est par utilisation de l'API de semantic scholar que la base est complétée.

# Contenu des fichiers python
  * advancedArXivSearch permet la création du BDD SQLite qui contient l'ensemble des informations (métadonnées arXiv). Ce code utilise l'url "https://arxiv.org/search/advanced" qui permet de spécifier une période dans la recherche des articles. Cela permet de faire une requête qui a plus de 10 000 réponses. Le téléchargement de l'ensemble des informations (or PDF) se fait en 3 nuits ;
  * EnrichDB télécharge les PDF et les exploite pour enrichir la BDD locale ; 
  * ExtracDataFromPDF pour extraire des informations (actuellement mots-clés, références, métadonnées du fichier) du PDF ;
  * MyPyPDF2 et MyStringSearch sont des surcharges de PyPDF2 ;
  * EnrichDBFromS2 utilise l'api de semantic scholar pour extraire les informations des pdf. (Bibliographie et citation, affiliation et topics) ;
