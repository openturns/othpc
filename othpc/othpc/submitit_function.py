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
    TBD
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
        slurm_extra_options=["--output=logs/output.log", "--error=logs/error.log"],
        verbose=False,
    ):
        super().__init__(callable.getInputDimension(), callable.getOutputDimension())
        self.setInputDescription(callable.getInputDescription())
        self.setOutputDescription(callable.getOutputDescription())
        self.tasks_per_job = tasks_per_job
        self.nodes_per_job = nodes_per_job
        self.cpus_per_job = cpus_per_job
        self.timeout_per_job = timeout_per_job
        self.memory_per_job = memory_per_job
        self.slurm_extra_options = slurm_extra_options
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
        

        if verbose:
            print(
                "** Requested ressources **\n"
                "**************************\n"
                f"+ cpus_per_job------{self.cpus_per_job}\n"
                f"+ timeout_per_job---{self.timeout_per_job} minutes\n"
                f"+ memory_per_job----{self.memory_per_job} MB\n"
            )
        # print(self.callable_file)

    def _exec_sample(self, X):
        # Divide input points across jobs (e.g. create batches)
        X = ot.Sample(X)
        X.setDescription(
            self.getInputDescription()
        )  # for accurate prints in print_and_call
        # tasks_per_job = len(X) // self.job_number
        job_number = len(X) // self.tasks_per_job
        if (
            len(X) % self.tasks_per_job
        ):  # if the input size is not divisible by the number of tasks per job
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
                time.sleep(1)  # Avoid spamming the scheduler

        # Return outputs
        result = ot.Sample(concatenate([job.result() for job in jobs], axis=0))
        result.setDescription(self.getOutputDescription())
        return result
