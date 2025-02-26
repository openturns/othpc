# Etude paramétrique avec le cas de la poutre encastrée

## Introduction
Les scripts Python présentés ici permettent de réaliser une étude paramétrique
avec le modèle de poutre encastrée. 
Le plan d'expériences est réalisé avec OpenTURNS, sur la base d'un échantillon 
Monte-Carlo simple.
La méthode de parallélisation est fondé sur la commande `jobarray` 
de l'outil SLURM.

Cette méthode est adaptée de celle utilisée dans le contexte du code LEGOS.

## Principe
La méthode est décomposée en trois parties :
- préparation de l'étude paramétrique (écrit le plan d'expériences
  en entrée sur le disque) avec le script `runParametricBeam.py`,
- exécution de l'étude paramétrique avec `sbatch` avec le 
  script `lance_jobs.sh`,
- rassemblement des résultats locaux (écrit les valeurs de 
  sortie du modèle sur le disque) avec le script `runGatherResultsBeam.py`.

### Création de l'étude paramétrique
De manière plus détaillée, la préparation de l'étude paramétrique
réalisée dans le script `runParametricBeam.py` est réalisée ainsi :
- crée un sous-répertoire `work` du répertoire `/scratch/users/C61371/beam` :
  les répertoires de calcul seront des sous-répertoires de ce répertoire principal,
- crée un plan d'expériences avec OpenTURNS,
- génère les répertoires d'étude locaux en Python,
- dans chaque répertoire local, copie les fichiers
  nécessaires au cas de la poutre encastrée : l'exécutable `beam`, 
  le fichier d'entrée `beam.xml`,
- génère le script `lance_jobs.sh` en tenant compte du nombre 
  de points dans le plan d'expériences.

Dans chaque répertoire de calcul, le fichier `beam.xml`
est créé à partir du fichier `beam_input_template.xml`.
Cela est réalisé par substitution des balises par des valeurs 
grâce au module `coupling_tools`.

Le script `runParametricLegos.py` génère l'arborescence de répertoires 
suivants :
```
/scratch/users/C61371/beam/work
|
+ 1
|
+ 2
...
|
+ n
```
où n est la taille de l'échantillon.
A l'issue de l'exécution de ce script, deux fichiers sont générés dans le répertoire 
`/scratch/users/C61371/beam/work` :
- `input.csv` : le plan d'expérience en entrée du modèle de la poutre encastrée,
- `lance_jobs.sh` : le script `Bash` placé en argument de la commande `sbatch`.

### Evaluation du plan d'expériences avec sbatch
Lorsqu'on utilise une taille d'échantillon égale à 10,
on obtient le fichier `lance_jobs.sh` suivant :
```
#!/bin/bash
#SBATCH --job-name=myJobarrayTest
#SBATCH --nodes=1 --ntasks=1
#SBATCH --time=4:00:00
#SBATCH --output=test_%A_%a.out
#SBATCH --error=test_%A_%a.err
#SBATCH --partition=cn
#SBATCH --array=1-10
#SBATCH --wckey=P11YB:ASTER

cd /scratch/users/C61372/beam/work/$SLURM_ARRAY_TASK_ID
./beam -x beam.xml
```

On observe que ce script commence par aller dans le répertoire 
`/scratch/users/C61372/beam/work/$SLURM_ARRAY_TASK_ID` où 
`SLURM_ARRAY_TASK_ID` est l'indice du calcul dans la liste des 
entiers entre 1 et 10.
Puis, la commande exécute l'exécutable `beam` avec comme argument 
d'entrée le fichier `beam.xml` spécifique pour ce point particulier
du plan d'expériences.

### Collecte des résultats
Le rassemblement des résultats de sortie est réalisé avec le script
`runGatherResultsBeam.py`.
Pour chaque répertoire local de simulation, le script lit 
le fichier `_beam_outputs_.xml`.
Puis il utilise `coupling_tools` pour extraire la valeur de la déviation.
A la fin, le fichier `output.csv` est généré, contenant la valeur 
de la sortie y correspondant à chaque point du plan d'expériences.

## Tutoriel
La création du plan d'expériences est réalisée par la commande :
```
python3 runParametricBeam.py
```
L'éxécution du script précédent produit l'affichage suivant :
```
$ python3 runParametricBeam.py 
1. Set the probabilistic model
2. Generate the design of experiments
Création de tous les répertoires d'où vont être lancés les jobs
Création répertoire #1 / 10
Create /scratch/users/C61372/beam/work/1
Create beam.xml
Copy beam into /scratch/users/C61372/beam/work/1
Copy beam.xml into /scratch/users/C61372/beam/work/1
Création répertoire #2 / 10
[...]
Création répertoire #10 / 10
Create /scratch/users/C61372/beam/work/10
Create beam.xml
Copy beam into /scratch/users/C61372/beam/work/10
Copy beam.xml into /scratch/users/C61372/beam/work/10
Write input data into /scratch/users/C61372/beam/work/input.csv
Write the jobarray/SLURM bash script /scratch/users/C61372/beam/work/lance_jobs.sh
```

La suite de l'étude consiste à lancer le script `lance_jobs.sh` avec `sbatch`:
```
sbatch /scratch/users/C61372/beam/work/lance_jobs.sh
```

Enfin, on peut rassembler les résultats générés dans les répertoires de 
simulation avec le script `runGatherResultsBeam.py` :
```
python3 runGatherResultsBeam.py
```
L'éxécution du script précédent produit l'affichage suivant :
```
Number of jobs = 10
Current directory /scratch/users/C61372/beam/work/1
Current directory /scratch/users/C61372/beam/work/2
[...]
Current directory /scratch/users/C61372/beam/work/9
Write output data into /scratch/users/C61372/beam/work/output.csv
```


