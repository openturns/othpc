Ce répertoire contient des cas d'utilisation du module `otcluster`. Dans ce document, nous présentons les fichiers présentés dans le répertoire.

De manière générale, les deux scripts les plus importants de ce répertoire sont les suivants :
- `demo_SLURM_beam.py` : Une démonstration de l'évaluation sur cluster du cas de la poutre encastrée.
- `demo_SLURM_beam_submit_and_gather.py` : Une démonstration de l'évaluation par découpage en soumission puis collecte.

## Cas de la poutre encastrée
Une première série de fichiers permet de définir le cas de la poutre encastrée.

- `BeamFunction.py` : implémente la classe BeamFunction
- `beam` : un exécutable du cas de la poutre encastrée pour Linux
- `beam.c` : le code source en langage C
- `beam.exe` : un exécutable du cas de la poutre encastrée pour Windows
- `beam_input_template.xml` : le fichier d'entrée modèle de la poutre encastrée. Ce fichier subit les substitutions des balises par des valeurs numériques pour devenir le fichier d'entrée "beam.xml".
- `demo_beam.py` : démonstration de l'utilisation de la poutre encastrée avec évaluation locale.
- `demo_beam_inside_directory.py` : démonstration de la classe `FunctionInsideDirectory` sur la poutre encastrée. L'objectif de cette classe est de fournir un service permettant d'étanchéifier les calculs nécessitant la mise en oeuvre de fichiers intermédiaires. Cette classe est une maquette qui n'est pas achevée.

## Démonstrations d'évaluation locale
- `demo_MemoizeWithCSVFile.py` : Démonstration de la classe `MemoizeWithCSVFile`. Cette classe fournit un mécanisme de cache fondé sur une paire de fichiers CSV.
- `demo_OpenTURNSPythonFunction.py` : Une démonstration de la classe `OpenTURNSPythonFunction` dans le cas Ishigami avec évaluation simple et évaluation vectorisée. Il est destiné au lecteur qui n'est pas nécessairement familier de cette classe.

## Démonstration d'évaluation sur cluster avec SLURM
- `demo_SLURM_beam.py` : A demonstration of the SLURMJobArrayFunction class on the beam example. La sortie de ce script est disponible dans le fichier `test.output.txt`. C'est le script le plus important du répertoire.
- `demo_SLURM_beam_submit_and_gather.py` : A demonstration of the SLURMJobArrayMachine class on the beam  example: 1. Submit the job (connect), 2. Disconnect the computer, 3. Wait and gather the results. C'est le second script le plus important du répertoire.
- `demo_SLURM_beam_algorithm.py` : A demonstration of the SLURMJobArrayFunction on the beam example, within an OpenTURNS algorithm. The chosen algorithm is ExpectationSimulationAlgorithm. 
- `demo_SLURM_flood_fail.py` : A demonstration of the SLURMJobArrayFunction class on the flood model. Uses a version of the flooding model which fails half of the times. C'est une pièce importante pour montrer ce qui arrive pour un code qui plante fréquemment.
- `demo_SLURM_ishigami.py` : Use SLURMJobArrayFunction on a symbolic function. C'est une pièce importante de l'étude qui permet de montrer que la classe peut être utilisée dans un contexte où il n'y a pas de binaire à exécuter ou de répertoire à créer.
- `demo_SLURM_beam_blocksize.py` : A demonstration of the SLURMJobArrayFunction class on the beam example. Divide sample into blocks of size block_size. May improve performance if the file exchange penalty is large. May overcome the maximum number of jobs (500) limitation.
- `demo_SLURM_beam_cache.py` : A demonstration of the SLURMJobArrayFunction class on the beam example with the MemoizeWithCSVFile. The model is evaluated pointwise. This allows to use a intput/output cache file pair. Hence, if the job does not go to its end (e.g. if the time is limited), then it suffices to re-run the sbatch command. In this case, if any point has already been evaluated inside a  local simulation directory, then the evaluation will be instantaneous.
- `demo_SLURM_beam_evaluate_experiment.py` : A demonstration of the SLURMJobArrayFunction class on the beam  example. Evaluates the DoE available in "input_doe.csv".

## Démonstration d'évaluation sur cluster avec Dask
- `demo_dask_beam.py` : A demonstration of the DaskFunction on the beam example. Ce script n'est pas abouti à ce jour.

## Autres fichiers
- `input_doe.csv` : Un fichier CSV fourni par un collègue et contenant un plan d'expériences. Notre travail consiste à évaluer ce plan d'expériences sur cluster. Cela est réalisé par le script `demo_SLURM_beam_evaluate_experiment.py`. C'est une pièce importante de l'étude car elle montre comment procéder dans ce contexte.

## Scripts de support pour l'étude
- `jobqueue.yaml` : Paramètres de configuration du cluster. Ils sont récupérés depuis le fichier "jobqueue.yaml" placé dans le home : "~/.config/dask". La documentation Dask recommande de placer ce fichier dans un dossier "/etc/dask" pour qu'il soit commun à tous les utilisateurs du cluster.
- `run-examples.sh` : Exécute tous les scripts Python du répertoire. Ce script sert à vérifier que les démonstrations fournies sont fonctionnelles.

## Fichiers générés par les scripts
- `test.output.txt` : Ce qui est affiché dans le terminal lorsqu'on exécute le script demo_SLURM_beam.py.
