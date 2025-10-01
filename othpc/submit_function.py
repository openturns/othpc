#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin
"""
import os
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
        The unit function for which can either be sequential (a unit evaluation only requires one CPU),
        multi-cores or multi-nodes (a unit evaluation requires multiple cores and possibly multiple nodes).
    timeout_per_job : int
        Timeout requested (in minutes) per SLURM job.
    ntasks_per_node : int
        Number of tasks (a task is a single evaluation of *callable*) that can be handled by a single SLURM job.
        Passed to SLURM as `--ntasks-per-node`.
    nodes_per_job : int
        Number of HPC nodes requested per SLURM job submitted.
        Passed to SLURM as `--nodes`.
    cpus_per_task : int
        Number of CPUs required to perform one task, i.e. one evaluation of *callable*.
    mem : int
        Memory (in MB) requested per node.
        Passed to SLURM as `--mem`.
    slurm_wckey : str
        Only for clusters that require a WCKEY (EDF clusters for example), i.e. a project identification key.
        To check the current wckeys, use the bash command `cce_wckeys`.
        Passed to SLURM as `--wckey`.
    slurm_additional_parameters : dictionary
        Extra parameters to pass to SLURM (for example, `{"exclusive": True, "mem_per_cpu": 12}`).
        Empty by default.


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
        timeout_per_job=5,
        ntasks_per_node=1,
        nodes_per_job=1,
        cpus_per_task=1,
        mem=512,
        slurm_wckey="P120K:SALOME",
        slurm_additional_parameters={},
    ):
        super().__init__(callable.getInputDimension(), callable.getOutputDimension())
        self.setInputDescription(callable.getInputDescription())
        self.setOutputDescription(callable.getOutputDescription())
        # assume a task means an evaluation of callable
        self.tasks_per_job = nodes_per_job * ntasks_per_node
        self.timeout_per_job = timeout_per_job
        self.ntasks_per_node = ntasks_per_node
        self.nodes_per_job = nodes_per_job
        self.cpus_per_task = cpus_per_task
        self.mem = mem
        self.slurm_wckey = slurm_wckey
        self.callable = callable

        # Wrapper around callable to be able to dispatch single evaluation as SLURM tasks
        def task(X):
            task_number = int(os.environ.get("SLURM_PROCID", 0))
            if not task_number < len(X):
                return [float("nan")] * self.getOutputDimension()
            return self.callable(X[task_number])

        self.task = task

        # Setup submitit executor
        self.executor = submitit.AutoExecutor(folder="logs/%j")
        self.executor.update_parameters(
            timeout_min=timeout_per_job,
            slurm_ntasks_per_node=ntasks_per_node,
            nodes=nodes_per_job,
            cpus_per_task=cpus_per_task,
            slurm_mem=mem,
            slurm_wckey=slurm_wckey,
            slurm_additional_parameters=slurm_additional_parameters,
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
        jobs = [self.executor.submit(self.task, subsample) for subsample in subsamples]

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
        result = ot.Sample(concatenate([job.results() for job in jobs], axis=0))
        result.setDescription(self.getOutputDescription())
        # Rows beyond len(X) are dummy rows filled with NaNs.
        # They are generated by the useless tasks in the last job if len(X) % self.tasks_per_job != 0.
        # If len(X) % self.tasks_per_job == 0, then len(result) == len(X) anyway.
        return result[0 : len(X)]
