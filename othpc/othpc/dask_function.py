#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin
"""
import openturns as ot
from dask_jobqueue import SLURMCluster
from dask.distributed import Client, print, progress


class DaskFunction(ot.OpenTURNSPythonFunction):
    """
    The aim of this class is to plug a numerical simulation model to an OpenTURNS.PythonFunction object in a HPC environment.
    This class gives an example of a HPC wrapper for an executable numerical model using the Python package Dask (see https://docs.dask.org/en/stable/).

    Parameters
    ----------
    callable : openturns.Function
        The unit function to parallelize on the cluster
    job_number : integer
        Defines the number of jobs submitted.
    nodes_per_job : integer
        Defines the number of nodes requested per job.
    cpus_per_job : integer
        Defines the number of cpus requested per job.
    timeout_per_job : integer
        Defines the timeout requested (in minutes) per job.
    memory_per_job : integer
        Defines the memory (in MB) requested per job.
    slurm_wckey : string
        Only for EDF clusters. Defines the identifaction key of a project. To check the current wckeys, use the bash command "cce_wckeys".
    slurm_extra_options : list
        Gives access to all the other arguments that can be parsed by the SLURM sbatch API.

    Examples
    --------
    >>> import othpc
    >>> import openturns as ot
    >>> from cantilever_beam import CantileverBeam

    >>> cb = CantileverBeam("template/beam_input_template.xml", "template/beam", "my_results")
    >>> dask_wrapper = othpc.DaskFunction(cb)
    >>> X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
    >>> Y = dask_wrapper(X)
    """

    def __init__(
        self,
        callable,
        job_number=1,
        nodes_per_job=1,
        cpus_per_job=4,
        timeout_per_job=5,
        memory_per_job=512,
        slurm_wckey="P120K:SALOME",
        slurm_extra_options=["--output=logs/output.log", "--error=logs/error.log"],
        verbose=False,
    ):
        super().__init__(callable.getInputDimension(), callable.getOutputDimension())
        self._callable = callable
        self.setInputDescription(callable.getInputDescription())
        self.setOutputDescription(callable.getOutputDescription())
        self.job_number = job_number
        self.nodes_per_job = nodes_per_job
        self.cpus_per_job = cpus_per_job
        self.timeout_per_job = timeout_per_job
        self.memory_per_job = memory_per_job
        self.slurm_extra_options = slurm_extra_options
        self.dask_options = [f"--wckey={slurm_wckey}"] + slurm_extra_options + [f"--nodes={nodes_per_job}"]
        self.cluster = SLURMCluster(
            cores=self.cpus_per_job,
            memory=f"{self.memory_per_job} MB",
            walltime=self.timeout_per_job,
            name="dask_worker",
            job_extra_directives=self.dask_options,
            interface="ib0",
            job_directives_skip=['-n 1']
        )
        if verbose:
            print(
                "** Requested ressources **\n"
                "**************************"
                f"+ job_number--------{self.job_number}\n"
                f"+ nodes_per_job-----{self.nodes_per_job}\n"
                f"+ cpus_per_job------{self.cpus_per_job}\n"
                f"+ timeout_per_job---{self.timeout_per_job} minutes\n"
                f"+ memory_per_job----{self.memory_per_job} MB\n"
            )

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
        # print(X)
        # Creates job_number SLURM jobs
        self.cluster.scale(self.job_number)
        # print(f"> The dashboard link from the cluster : {self.cluster.dashboard_link}")

        # Create a Client for the SLURMCluster object
        client = Client(self.cluster)

        # OPTION 1
        # futures = client.map(self._callable, X)
        # outputs = client.gather(futures)

        # OPTION 2
        # WE NOTICE THAT THE 'PENDING' STATE IS LONGER BUT THIS ALLOWS US TO USE OpenTURNS ALGORITHMS
        async def f():
            futures = client.map(self._callable, X)
            outputs = await client.gather(futures, asynchronous=True)
            return outputs
        outputs = client.sync(f)
        client.close()

        # OPTION 3 (to be tested)
        # From Dask documentation: https://distributed.dask.org/en/stable/asynchronous.html
        # async def f():
        #     client = await Client(self.cluster, asynchronous=True)
        #     print(client)
        #     futures = client.map(self._callable, X)
        #     # progress(futures)
        #     outputs = await client.gather(futures, asynchronous=True)
        #     await client.close()
        #     return outputs
        # # Use asyncio
        # outputs = asyncio.get_event_loop().run_until_complete(f())

        return outputs
