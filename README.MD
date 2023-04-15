Ce repository (https://github.com/Parreirac/arxiv_m1.git) décrit les livrables du projet fil rouge (sauf le rapport).
Les repertoires correspondent aux différents modules, sauf :
* M0 qui décrit le programme réalisé dans le cadre de l'évaluation python
* AWS qui décrit les éléments liés au module AWS, IAC, conteneurisation.

Certains travaux ont été réalisés vie jupyter notebook.
Sauf pour le module AWS, ils peuvent s'exécuter avec google colab.
(il convient de placer ces fichiers dans son drive google, ainsi que les éventuels fichiers de données au même niveau. Aucune installation n'est nécessaire.)
Sinon, ils peuvent être consultés via le github au lien https://github.com/Parreirac/arxiv_m1.
Malheureusement, dans le cas du notebook de topic modeling, les résultats du SDK LDAvis (pour visualiser un modèle LDA) sont perdu. Le notebook doit être relancé, or il nécessite un temps de calcul de plus de 5h.

Le fichier settings définit quelques variables globales, dont les chemins d'accès.