#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""

import pickle
import openturns as ot
from dask_jobqueue import SLURMCluster
from dask.distributed import Client, print, progress


class DaskFunction(ot.OpenTURNSPythonFunction):
    """
    The aim of this class is to plug an black box model to an OpenTURNS.PythonFunction object in a HPC environment. 
    This class gives an example of a HPC wrapper for an executable black box model using the Python package Dask (see https://docs.dask.org/en/stable/). 
    
    Parameters
    ----------
    callable : openturns.Function
            The unit function to parallelize on the cluster
    csv_dump_file : str 
            If not None, it writes an input-ouput csv file at the absolute path given. 

    Examples
    --------
    >>> input_file_path = "input_doe/doe.csv"
    >>> df_doe = pd.read_csv(input_file_path, index_col=0).reset_index()
    >>> X = ot.Sample.BuildFromDataFrame(df_doe)
    >>> my_wrapper = DaskFunction(input_dimension=df_doe.shape[1], output_dimension=1, index_col=0)
    >>> g = my_wrapper.get_function()
    >>> Y = g(X)
    """
    def __init__(self, callable, csv_dump_file=None):
        # Inherit methods and attributes from the base class "OpenTURNSWrapper"
        super().__init__(callable.getInputDimension(), callable.getOutputDimension())
        self._callable = callable
        self.csv_dump_file = csv_dump_file
    
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

        # Distribute the evaluations
        futures = client.map(self._callable, X)
        progress(futures)
        # # wait est une methode de dask.distributed servant a attendre que tous les calculs soient finis ou aient renvoye une erreur
        # # mais cela ne semble pas necessaire en pratique
        # wait(futures) # dask.distributed method to wait until all computations are finished or have errored # may not be necessary
        outputs = client.gather(futures) # liste de Points
        if self.csv_dump_file is not None: 
            X.stack(outputs)
            X.exportToCSVFile(self.csv_dump_file, ',')

        # # Ces commandes sont peut-etre plus propres mais ne semblent pas indispensables :
        # cluster.close()
        client.shutdown()

        return outputs 
