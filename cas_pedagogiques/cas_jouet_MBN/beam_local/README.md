# Modèle de poutre encastrée fondé sur un binaire

Ce répertoire contient un exemple de poutre encastrée fondé sur l'évaluation d'un binaire et une communication par échange de fichiers.

## Exemple
Pour exécuter ce modèle, il est nécessaire que le binaire soit exécutable.

Le binaire `beam` est un binaire Linux. Celui-ci doit être exécutable.

```bash
chmod u+x beam
```
De même, l'exécutable `beam.exe` est un binaire Windows. 
Pour le rendre exécutable, il faut modifier ses propriétés, par exemple 
avec le gestionnaire de fichiers Windows.

Pour exécuter la démonstration, on peut faire ceci.
```bash
python3 demo_beam.py
```
Le script génère un échantillon d'entrée, évalue la fonction sur chacun des points de l'échantillon puis affiche l'échantillon de sortie.
```
$ python3 demo_beam.py 
Test the BeamFunction
Create X sample
X = 
    [ E             F             L             I             ]
0 : [   6.78712e+10 263.092         2.53306       1.55122e-07 ]
1 : [   6.50254e+10 309.118         2.53613       1.56701e-07 ]
2 : [   6.83691e+10 323.088         2.5319        1.47726e-07 ]
3 : [   6.50185e+10 262.654         2.50948       1.46362e-07 ]
4 : [   6.88439e+10 294.387         2.52877       1.49355e-07 ]
5 : [   6.72234e+10 312.085         2.51496       1.40294e-07 ]
6 : [   6.75567e+10 294.798         2.56374       1.5807e-07  ]
7 : [   6.67157e+10 276.128         2.52353       1.4422e-07  ]
8 : [   6.50716e+10 310.705         2.59143       1.50531e-07 ]
9 : [   6.81962e+10 297.215         2.57052       1.46323e-07 ]
Convert model into Function
Compute Y
Execute beam at [6.78712e+10,263.092,2.53306,1.55122e-07]
From /home/C61372/GITLAB/hpc/cas_pedagogiques/cas_jouet_MBN/beam_local/beam_input_template.xml, write beam.xml
Execute: ""/home/C61372/GITLAB/hpc/cas_pedagogiques/cas_jouet_MBN/beam_local/beam" -x beam.xml"
Read _beam_outputs_.xml
Y = 0.135382987
Execute beam at [6.50254e+10,309.118,2.53613,1.56701e-07]
[...]
Y = 0.1686315465
Y = 
    [ Deviation ]
0 : [ 0.135383  ]
1 : [ 0.164954  ]
2 : [ 0.173071  ]
3 : [ 0.145394  ]
4 : [ 0.154326  ]
5 : [ 0.175463  ]
6 : [ 0.155062  ]
7 : [ 0.15373   ]
8 : [ 0.184005  ]
9 : [ 0.168632  ]

```
