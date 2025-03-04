analyse cas_pedagogiques/cas_jouet_JME/wrapper_dask.py
======================================================

* on peut passer les paramètres nombre de processus et interface réseau du fichier de configuration à l'instanciation de SLURMCluster

* on pourrait utiliser l'API asynchrone du client [1] au lieu de gather pour retourner la progression
  comme ce qui est fait pour le backend multiprocessing de otwrapy ou utiliser la barre de progression dask [2]
  comme le backed SSHCluster::

      for future in as_completed(futures):
        print(future.result())

  [1] https://docs.dask.org/en/latest/futures.html#distributed.as_completed
  [2] https://docs.dask.org/en/stable/diagnostics-distributed.html#progress-bar

* à la différence du backend SSHCluster de otwrapy on suppose les noeuds homogènes on utilise donc la fonction scale
  au contraire le backend SSHCluster pondère les jobs à dispatcher par noeud avec leur nombre de cpus respectifs

* il semble que l'on peut aussi utiliser les mot-clés death_timeout, log_directory directement
  au lieu de les passer sous la forme d'un dictionnaire d'options SLURM
  ce n'est pas le cas du wckey qui n'est pas pris en compte dans DASK


points utiles otwrapy
=====================

* otwrapy.Parallelizer (http://openturns.github.io/otwrapy/master/_generated/otwrapy.Parallelizer.html)
  Construit une nouvelle fonction avec parallélisation avec multiprocessing/ipyparallel/joblib/pathos/serial ou dask(ssh)::

    from otwrapy.examples.beam import Wrapper
    model = otw.Parallelizer(Wrapper(), n_cpus=-1)

  idée: transformer en décorateur / ajouter Dask+SLURM

* otwrapy.TempWorkDir (http://openturns.github.io/otwrapy/master/_generated/otwrapy.TempWorkDir.html)
  Utilise le patron de conception "contexte" Python pour créer manipuler un répertoire temporaire::

    with otw.TempWorkDir('/tmp', prefix='run-', cleanup=True) as tmp:
        shutil.copy(...)
        otcp.execute(cwd=tmp)
        parse(...)

  idée: transformer en décorateur de fonction ?

* otwrapy.FunctionDecorator (http://openturns.github.io/otwrapy/master/_generated/otwrapy.FunctionDecorator.html)
  Conversion d'une OpenTURNSPythonFunction en Function avec optionnellement le cache activé::

    @otw.FunctionDecorator(enableCache=True)
    class Wrapper(ot.OpenTURNSPythonFunction):
        pass

  idée: nouvelle classe de cache sur disque ?

* otwrapy.Debug
  Decorateur pour enregistrer les exceptions d'une fonction (via logging ou fichiers)::

    @otw.Debug('func.log')
    def func(*args, **kwargs):
        pass

Et aussi diverses API moins significatives:
- otwrapy.dump_array : sauver Sample avec compression
- otwrapy.load_array : charger Sample
- otwrapy.safemakedirs : créer dossier, sans exception s'il existe déjà
- otwrapy.create_logger : créer un enregistreur d'instance (module logging) avec sortie sur fichier, gestion d'un niveau de log
