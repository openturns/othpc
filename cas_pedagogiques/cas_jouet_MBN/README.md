# Etude paramétrique avec le cas de la poutre encastrée

## Introduction
Les scripts Python présentés ici permettent de réaliser une étude paramétrique
avec le modèle de poutre encastrée. 
Le plan d'expériences est réalisé avec OpenTURNS, sur la base d'un échantillon 
Monte-Carlo simple.

Voici une courte description des répertoires.
- `beam_local` : Le cas de la poutre encastrée fondé sur l'échange de fichiers. L'évaluation est réalisée sur la station de travail, en local. C'est le pré-requis de l'étude, c'est-à-dire le script que doit fournir l'utilisateur souhaitant évaluer la fonction sur cluster.
- `beam_with_jobarray` : Une implémentation de l'évaluation sur cluster du cas de la poutre encastrée fondée sur SLURM. La méthode de parallélisation est fondé sur la commande `jobarray` de l'outil SLURM.
- `beam_with_ot` : Une implémentation fondée sur un nouveau module, nommé  `otcluster`. La méthode consiste à définir une fonction (une `ot.Function`) implémentant le couplage, puis à évaluer cette fonction en parallèle sur plusieurs noeuds de calcul.
