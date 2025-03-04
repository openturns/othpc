analyse cas_pedagogiques/cas_jouet_JME/wrapper_dask.py
======================================================

* on peut passer les paramètres nombre de processus et interface réseau du fichier de configuration à l'instanciation de SLURMCluster

* on pourrait utiliser l'API asynchrone du client [1] au lieu de gather pour retourner la progression
  comme ce qui est fait pour le backend multiprocessing de otwrapy ou utiliser la barre de progression dask [2] comme le backed SSHCluster

    for future in as_completed(futures):
        print(future.result())

[1] https://docs.dask.org/en/latest/futures.html#distributed.as_completed
[2] https://docs.dask.org/en/stable/diagnostics-distributed.html#progress-bar

* à la différence du backend SSHCluster de otwrapy on suppose les noeuds homogènes on utilise donc la fonction scale
  au contraire le backend SSHCluster pondère les jobs à dispatcher par noeud avec leur nombre de cpus respectifs

* il semble que l'on peut aussi utiliser les mot-clés death_timeout, log_directory directement
  au lieu de les passer sous la forme d'un dictionnaire d'options SLURM
  ce n'est pas le cas du wckey qui n'est pas pris en compte dans DASK