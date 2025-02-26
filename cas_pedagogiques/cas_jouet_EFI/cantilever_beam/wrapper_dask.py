#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari
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

from wrapper_base import OpenTURNSWrapper

class DaskWrapper(ot.OpenTURNSPythonFunction):
    """
    The aim of this class is to plug an black box model to an OpenTURNS.PythonFunction object in a HPC environment. 
    This class gives an example of a HPC wrapper for an executable black box model using the Python package Dask (see https://docs.dask.org/en/stable/). 
    
    Parameters
    ----------
    callable : openturns.Function
            The unit function to parallelize on the clusteer
    verbose : bool 
            Controls the verbosity, True by default

    Examples
    --------
    >>> input_file_path = "input_doe/doe.csv"
    >>> df_doe = pd.read_csv(input_file_path, index_col=0).reset_index()
    >>> X = ot.Sample.BuildFromDataFrame(df_doe)
    >>> my_wrapper = DaskWrapper(input_dimension=df_doe.shape[1], output_dimension=1, index_col=0)
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
        self.dask_options = ["--wckey=P120F:PYTHON",  f"--time={self.slurm_resources["timeout"]}", "--output=logs/output.log", "--error=logs/error.log"]

    @staticmethod
    def _wait_until_finished(futures, sleepl=10, text=None, verbose=True):
        """
        Waits for the jobs to be finished, either because the execution are done or by reaching a timeout threshold. 

        Parameters
        ----------

        futures : Dask.Futures
                Futures refer to results that may not be completed yet. 
        
        sleepl : integer
                Sets the number of seconds to wait between each iteration that checks that the futures are completed. 

        text : string
                Text displayed ahead of the verbose option. 

        verbose : Boolean
                If True, a progress bar is displayed.
        """

        print("_" * 55)
        start = time.time()
        if text is None: 
            text = "progress"
        statuses = np.array([future.status for future in futures])
        nb_submissions = len(futures)
        nb_finished = np.sum(statuses=='finished')
        counter = 0
        while nb_finished < nb_submissions : 
            pc = int((100 * nb_finished / nb_submissions) // 1)
            if verbose and (counter % 10) == 0:
                print(f"{text}:\t {pc}%\t|" + "#" * (pc//5) + " " * (20 - pc//5) + f"| {nb_finished} / {nb_submissions}")
            time.sleep(sleepl)
            statuses = np.array([future.status for future in futures])
            nb_finished = np.sum(statuses=='finished')
            nb_lost = np.sum(statuses=='lost')
            if nb_lost > 1:
                print(f"__ SLURM TIMEOUT! __")
                break
            counter += 1          
        print(f"{text}:\t 100%\t|" + "#" * (20) + f"| {nb_finished} / {nb_submissions}")
        elapsed = time.time() - start
        hours = int(elapsed // 3600)
        minutes = int((elapsed - 3600 * hours) // 60)
        seconds = int(elapsed - 3600 * hours - 60 * minutes)
        print(f"__ ELAPSED: ({hours:02d}:{minutes:02d}:{seconds:02d}) " + "_" * 26)

    
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
        nb_total_cores = self.slurm_resources["cpus-per-job"] * self.slurm_resources["nb-jobs"]
        # Define Dask object SLURMCluster
        #cluster = SLURMCluster(cores=self.slurm_resources["cpus-per-job"], 
                            #    memory=f"{self.slurm_resources["mem-per-job"]} MB", 
                            #    job_extra_directives=self.dask_options)
        #cluster.scale(self.slurm_resources["nb-jobs"])
        # print(f'> The dashboard link: {cluster.dashboard_link}')
        # Define Dask client
        client = Client()
        #client = Client(cluster)
        # Check that all the workers are up
        nb_total_running_cores = sum(client.ncores().values())
        while nb_total_running_cores < nb_total_cores: # Waiting for all the CPUs to be up is not the fastest
            pc = int((100 * nb_total_running_cores / nb_total_cores) // 1)
            if self.verbose: 
                print(f"RUNNING CORES: {pc}%\t|" + "#" * (pc//5) + " " * (20 - pc//5) + f"| {nb_total_running_cores} / {nb_total_cores}")
            time.sleep(5)
            nb_total_running_cores = sum(client.ncores().values())
        print(client)
        print(client.dashboard_link)

        futures = client.map(self._callable, X)

        #self._wait_until_finished(futures, sleepl=5, text="SIMULATE", verbose=self.verbose)
        wait(futures) # dask.distributed method to wait until all computations are finished or have errored # may not be necessary
        outputs = client.gather(futures) # liste de Points
        # attention, pour une raison etrange, outputs est une liste contenant une liste de listes
        # en d'autre termes, il y a un niveau de liste en trop par rapport a l'attendu
        #cluster.close()
        #client.shutdown()
        return outputs[0] # liste de Points = Sample
