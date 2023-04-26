Ce répertoire contient les éléments sur AWS, terraform, et la conteneurisation.

A cette heure, les services AWS sont évalués dans un notebook jupyter. Pour comparaison :
* en M1, un notebook réalise l'extraction du texte d'un PDF par du code (PyPDF2) et par OCR avec Tesseract de google.
Les résultats sont consultables via https://github.com/Parreirac/arxiv_m1/blob/master/M1.Extract/PFR_1.ipynb ;
* en M2, un notebook réalise la NER via spaCy (voir https://github.com/Parreirac/arxiv_m1/blob/master/M2.NLP/PFR_2_NER_spaCy.ipynb). Mais les résultats sont moins bons qu'avec AWS.

Un déploiement terraform d'une BDD Neo4j est en cours.

La conteneurisation a été réalisée sur le module M0. Le README.md a été modifié pour indiquer la procédure afférente. 