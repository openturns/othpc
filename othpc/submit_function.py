#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin
"""
import time
import submitit
from tqdm import tqdm
import openturns as ot
from numpy import concatenate


class SubmitFunction(ot.OpenTURNSPythonFunction):
    """
    The aim of this class is to ease the realization of parallel evaluations of a numerical simulation model in a HPC environment.
    This class gives an example of a HPC wrapper for an executable numerical model using the Python package `submitit <https://github.com/facebookincubator/submitit>`_.

    Parameters
    ----------
    callable : :py:class:`openturns.Function`
        The unit function for which can either be sequential (a unit evaulation only requires one CPU),
        multi-cores or multi-nodes (a unit evaluation requires multiple cores and possibly multiple nodes).
    evals_per_jobs : int
        Defines the number of tasks (or evaluations of the numerical simulation model) realized in each single SLURM jobs.
    nodes_per_job : int
        Defines the number of HPC nodes requested per SLURM job submitted.
    cpus_per_job : int
        Defines the number of CPUs requested per SLURM job submitted.
    timeout_per_job : int
        Defines the timeout requested (in minutes) per SLURM job.
    memory_per_job : int
        Defines the memory (in MB) requested per SLURM job.
    slurm_wckey : str
        Only for clusters that require a WCKEY (EDF clusters for example), i.e. a project identification key. To check the current wckeys, use the bash command "cce_wckeys".

    Examples
    --------
    >>> import othpc
    >>> import openturns as ot
    >>> from othpc.example import CantileverBeam

    >>> cb = CantileverBeam("my_results")
    >>> slurm_cb = othpc.SubmitFunction(cb)
    >>> X = [[30e3, 28e6, 250.0, 400.0], [20e3, 35e6, 250.0, 400.0]]
    >>> Y = slurm_cb(X)
    """

    def __init__(
        self,
        callable,
        evals_per_jobs=1,
        nodes_per_job=1,
        cpus_per_job=4,
        timeout_per_job=5,
        memory_per_job=512,
        slurm_wckey="P120K:SALOME",
    ):
        super().__init__(callable.getInputDimension(), callable.getOutputDimension())
        self.setInputDescription(callable.getInputDescription())
        self.setOutputDescription(callable.getOutputDescription())
        self.evals_per_jobs = evals_per_jobs
        self.nodes_per_job = nodes_per_job
        self.cpus_per_job = cpus_per_job
        self.timeout_per_job = timeout_per_job
        self.memory_per_job = memory_per_job
        self.slurm_wckey = slurm_wckey
        self.callable = callable

        self.executor = submitit.AutoExecutor(folder="logs/%j")
        self.executor.update_parameters(
            slurm_mem=memory_per_job,
            cpus_per_task=cpus_per_job,
            nodes=nodes_per_job,
            timeout_min=timeout_per_job,
            slurm_wckey=slurm_wckey,
        )

    def _exec(self, X):
        return self._exec_point_on_exec_sample(X)

    def _exec_sample(self, X):
        # Divide input points across jobs (e.g. create batches)
        X = ot.Sample(X)
        X.setDescription(self.getInputDescription())
        job_number = len(X) // self.evals_per_jobs
        if len(X) % self.evals_per_jobs:
            job_number += 1  # an additional job is needed
        subsamples = [
            X[self.evals_per_jobs * i : self.evals_per_jobs * (i + 1)]
            for i in range(job_number)
        ]

        # Submit multiple jobs
        jobs = [
            self.executor.submit(self.callable, subsample) for subsample in subsamples
        ]

        # Track progress
        with tqdm(total=job_number) as pbar:
            completed = [False] * len(jobs)
            while not all(completed):
                for i, job in enumerate(jobs):
                    if not completed[i] and job.done():
                        completed[i] = True
                        pbar.update(1)
                time.sleep(1)  # Avoids spamming the scheduler

        # Return outputs
        result = ot.Sample(concatenate([job.result() for job in jobs], axis=0))
        result.setDescription(self.getOutputDescription())
        return result
