# Quantification des incertitudes avec le cas de la poutre encastrée

## Introduction
Les scripts Python présentés ici permettent de réaliser une étude paramétrique avec le modèle de poutre encastrée. Le plan d'expériences est réalisé avec OpenTURNS, sur la base d'un échantillon Monte-Carlo simple. La méthode de parallélisation est fondé sur la commande `jobarray` de l'outil SLURM. La méthode consiste à définir une fonction (une `ot.Function`) implémentant le couplage, puis à évaluer cette fonction en parallèle sur plusieurs noeuds de calcul.

## Principe
La méthode est décomposée en deux parties :
- l'utilisateur doit d'abord définir une instance de la classe `Function` implémentant l'évaluation de la fonction ;
- on peut ensuite créer une instance de la classe `SLURMJobArrayFunction` qui permet d'évaluer la fonction avec SLURM.

Dans le cas de la poutre encastrée, on peut créer un modèle de poutre avec la classe `BeamFunction`.

## Description des répertoires
- `otcluster` : Le module otcluster qui implémente les classes utilisées dans les exemples.
- `examples` : Les exemples d'utilisation.

## Cas d'usage
Dans la suite, nous présentons plusieurs cas d'usage.
- Dans le cas le plus simple, on évalue un plan d'expériences sur cluster directement dans un seul script. Si besoin, les calculs sont temporairement sauvegardé dans une paire de fichiers CSV contenant les entrées et les sorties, ce qui peut permettre d'ajouter des points si besoin.
- La fonction d'étude évaluée sur cluster est mise en oeuvre dans le contexte d'un algorithme de simulation itératif qui estime l'espérance de la sortie du modèle.
- L'évaluation du plan d'expériences est réalisée en deux parties : 1) la création de l'étude paramétrique et la soumission du job, 2) l'attente des résultats et la collecte des sorties.
- Le code plante pour certaines valeurs des entrées.

Ces scénarios sont présentés dans la suite du texte.

## Scénario 1 : Evaluation d'un plan d'expériences sur cluster
### Evaluation du plan d'expériences
Le script suivant présente un cas d'usage simple de la classe `SLURMJobArrayFunction.py`. Il est disponible dans le fichier `examples/demo_SLURM_beam.py`. Ce script présente un scénario d'utilisation simple de la classe, dans lequel l'échantillon de sortie est directement calculé en fonction de l'échantillon d'entrée.

Nous commençons par définir le modèle de poutre encastrée :
```python
beamModel = BeamFunction()
model = ot.Function(beamModel)
```
Puis nous créons le modèle probabiliste et générons un échantillon de taille 10 du vecteur aléatoire X en entrée du modèle.
```python
X_distribution = beamModel.getInputDistribution()
sampleSize = 10
X = X_distribution.getSample(sampleSize)
```
Enfin, nous évaluons le modèle en parallèle grâce à SLURM.
```python
cwd = os.getcwd()
sbatch_wckey = "P120F:PYTHON"
user_resources = [
    os.path.join(cwd, "beam_input_template.xml"),
    os.path.join(cwd, "BeamFunction.py"),
    os.path.join(cwd, "beam"),
]
base_directory = os.getcwd()
sbatch_extra_options = (
    '--output="logs/output.log" '
    '--error="logs/error.log" '
    "--nodes=1 "
    "--cpus-per-task=1 "
    "--mem=512 "
    '--time="00:05:00"'
)
slurm_wrapper = SLURMJobArrayFunction(
    model,
    sbatch_wckey,
    user_resources=user_resources,
    base_directory=base_directory,
    sbatch_extra_options=sbatch_extra_options,
    verbose=True,
)
slurm_function = ot.Function(slurm_wrapper)
Y = slurm_function(X)
```

Dans le code précédent, les instructions `model = ot.Function(beamModel)` et `slurm_function = ot.Function(slurm_wrapper)` ne sont pas strictement nécessaires. Leur intérêt est de montrer que les objets créés peuvent être convertis en objets `ot.Function`, ce qui permet à OpenTURNS d'utiliser ces fonctions au même titre que tout autre fonction. En conséquent, on peut utiliser toutes les méthodes de la classe `ot.Function` ou encore l'utiliser comme argument d'entrée d'un algorithme OpenTURNS comme `ExpectationSimulationAlgorithm`.

Le script précédent produit l'affichage suivant.
```
Create beam model
Case 1 : Define SLURM function (no cache)
Create /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18
Evaluate model
Create directory =  /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_0
Create local DOE = /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_0/14-10-2024_21-18_input_point.csv
Write the Python evaluation script /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_0/14-10-2024_21-18_localSLURMEvaluationFromStudy.py
Copy resources into /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_0
Copy file /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/beam_input_template.xml to /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_0
Copy file /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/BeamFunction.py to /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_0
Copy file /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/beam to /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_0
[...]
Create directory =  /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_9
Create local DOE = /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_9/14-10-2024_21-18_input_point.csv
Write the Python evaluation script /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_9/14-10-2024_21-18_localSLURMEvaluationFromStudy.py
Copy resources into /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_9
Copy file /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/beam_input_template.xml to /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_9
Copy file /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/BeamFunction.py to /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_9
Copy file /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/beam to /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_9
Write the jobarray/SLURM bash script /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/14-10-2024_21-18_jobarray_launcher.sh
Execute sbatch --output="logs/output.log" --error="logs/error.log" --nodes=1 --cpus-per-task=1 --mem=512 --time="00:05:00" /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/14-10-2024_21-18_jobarray_launcher.sh
Submitted batch job 46588484
Wait for results after 0
Wait for results after 1.0
Wait for results after 2.0
Wait for results after 3.0
Read /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_0/14-10-2024_21-18_output_point.csv
Read /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_1/14-10-2024_21-18_output_point.csv
Read /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_2/14-10-2024_21-18_output_point.csv
Read /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_3/14-10-2024_21-18_output_point.csv
Read /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_4/14-10-2024_21-18_output_point.csv
Read /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_5/14-10-2024_21-18_output_point.csv
Read /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_6/14-10-2024_21-18_output_point.csv
Read /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_7/14-10-2024_21-18_output_point.csv
Read /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_8/14-10-2024_21-18_output_point.csv
Read /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/simulation_9/14-10-2024_21-18_output_point.csv
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
Save cache on disk
```

### Sauvegarde des calculs dans la mémoire cache
Dans certains contextes et en particulier lorsque le coût d'évaluation est élevé, il peut être commode de sauvegarder les calculs dans un fichier, pour les réutiliser si besoin. Il est facile de le faire en utilisant la méthode `ot.Sample.exportToCSVFile`. De surcroît, il peut être utile d'augmenter la taille de l'échantillon sans toutefois ré-évaluer les points déjà disponibles. Cela peut être utile dans le cas où certaines évaluations ont échoué, par exemple si la durée d'évaluation a dépassé la durée limite. Dans ce contexte, on peut utiliser la classe `MemoizeWithFile`, dont nous présentons un exemple ci-dessous.
```python
# Step 1: Set X and Y
X = [...]
Y = [...]
# Save cache on disk
input_cache_filename = "input_cache.csv"
output_cache_filename = "output_cache.csv"
X.setDescription(slurm_wrapper.getInputDescription())
X.exportToCSVFile(input_cache_filename)
Y.setDescription(slurm_wrapper.getOutputDescription())
Y.exportToCSVFile(output_cache_filename)

# Step 2: Define SLURM function class (with cache)
slurm_wrapper_with_cache = MemoizeWithFile(
    slurm_function, input_cache_filename, output_cache_filename
)
slurm_wrapper_with_cache.load_cache()
Y = slurm_wrapper_with_cache(X)  # This should be instantaneous
slurm_wrapper_with_cache.save_cache()
```

## Scénario 2 : Utilisation  d'une fonction SLURMJobArrayFunction dans un algorithme
Toute instance de la classe `SLURMJobArrayFunction` peut être convertie en `ot.Function`. Cela permet d'utiliser une telle fonction au même titre que toute autre fonction dans la librairie. L'exemple suivant montre comment utiliser la classe `ExpectationSimulationAlgorithm` pour estimer la moyenne de la sortie du modèle de poutre encastrée. Dans ce contexte, la taille du bloc peut être égale, par exemple, aux nombre de jobs utilisé pour chaque bloc généré par la classe `ExpectationSimulationAlgorithm`.

```python
slurm_wrapper = SLURMJobArrayFunction(
    model,
    sbatch_wckey,
    user_resources=user_resources,
    base_directory=base_directory,
    sbatch_extra_options=sbatch_extra_options,
    verbose=False,
)
slurm_function = ot.Function(slurm_wrapper)
inputRandomVector = ot.RandomVector(X_distribution)
outputRandomVector = ot.CompositeRandomVector(slurm_function, inputRandomVector)
algo = ot.ExpectationSimulationAlgorithm(outputRandomVector)
algo.setMaximumOuterSampling(100)
algo.setBlockSize(20)  # The number of nodes/CPUs we usually have.
algo.setMaximumCoefficientOfVariation(0.01)  # 1% C.O.V.
def report_progress(progress):
    sys.stderr.write('-- progress=' + str(progress) + '%\n')
algo.setProgressCallback(report_progress)
algo.run()
result = algo.getResult()
expectation = result.getExpectationEstimate()
print(f"Expectation = {expectation[0]}")
expectationDistribution = result.getExpectationDistribution()
alpha = 0.95
interval = expectationDistribution.computeBilateralConfidenceInterval(alpha)
print(f"interval = {interval}")
```

## Scénario 3 : Soumission puis collecte
Il peut arriver que l'évaluation du plan d'expériences soit longue ce qui peut mener à une utilisation peu pratique des scripts précédents. En effet, ceux-ci font l'hypothèse que l'utilisateur évalue le script grâce à la commande `bash` suivante :
```bash
$ python3 demo_SLURM_beam.py
```
Puis l'utilisateur attend que l'intégralité du plan d'expériences soit évaluée puis écrite sur le disque. Cette étape peut durer plusieurs heures dans certains cas. En conséquence, le terminal Linux doit rester ouvert pendant l'intégralité de la période temporelle, ce qui n'est pas toujours facile ou possible. 
C'est la raison pour laquelle il est parfois plus facile de procéder de la manière suivante :
1. création de l'étude paramétrique (et des répertoires de travail intermédiaires) et soumission du job,
2. déconnexion,
3. attente de la disponibilité des résultats, puis collecte des données dans les répertoires.

Ce cas d'usage est présenté dans le script `demo_SLURM_beam_submit_and_gather.py`. Ce script rassemble les 3 étapes dans un unique script pour plus de commodité pour la démonstration, mais le script est découpé en deux scripts distincts dans les cas d'usage industriels, nommés `submit.py` et `gather.py`.

La première partie du script permet de créer une instance de la classe `SLURMJobArrayMachine`. Cette classe est construite sur la base des paramètres d'évaluation sur cluster comme la WcKey, le nom du répertoire de base, etc. La classe dispose d'une méthode `create(X)` qui crée l'étude paramétrique. Cela consiste à créer une collection de sous-répertoires contenant chaque sous-échantillon de l'échantillon d'entrée contenu dans la variable `X`.  Cette méthode retourne un objet `job` qui est par la suite sauvegardée sur le disque dans un fichier `Pickle`. La méthode `submit()` permet de créer le fichier de commandes `sbatch` et retourne la commande Bash exécutée pour soumettre le calcul sur cluster.
```python
# Create beam model
print("+ Create beam model")
cwd = os.getcwd()
input_template_filename = os.path.join(
    cwd, "beam_input_template.xml"
)  # This file is in the current directory (not copied)
beam_executable = os.path.join(
    cwd, "beam"
)  # This file is in the current directory (not copied)
beamModel = BeamFunction(input_template_filename, beam_executable)
X_distribution = beamModel.getInputDistribution()

# Input sample
sampleSize = 10
X = X_distribution.getSample(sampleSize)

# Define SLURM function (no cache)
print("+ Define SLURM function (no cache)")
model = ot.Function(beamModel)
sbatch_wckey = "P120F:PYTHON"
user_resources = [
    os.path.join(cwd, "BeamFunction.py"),
]

# base_directory = "/scratch/users/C61372/beam"
base_directory = os.getcwd()
sbatch_extra_options = (
    '--output="logs/output.log" '
    '--error="logs/error.log" '
    "--nodes=1 "
    "--cpus-per-task=1 "
    "--mem=512 "
    '--time="00:05:00"'
)

# Part 1: launch job, and disconnect
slurm_machine = otcluster.SLURMJobArrayMachine(
    model,
    sbatch_wckey,
    user_resources=user_resources,
    base_directory=base_directory,
    sbatch_extra_options=sbatch_extra_options,
    verbose=True,
)
print("slurm_machine = ")
print(slurm_machine)
job = slurm_machine.create(X)
command = slurm_machine.submit()
print(f"command = {command}")

# Save job on disk
with open("job.pkl", "wb") as f:
    pickle.dump(job, f)
```
Dans ce contexte, la session de travail de l'utilisateur est la suivante.
```bash
$ python3 submit.py
Create beam model
Create directory ...
...
Write the jobarray/SLURM bash script /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/14-10-2024_21-18_jobarray_launcher.sh
Execute sbatch --output="logs/output.log" --error="logs/error.log" --nodes=1 --cpus-per-task=1 --mem=512 --time="00:05:00" /fscronos/home/C61372/hpc/cas_pedagogiques/cas_jouet_MBN/beam_with_ot/work_14-10-2024_21-18/14-10-2024_21-18_jobarray_launcher.sh
Submitted batch job 46588484
```
Le job SLURM étant soumis, l'utilisateur peut consulter l'avancement du job grâce à la commande `squeue`. On peut si besoin fermer le terminal Linux ou même éteindre la station de travail puisque le job est en cours d'évaluation sur le cluster de manière indépendante du terminal initial.

Dans un second temps, l'utilisateur peut lancer le script de collecte des résultats grâce au script `gather.py`. Ce script commence par lire le job sauvegardé dans le fichier `Pickle`. Cet objet est une instance de la classe `SLURMJobArrayJob`. Cette objet stocke toutes les informations relatives à l'exécution d'une étude paramétrique, en particulier le nom du répertoire de travail, la liste des sous-répertoires d'étude, la taille de l'échantillon, la taille de bloc et d'autres paramètres. Puis le script attend que les résultats soient disponibles grâce à une boucle `while`. A chaque itération, le script attend 1 seconde puis exécute la méthode `is_finished()` qui retourne `True` lorsque les résultats sont disponibles. Dans ce cas, la boucle `while` est interrompue. Puis, les données sont lues grâce à la méthode `get_input_output()` et retournées à l'utilisateur.
```python
# Part 2: reconnect to job, and wait
with open("job.pkl", "rb") as f:
    job = pickle.load(f)

print("job = ")
print(job)

print(f"Gathering results from {job.results_directory}.")

# Wait 60 seconds or less
tempo = 0.0
timeout = 60.0
wait_time = 1.0
verbose = True
finished = False
while not finished and tempo < timeout:
    if verbose:
        print(f"Wait for results after {tempo}")
    tempo += wait_time
    time.sleep(wait_time)
    finished = job.is_finished()

if tempo >= timeout:
    raise ValueError(f"Waited more than {timeout} seconds: time out.")
else:
    print("Success!")

# The job is finished: get the X/Y pair.
X, Y = job.get_input_output(verbose=True)

print("X = ")
print(X)

print("Y = ")
print(Y)
```
Si besoin, l'utilisateur peut sauvegarder ce couple (X, Y) dans un fichier CSV, mais cela n'est pas réalisé ici. La session de l'utilisateur est la suivante.
```bash
$ python3 gather.py
Gathering results from results_2025
Wait for results after 0
Wait for results after 1.0
[...]
Wait for results after 10.0
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
En pratique, l'utilisateur peut exécuter le script `gather.py` autant de fois que nécessaire.

## Scénario 4 : Plantages du modèle
Il peut arriver que l'évaluation du modèle échoue. Dans ce cas, une exception sera générée lors de l'évaluation de la fonction dans le répertoire de simulation local. Si cela arrive, l'exception est capturée par la classe `SLURMJobArrayFunction` et un vecteur de Nan, de dimension égale à la dimension de sortie est écrit dans le vecteur de sortie Y. Cela permet ensuite d'écrire le fichier de sortie sur le disque. Ainsi, le système d'attente de l'écriture de l'ensemble des fichiers de sorties correspondant à toutes les évaluations n'est pas bloqué.

Par exemple, le modèle `demo_SLURM_flood_fail.py` est construit de telle sorte qu'une évaluation sur deux échoue.
```bash
$ python3 demo_SLURM_flood_fail.py
```

L'instruction précédente génère l'affichage suivant.
```
Y = 
     [ S          ]
 0 : [   0.94531  ]
 1 : [   2.39764  ]
 2 : [  -5.76566  ]
 3 : [  -3.15975  ]
 4 : [  -6.67924  ]
 5 : [ nan        ]
 6 : [ nan        ]
 7 : [ nan        ]
 8 : [ nan        ]
 9 : [ nan        ]
10 : [  -5.10007  ]
[...]
```

## Classes
### Les classes structurantes
Dans cette section, nous présentons les classes structurantes du module `otcluster`
- `SLURMJobArrayJob`: Create a SLURM JobArray job. This implements `is_finished()` which returns True when the job is evaluated. It also implements `get_input_output()` which gathers the data from the sub.-directories.
- `SLURMJobArrayMachine`: Create a parallel function evaluated using the jobarray option of SLURM. Cette classe permet de stocker les paramètres d'évaluation d'un job sur le cluster comme la WcKey, le nom du fichier sbatch généré, les ressources utilisateurs, le nom du répertoire de base, le nom des répertoires de simulation et la taille du bloc. La méthode `copyResources()` est utilisée pour copier les ressources dans chaque répertoire d'étude. Cela peut être utile dans le cas où l'évaluation du modèle physique nécessite des fichiers supplémentaires.
- `SLURMJobArrayFunction`: Create a parallel function evaluated using the jobarray option of SLURM. This class uses `SLURMJobArrayMachine` and `SLURMJobArrayJob` to evaluate a function. Cette classe stocke un paramétrage donné d'un job évalué sur le cluster. Si il n'était pas nécessaire de procéder par soumission puis collecte, ce serait la seule classe utile.
- `FunctionInsideDirectory` : Evaluates the beam model inside a directory. L'objectif de cette classe est de fournir un service permettant d'étanchéifier les calculs nécessitant la mise en oeuvre de fichiers intermédiaires. Cette classe est une maquette qui n'est pas achevée. ~~D'après Joseph, la classe n'est pas toujours utilisable car il pourrait arriver que, si plusieurs jobs différents créent une instance de la classe, alors ils créent tous le même répertoire d'indice 0. Une alternative est l'utilisation d'un SHA1.~~ La classe  génère à présent une chaîne de caractères aléatoire utilisée comme suffixe du répertoire de travail d'une évaluation. Cela évite que plusieurs processus puissent écrire dans le même dossier.
- `MemoizeWithCSVFile`: Implémente un mécanisme de mémoire cache avec sauvegarde et chargement depuis un fichier CSV.
- `DaskFunction`: Create a Dask function from a model. Cette classe n'est pas aboutie.

### Articulation des classes
Les classes sont articulées de la manière suivante. 
- Le constructeur de `SLURMJobArrayMachine` est fondé sur une `ot.Function`. La méthode `SLURMJobArrayMachine.create()` retourne une instance de `SLURMJobArrayJob`.  Ces classes permettent de gérer le mécanisme de soumission et collecte.
- La classe `SLURMJobArrayFunction` permet d'évaluation une fonction sur cluster de manière simple. Le constructeur est fondé sur une `SLURMJobArrayMachine`. De plus, l'argument `wait_time` permet de configurer la durée maximale d'attente d'évaluation sur cluster. La méthode `_exec_sample` réalise une boucle d'attente puis utilise la méthode `SLURMJobArrayJob.get_input_output()`.

### Le code WCKEY et la classe WcKeyChecker
Le code WCKEY doit être fourni par l'utilisateur pour que les calculs effectués sur super-calculateur soient virtuellement facturés aux projets. Il s'agit d'une chaîne de caractère composée de deux parties séparées par deux points, la première partie étant le code PAREO du projet et la second étant le code applicatif dans ce projet :
```
CODEPAREO:CODE
```

La table suivante présente une liste de ces codes pour quelques exemples.

| WCKEY             | Projet                            |
| ----------------- | --------------------------------- |
| ~~P120F:PYTHON~~      | ~~Projet Ventilation Nucléaire 2024~~ (code non fonctionnel le 25/02/2025) |
| P11YB:ASTER       | Projet PSM 2024, code LEGOS       |
| P11N0:SALOME      | Projet PG2S, code SALOME          |
| P127Z:DATASCIENCE | Inconnu                           |
**Table 1.** Le code WCKEY de plusieurs projets.

La classe `WcKeyChecker` a pour objectif de vérifier que le code WcKey fourni par l'utilisateur est correct. Ainsi l'utilisateur peut savoir si le code est valide avant de soumettre le job à SLURM, ce qui permet de corriger le problème au plus tôt dans la chaîne de calcul. 

Le script suivant présente un exemple de la classe. La méthode `check()` prend en entrée le code et retourne le nom du projet et le nom du code si ils sont reconnus. Sinon, une exception est générée.

```python
checker = WcKeyChecker()
print(checker)
project, code = checker.check("p125v:openturns")
print(f"project = {project}")
print(f"code = {code}")
```

La classe possède deux modes de construction. Si `initialize_from_list` est vrai (c'est le mode par défaut), alors les valeurs stockées au sein de la classe sont utilisées. Une limitation de cet usage est que le code source de WcKeyChecker.py doit être modifié à chaque fois qu'un nouveau code Paréo est créé. Sinon, la classe utilise le programme `cce_wckeys` pour récupérer la liste des projets et des codes. Le second usage  est fondé sur l'exécution d'un programme en ligne de commande, ce qui est un peu moins performant.

### Découpage en blocs
Le constructeur de la classe `SLURMJobArrayMachine` dispose de l'option `block_size`. Ce paramètre représente le nombre maximum de points évalués lors d'une évaluation locale. Lorsqu'on évalue un plan d'expériences de taille `sample_size`, l'échantillon est découpé en sous-échantillon de taille maximale égale à `block_size`. Ainsi, le nombre de jobs requis est égal à `ceil(sample_size / block_size)`. La taille du bloc est un paramètre qui influe sur la méthode `create()` car elle détermine la valeur des indices de début et de fin de l'option `array` de Sbatch. 

Le découpage en blocs a plusieurs objectifs.
1. Pouvoir gérer un plan d'expériences de taille strictement supérieure à 500. En effet, c'est le nombre maximum de jobs simultanés acceptée par la configuration spécifique de SLURM sur les clusters EDF R&D en 2024.
2. Chaque noeud de calcul doit évaluer les points d'un échantillon de taille supérieure ou égale à 1. Ainsi, une fois que la pénalité de passage dans la file d'attente de SLURM est payée, chaque noeud de calcul peut être utilisé pour plus d'une évaluation si possible. Ainsi, on peut évaluer de manière performante des fonctions qui peuvent être peu coûteuses, à condition de confier à chaque noeud de calcul un nombre suffisant de points à évaluer.

### Création de l'étude paramétrique
La méthode `SLURMJobArrayMachine._build_tree()` crée l'étude paramétrique, ce qui est la partie la plus complexe de l'implémentation. Plus précisément, elle crée les sous-répertoires nécessaires pour rendre chaque calcul étanche, y compris lorsque le modèle physique $g$ lit et écrit des fichiers intermédiaires. De plus, elle permet l'évaluation retardée du modèle physique $g$ grâce au mécanisme de persistance assuré par la classe `ot.Study`.

Plus précisément, dans chaque sous-répertoire, la méthode crée un fichier CSV contenant les X à évaluer pour ce bloc. Puis elle crée un script d'évaluation locale qui évalue le sous-échantillon correspondant au job courant dans le `jobarray`. La méthode crée un fichier XML contenant le modèle physique $g$. Elle copie enfin les ressources nécessaires à l'évaluation locale, c'est-à-dire les fichiers et répertoires requis par l'évaluation unitaire, si l'utilisateur a configuré l'option `user_resources`.

### Evaluation locale pour un job
Présentons plus en détail le script Python local d'évaluation généré par la méthode `SLURMJobArrayMachine._build_tree()`. Le nom de ce script peut être paramétré grâce à l'option `local_evaluation_script_filename`. En résumé, le script permet d'assurer l'évaluation du modèle physique $g$ après la soumission du job par la commande `sbatch`. Ce script Python récupère la fonction qui est stockée dans une instance de `ot.Study` dans un fichier XML local. Ce mécanisme permet d'assurer la persistance de la fonction sur le disque. Le script lit les entrées X à évaluer depuis un fichier CSV qui a été préparé à l'avance. Puis le script local évalue les points du plan d'expériences si cela est nécessaire. Enfin, il écrit le fichier de sortie CSV contenant les Y. L'évaluation du sous-échantillon est encapsulée dans un `try/except` dans le but de gérer un éventuel plantage d'un point de ce bloc. Dans ce cas, la valeur de toutes les sorties pour ce bloc est égal à `Nan`, même si certains points intermédiaires peuvent avoir réussi.

## Questions ouvertes
On peut se demander comment compléter un plan d'expériences de taille 100 par un nouveau plan d'expériences de taille 100, formant ainsi un plan de taille 200. Si les répertoires sont toujours présents, peut-on simplement lire les répertoires déjà existant sans relancer le calcul, puis lancer un job contenant uniquement les calculs complémentaires ?

# Comparaison entre les propositions utilisant SLURM JobArray de Michaël et d'Elias

## Implémentation d'Elias

Elias a proposé un canevas d'implémentation d'une `OpenTURNSPythonFunction` permettant d'utiliser SLURM JobArray.

La classe proposée, `SLURMJobArrayWrapper`, ainsi que sa classe mère `OpenTURNSWrapper` et le script shell `jobarray_launcher.sh` doivent être modifiés en fonction de l'application,
car la classe contient la connaissance de cette application.

Description du workflow de la classe `SLURMJobArrayWrapper`:

1. Chargement des données d'entrée.
2. Création des répertoires d'évaluation. Dans chacun est placé le fichier d'entrée correspondant au template, dans lequel les valeurs d'un point d'entrée ont été substituées aux balises.
3. Commande `sbatch` de lancement du code dans chaque répertoire de simulation.
4. Parsing des résultats dans l'ensemble des répertoires d'évaluation pour reconstituer l'échantillon de sortie.

## Implémentation de Michaël

Michaël a proposé une classe `SLURMJobArrayFunction` qui hérite de `OpenTURNSPythonFunction` et prend en constructeur une autre `OpenTURNSPythonFunction` (fournie par l'utilisateur) responsable de l'exécution unitaire du code (mais pas de la gestion des dossiers, on suppose qu'elle s'exécute et lit/écrit des fichiers dans le répertoire courant).

La classe `SLURMJobArrayFunction` repose sur la classe `SLURMJobArrayMachine`, qui n'hérite d'aucune autre classe et est responsable de l'interfaçage avec l'API SLURM JobArray.
`SLURMJobArrayFunction` étant essentiellement un emballage de `SLURMJobArrayMachine` permettant de respecter l'API de `OpenTURNSPythonFunction`, nous nous intéressons à `SLURMJobArrayMachine` qui implémente les fonctionnalités intéressantes.

Le point important est que `SLURMJobArrayMachine` n'a aucune connaissance du code de calcul, ni de ce qu'il attend comme fichier d'entrée, ni de ce qu'il produit comme fichier de sortie.
`SLURMJobArrayMachine` connaît uniquement l'`OpenTURNSPythonFunction` responsable de l'exécution unitaire. L'utiisateur n'a pas besoin de modifier le code de `SLURMJobArrayMachine`.

Description du workflow de la classe `SLURMJobArrayMachine` :

1. Chargement des données d'entrée.
2. Création des répertoires d'évaluation. Dans chacun est placé :
- un CSV contenant un point d'entrée à évaluer
- un fichier XML et un fichier HDF5 contenant les informations relatives à une `Study` OpenTURNS contenant la `OpenTURNSPythonFunction` fournie par l'utilisateur
- un script Python chargeant la `Study` et le point d'entrée à évaluer, et écrivant la sortie correspondant à ce point dans un autre fichier CSV
3. Commande `sbatch` d'exécution des scripts Python dans chaque répertoire d'évaluation.
4. Collecte des CSV de sortie dans l'ensemble des répertoires d'évaluation pour reconstituer l'échantillon de sortie.
