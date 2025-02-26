# Objectif

Nous avons ici un exemple de spécialisation de la classe `OpenTURNSPythonFunction` basé sur le module de Salomé Ydefx qui permet de faire du calcul HPC.
Le scénario d'utilisation couvert ici permet de lancer les calculs à partir d'un poste de travail vers un cluster HPC distant.

# Contraintes Ydefx

Le module Salomé Ydefx a été conçu pour les besoins de Persalys, qui sont légèrement différents de ceux de la classe `OpenTURNSPythonFunction`.
Ainsi, la fonction d'étude est manipulée sous forme de texte dans Persalys. Elle est saisie par l'utilisateur dans un formulaire et l'API d'Ydefx permet de la spécifier sous forme de texte pour répondre à ce besoin.
La différence est que pour `OpenTURNSPythonFunction` on veut manipuler la fonction en tant qu'objet python, ce qui demande la gestion de sa sérialisation.
Par ailleurs, dans Persalys on veut identifier les entrées et les sorties par des noms pour mieux les gérer dans les différentes restitutions et l'API d'Ydefx propose un format qui inclut ces informations.
Openturns utilise son propre format, basé sur la classe `Sample`, et une conversion vers le format attendu par Ydefx est nécessaire.
A noter aussi que pour utiliser Ydefx il est nécessaire d'installer Salomé sur son poste de travail et sur le cluster. La configuration du cluster est automatique avec l'installeur EDF R&D.

# Cas d'utilisation

Avec Ydefx il est possible d'utiliser une ressource de type cluster HPC à partir de son poste de travail pour réaliser un calcul paramétrique.
L'installeur de Salomé fait la configuration automatique pour les clusters cronos et gaia si l'utilisateur détient un compte sur ces machines.
Il est aussi possible d'utiliser Salomé / Ydefx à partir des frontales de cronos et de gaia, mais il faut faire soi-même la configuration des ressources dans Salomé dans ce cas.
A noter qu'Ydefx permet aussi de lancer des calculs en local, mais cette fonctionnalité est déjà couverte par d'autres moyens dans Openturns.
L'API d'Ydefx fournit aussi des méthodes pour:
- suivre l'avancement du calcul,
- se déconnecter et se reconnecter plus tard à un calcul,
- identifier les points où le calcul est en erreur.

Ydefx implémente plusieurs stratégies dans la réalisation des calculs :
- faire toutes les évaluations dans un seul job,
- faire un job différent pour chaque évaluation,
- d'autres implémentations sont possibles.

Par ailleurs, Ydefx se base sur le composant Jobmanager de Salomé qui utilise une abstraction de la notion de job et permet l'utilisation de clusters qui utilisent d'autres gestionnaires de traitement par lot que Slurm, comme par exemple PBS.

# Principe

Ydefx permet l'évaluation d'un calcul paramétrique qui est défini à partir de trois éléments :

- la fonction d'étude,
- le plan d'expérience,
- les paramètres de lancement.

A partir de ces trois éléments on crée un objet 'étude' qu'on peut lancer.
A la fin de l'exécution de l'étude on récupère un objet résultat.

Il faut comprendre que l'exécution de la fonction d'étude est réalisée sur une machine et dans un environnement différents du poste de travail où Ydefx et Openturns sont utilisés. L'environnement d'exécution est l'installation de Salomé sur le cluster distant alors que l'environnement de lancement est l'installation de Salomé sur le poste de travail local.
En conséquence, il faut faire attention à fournir à Ydefx tout fichier nécessaire à l'exécution de la fonction d'étude pour le copier dans l'environnement d'exécution à partir du poste de travail.
Par ailleurs, dans le développement de la fonction d'étude il faut prendre en compte le fait que plusieurs évaluations peuvent être faite en même temps et gérer l'utilisation de l'espace disque pour éviter les conflits entre plusieurs exécutions simultanées.

## La fonction d'étude

L'objet "fonction d'étude" d'Ydefx est construit à partir d'une chaîne de caractères qui contient du code python qui inclut une fonction `_exec` qui est la fonction à exécuter.
L'objet d'Ydefx identifie les noms des entrées et des sorties de la fonction `_exec` et ces noms sont utilisés dans la définition du plan d'expérience et dans les résultats.
Ce format est adapté à l'usage fait par Persalys, mais il n'est pas utilisable directement dans le cas d'Openturns, car Openturns fournit un objet `OpenTURNSPythonFunction` et ne manipule pas les entrées et les sorties par leur nom.
L'adaptation pour Openturns consiste à utiliser une fonction `_exec` générique qui charge et exécute une sérialisation de la fonction python fournie par Openturns.
A noter la différence dans l'identification des paramètres entre Ydefx et Openturns :
- Ydefx identifie les paramètres par leur nom qui est donné par les noms des arguments de la fonction '_exec'
- Openturns identifie les paramètres par leur ordre dans un objet 'Point' sans leur donner de nom.

## Le plan d'expérience

La classe pydefx.Sample représente un plan d'expérience qui regroupe les données en entrée, les données en sortie et les éventuels messages d'erreur pour chaque point de la simulation.
Les données en entrée doivent être initialisées à partir d'un dictionnaire python où :
- la clé est le nom d'un paramètre de l'étude,
- la valeur est la liste des valeurs pour ce paramètre.

Cette représentation est différente de celle utilisée par Openturns où les noms des paramètres ne sont pas nécessaires.
Une conversion est nécessaire qui passe par l'attribution de noms arbitraires aux paramètres (p1, p2, etc.).

## Les paramètres de lancement

Les paramètres de lancement définissent les ressources de calcul à utiliser (nom du cluster, paramètres du job à créer, fichiers additionnels nécessaires au calcul, répertoires de travail) et le nombre maximum de calculs simultanés.
Ces paramètres sont définis dans un objet indépendant du gestionnaire de calculs par lots utilisé (comme Slurm, PBS ou autre).
Cet objet est définit par la classe `pydefx.Parameters` qui contient deux attributs :
- `nb_branches` qui est le nombre maximum d'évaluations simultannées
- `salome_parameters` qui est un objet de type `salome.JobParameters` défini dans le module Kernel de Salomé.

La documentation de la classe `JobParameters` est disponible ici : http://docs.salome-platform.org/latest/tui/KERNEL/structEngines_1_1JobParameters.html.

Quelques attributs importants :
- `resource_required.name` qui est le nom du cluster à utiliser ("cronos", "gaia").
- `resource_required.nb_proc` qui est le nombre total de tâches à réserver dans le cas de Slurm (équivalent au "--ntasks").
- `work_directory` qui est le répertoire de travail sur le cluster où le job sera exécuté.
- `in_files` qui est une liste de fichiers à copier depuis la machine locale. On peut y indiquer des chemins absolus ou relatifs. S'il y a des chemins relatifs, il faut renseigner l'attribut `local_directory` pour indiquer où il faut les chercher.
- `wckey` équivalent au paramètre "--wckey" dans Slurm.

Le nom de la ressource doit correspondre à une ressource déjà présente dans le catalogue des ressources de Salomé. Lors d'une installation à la R&D, les clusters "cronos" et "gaia" sont automatiquement configurés dans le catalogue.

## Le résultat

Le résultat d'un calcul Ydefx permet d'identifier plusieurs éléments :

- Un résultat global, pour l'ensemble du calcul, qui est intéressant dans le cas des calculs in-situ mais qui n'a pas d'intérêt dans notre cas d'utilisation.
- Un message d'erreur global, qui n'est pas associé à un calcul en particulier comme par exemple une erreur au moment de la soumission du job.
- Un résultat pour chaque point évalué. Ce résultat peut se décomposer en plusieurs valeurs associées à des noms différents. Les noms correspondent aux noms des variables python utilisés dans le `return` de la fonction `_exec`.
- Un message d'erreur pour chaque point qui a eu une évaluation en échec.

Comme pour les paramètres en entrée, les paramètres en sortie sont distingués par leur nom dans Ydefx, mais Openturns n'a pas besoin de cette information.
Pour simplifier l'écriture de la fonction `_exec` on peut utiliser un seul paramètre en sortie qui peut être aussi un tuple, une liste ou tout autre conteneur. Cette approche ne fonctionne pas pour les entrées dans l'implémentation actuelle d'Ydefx, mais elle fonctionne pour les sorties.

# Les modèles d'étude Ydefx

Ydefx offre avant tout une interface pour la réalisation de calculs paramétriques et plusieurs implémentations sont possibles pour s'adapter à des conditions d'exécution particulières.
Plusieurs implémentation sont disponibles à ce jour:

- PyStudy
- MultiJobStudy
- SlurmStudy

## PyStudy

La classe `PyStudy` est le modèle par défaut utilisé dans Persalys.
Son implémentation est basée sur l'utilisation du module YACS de Salomé et toutes les évaluations de la fonction d'étude se font dans le même job.

Son grand avantage est sa versatilité, car il peut être utilisé dans des situations très diverses :

- exécution locale ou distante,
- utilisation possible des divers gestionnaires de traitement par lot gérés dans Salomé,
- gestion des fonctions d'étude avec parallélisme interne en jouant sur le nombre de branches simultanées et le nombre de coeurs alloués dans le job.

Le principal inconvénient est que le cas où la fonction d'étude a besoin de plusieurs nœuds de calcul n'est pas couvert.

Le paramètre `nb_branches` définit le nombre maximum d'évaluations parallèles dans le job et les `salome_parameters` définissent les paramètres du job unique.


## MultiJobStudy

La classe `MultiJobStudy` permet de couvrir l'inconvénient de `PyStudy` et fournir une solution au cas où la fonction d'étude a besoin de plusieurs nœuds du cluster.
Dans ce mode chaque évaluation est réalisée dans un nouveau job.
Son implémentation n'utilise pas YACS.
Comme pour `PyStudy`, il est possible d'utiliser des ressources gérées par d'autres gestionnaires que Slurm.
Le paramètre `nb_branches` définit le nombre maximum de jobs simultanés et les `salome_parameters` définissent les paramètres commun pour tous les jobs.

## SlurmStudy

La classe `SlurmStudy` est une alternative à `PyStudy` qui n'utilise pas YACS mais qui ne peut marcher que pour Slurm.
En effet, les fonctionnalités de distribution des calculs sont couvertes avec la commande `srun` de Slurm à la place de YACS.

## Autres

D'autres implémentations sont envisageables si des besoins sont identifiés.
Par exemple, on peut envisager une implémentation à base de Dask.

# Fonctionnalités supplémentaires potentielles

Certaines fonctionnalités intéressantes ne sont pas traitées dans l'implémentation proposée ici:
- Points en erreur
- Détachement / rattachement

Cependant, ces fonctionnalités sont disponibles dans Ydefx, mais il faut identifier la façon de les utiliser dans Openturns.
A noter que le détachement - rattachement n'est pas aujourd'hui implémenté pour `MultiJobStudy` mais il est envisageable de l'ajouter.

A noter aussi qu'il est envisageable d'élargir l'API d'Ydefx pour faciliter son utilisation dans Openturns en plus de l'utilisation qui est faite dans Persalys.
On pense ici, par exemple, à l'utilisation directe de n'importe quelle fonction python en tant que fonction d'étude.

Il est important de noter aussi que le mécanisme des modèles d'Ydefx permet l'ajout de modules futures pour des cas d'utilisation qui ne sont pas couverts aujourd'hui. Par exemple, on peut imaginer le traitement du cas où la fonction d'étude est un schéma de calcul complexe, composé d'un enchaînement de plusieurs calculs qui ont des besoins différents en terme de ressources. L'interface "Epylog", utilisée dans la chaîne Odyssée, pourrait répondre à ce type de besoin pour écrire la fonction d'étude.
