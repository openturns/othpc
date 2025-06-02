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


class SubmitItFunction(ot.OpenTURNSPythonFunction):
    """
    The aim of this class is to ease the realization of parallel evaluations of a numerical simulation model in a HPC environment.
    This class gives an example of a HPC wrapper for an executable numerical model using the Python package submitit (see https://github.com/facebookincubator/submitit/tree/main).

    Parameters
    ----------
    callable : openturns.Function
        The unit function for which can either be sequential (a unit evaulation only requires one CPU),
        multi-cores or multi-nodes (a unit evaluation requires multiple cores and possibly multiple nodes).
    tasks_per_job : integer
        Defines the number of tasks (or evaluations of the numerical simulation model) realized in each single SLURM jobs.
    nodes_per_job : integer
        Defines the number of HPC nodes requested per SLURM job submitted.
    cpus_per_job : integer
        Defines the number of CPUs requested per SLURM job submitted.
    timeout_per_job : integer
        Defines the timeout requested (in minutes) per SLURM job.
    memory_per_job : integer
        Defines the memory (in MB) requested per SLURM job.
    slurm_wckey : string
        Only for EDF clusters. Defines the identification key of a project. To check the current wckeys, use the bash command "cce_wckeys".

    Examples
    --------
    >>> import othpc
    >>> import openturns as ot
    >>> from cantilever_beam import CantileverBeam

    >>> cb = CantileverBeam("template/beam_input_template.xml", "template/beam", "my_results")
    >>> slurm_cb = othpc.SubmitItFunction(cb)
    >>> X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
    >>> Y = slurm_cb(X)
    """

    def __init__(
        self,
        callable,
        tasks_per_job=1,
        nodes_per_job=1,
        cpus_per_job=4,
        timeout_per_job=5,
        memory_per_job=512,
        slurm_wckey="P120K:SALOME",
    ):
        super().__init__(callable.getInputDimension(), callable.getOutputDimension())
        self.setInputDescription(callable.getInputDescription())
        self.setOutputDescription(callable.getOutputDescription())
        self.tasks_per_job = tasks_per_job
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
        job_number = len(X) // self.tasks_per_job
        if len(X) % self.tasks_per_job:
            job_number += 1  # an additional job is needed
        subsamples = [
            X[self.tasks_per_job * i : self.tasks_per_job * (i + 1)]
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
