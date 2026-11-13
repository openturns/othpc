#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin
"""
import os
from pathlib import Path
import time
import submitit
from tqdm import tqdm
import openturns as ot
from numpy import concatenate
from .utils import evaluation_error_log


class DistributedMPIFunction(ot.OpenTURNSPythonFunction):
    """
    The aim of this class is to run parallel evaluations of a numerical simulation model in a HPC environment.
    It is based on the Python package `submitit <https://github.com/facebookincubator/submitit>`_.

    Parameters
    ----------
    callable : :py:class:`openturns.Function`
        The unit MPI function which can be  multi-cores or multi-nodes 
        (a unit evaluation requires multiple cores and possibly multiple nodes). 
        Each job handles one evaluation of the MPI function.
    timeout_per_job : int
        Timeout requested (in minutes) per SLURM job.
    ntasks_per_node : int
        Number of tasks that can be handled by a single node.
        Passed to SLURM as `--ntasks-per-node`.
    nodes_per_job : int
        Number of HPC nodes requested per SLURM job submitted.
        Passed to SLURM as `--nodes`.
    cpus_per_task : int
        Number of CPUs required to perform one task.
        Passed to SLURM as `--cpus-per-task`.
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
    The example callable runs an MPI load simulation. Create its results
    directory before constructing the model.

    >>> import os
    >>> import othpc
    >>> from othpc.example import MPILoadSimulator

    >>> os.makedirs("my_results", exist_ok=True)
    >>> simulator = MPILoadSimulator(nb_mpi_proc=10, results_directory="my_results")
    >>> slurm_simulator = othpc.DistributedMPIFunction(
    ...     simulator, ntasks_per_node=10, nodes_per_job=1
    ... )
    >>> X = [[1.0, 2.0], [3.0, 4.0]]
    >>> Y = slurm_simulator(X)
    """

    def __init__(
        self,
        callable,
        timeout_per_job=5,
        ntasks_per_node=1,
        nodes_per_job=1,
        cpus_per_task=1,
        mem=16000,
        slurm_wckey="P12H8:SALOME",
        slurm_additional_parameters=None,
    ):
        super().__init__(callable.getInputDimension(), callable.getOutputDimension())
        self.setInputDescription(callable.getInputDescription())
        self.setOutputDescription(callable.getOutputDescription())
        # assume a task means an evaluation of callable
        self.tasks_per_job = nodes_per_job * ntasks_per_node
        self.timeout_per_job = timeout_per_job
        # self.ntasks_per_node = ntasks_per_node
        self.nodes_per_job = nodes_per_job
        self.cpus_per_task = cpus_per_task
        self.mem = mem
        self.slurm_wckey = slurm_wckey
        self.callable = callable

        slurm_parameters = dict(slurm_additional_parameters or {})
        slurm_parameters.update(
            {"ntasks_per_node": ntasks_per_node, "nodes": nodes_per_job}
        )

        # Setup submitit executor
        self.executor = submitit.AutoExecutor(folder="logs/%j")
        self.executor.update_parameters(
            timeout_min=timeout_per_job,
            # slurm_ntasks_per_node=ntasks_per_node,
            # nodes=nodes_per_job,
            cpus_per_task=cpus_per_task,
            slurm_mem=mem,
            slurm_wckey=slurm_wckey,
            slurm_additional_parameters=slurm_parameters,
            # The callable is expected to relies on MPI, 
            # so srun is not needed and would would create 
            # duplicate instances of the callable execution. 
            slurm_use_srun=False,
        )

    def job(self, x):
        """Wrapper around callable to allow us to dispatch a single evaluation as a SLURM job"""

        # Get job id
        jobid = os.environ.get("SLURM_JOBID", 0)
        task_number = int(os.environ.get("SLURM_PROCID", 0))

        # Write input to CSV file for future reference
        input_as_sample = ot.Sample([x])
        input_as_sample.setDescription(self.getInputDescription())
        folder = os.path.join("logs", jobid)
        input_file = os.path.join(folder, f"{jobid}_{task_number}_input.csv")
        input_as_sample.exportToCSVFile(input_file)

        # Actual call to the callable
        output = self.callable(x)

        # Save output to CSV file in case the job fails
        # because some other task fails
        output_as_sample = ot.Sample([output])
        output_as_sample.setDescription(self.getOutputDescription())
        output_file = os.path.join(folder, f"{jobid}_{task_number}_output.csv")
        output_as_sample.exportToCSVFile(output_file)

        return output

    def _exec(self, X):
        return self._exec_point_on_exec_sample(X)

    def _exec_sample(self, X):
        # Divide input points across jobs (e.g. create batches)
        X = ot.Sample(X)
        X.setDescription(self.getInputDescription())
        job_number = len(X)

        # Submit multiple jobs
        jobs = [self.executor.submit(self.job, x) for x in X]

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
        partial_results_list = []
        for job in jobs:
            try:
                partial_results_list.append(job.results())
            except Exception as error:  # Case where the job failed
                output_point = [float("nan")] * self.getOutputDimension()
                job_error = job.exception()
                if job_error is None:
                    job_error = error
                evaluation_error_log(
                    job_error,
                    "logs",
                    f"JobFailure_{job.job_id}.txt",
                )
                partial_results_list.append([output_point])
        results = ot.Sample(concatenate(partial_results_list, axis=0))
        results.setDescription(self.getOutputDescription())
        return results
