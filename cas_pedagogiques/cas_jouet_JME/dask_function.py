#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""

import os
import time
import pickle
import numpy as np 
import pandas as pd
import openturns as ot
from argparse import ArgumentParser, FileType
from dask_jobqueue import SLURMCluster
from dask.distributed import Client, print, progress, wait


class DaskFunction(ot.OpenTURNSPythonFunction):
    """
    The aim of this class is to plug an black box model to an OpenTURNS.PythonFunction object in a HPC environment. 
    This class gives an example of a HPC wrapper for an executable black box model using the Python package Dask (see https://docs.dask.org/en/stable/). 
    
    Parameters
    ----------
    callable : openturns.Function
            The unit function to parallelize on the cluster
    verbose : bool 
            Controls the verbosity, True by default

    Examples
    --------
    >>> input_file_path = "input_doe/doe.csv"
    >>> df_doe = pd.read_csv(input_file_path, index_col=0).reset_index()
    >>> X = ot.Sample.BuildFromDataFrame(df_doe)
    >>> my_wrapper = DaskFunction(input_dimension=df_doe.shape[1], output_dimension=1, index_col=0)
    >>> g = my_wrapper.get_function()
    >>> Y = g(X)
    """
    def __init__(self, callable, verbose=True):
        # Inherit methods and attributes from the base class "OpenTURNSWrapper"
        super().__init__(callable.getInputDimension(), callable.getOutputDimension())
        self._callable = callable
        self.verbose = verbose
        # Path of the beam executable
        #self.my_executable = os.path.join(self.base_dir, "template/beam")
        # SLURM options 
        self.slurm_resources = {
        "nodes-per-job": 1,
        "cpus-per-job": 1,
        "mem-per-job": 512, # 512 MB
        "timeout": "00:05:00", # 5 minutes
        "nb-jobs": 10
        }
        self.dask_options = ["--wckey=P120K:SALOME",  f"--time={self.slurm_resources["timeout"]}", "--output=logs/output.log", "--error=logs/error.log"]

        # Define Dask object SLURMCluster
        self.cluster = SLURMCluster(cores=self.slurm_resources["cpus-per-job"],
                                    memory=f"{self.slurm_resources["mem-per-job"]} MB",
                                    job_extra_directives=self.dask_options)

    def _exec_sample(self, X):
        """
        Launches the parallel evaluations black-box model evaluated at the input design of experiments X. 

        Parameters
        ----------
        X : OpenTURNS.Sample
        
        Returns
        -------
        Y : list
            This object contains the output results. 
        """
        X = ot.Sample(X)

        # Submit jobs to SLURM
        self.cluster.scale(self.slurm_resources["nb-jobs"])
        print(f'> The dashboard link from the cluster : {self.cluster.dashboard_link}')

        # Create a Client for the SLURMCluster object
        client = Client(self.cluster)
        print(f'> The dashboard link from the client  : {client.dashboard_link}')

        # # Check that all the workers are up
        # nb_total_cores = self.slurm_resources["cpus-per-job"] * self.slurm_resources["nb-jobs"]
        # nb_total_running_cores = sum(client.ncores().values())
        # while nb_total_running_cores < nb_total_cores: # Waiting for all the CPUs to be up is not the fastest
        #     pc = int((100 * nb_total_running_cores / nb_total_cores) // 1)
        #     if self.verbose:
        #         print(f"RUNNING CORES: {pc}%\t|" + "#" * (pc//5) + " " * (20 - pc//5) + f"| {nb_total_running_cores} / {nb_total_cores}")
        #     time.sleep(5)
        #     nb_total_running_cores = sum(client.ncores().values())

        # Distribute the evaluations
        futures = client.map(self._callable, X)
        progress(futures)
        # # wait est une methode de dask.distributed servant a attendre que tous les calculs soient finis ou aient renvoye une erreur
        # # mais cela ne semble pas necessaire en pratique
        # wait(futures) # dask.distributed method to wait until all computations are finished or have errored # may not be necessary
        outputs = client.gather(futures) # liste de Points

        # # Ces commandes sont peut-etre plus propres mais ne semblent pas indispensables :
        # cluster.close()
        client.shutdown()

        # # attention, pour une raison etrange, outputs (en version LocalCluster) est une liste contenant une liste de listes
        # # en d'autre termes, il y a un niveau de liste en trop par rapport a l'attendu
        # # Avec LocalCluster, on est oblige d'utiliser
        # return outputs[0]
        # Ce probleme ne se pose pas avec SLURMCluster.
        return outputs # liste de Points = Sample
