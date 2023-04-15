La sémantisation est réalisée via un notebook. Il s'agit d'exploiter un export JSON de la base de données SQL pour construire le fichier RDF.

ExportJSON est utilisé pour produire ces fichiers à partir d'une base de données de 7.72 Go.

Un export est réalisé et disponible sur github pour pouvoir utiliser ce module.
Il conviendra de le décompresser à l'emplacement idoine (en fonction du chemin de settings).

Pour réduire la consommation mémoire, on peut :
* agir sur l'ExportJSON, dans la version actuelle seuls les fichiers en anglais avec cs.AI en première catégorie sont exportés;
* on peut également mettre allowTheSecondLevel à False pour ne pas générer le deuxième niveau (auteurs et publication tirés des biographies).


