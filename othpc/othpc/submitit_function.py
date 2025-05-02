#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin
"""
import os
import time
import othpc
import pickle
import inspect
import openturns as ot
import openturns.coupling_tools as otct
import submitit


class SubmitItFunction(ot.OpenTURNSPythonFunction):
    """
    TBD
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
        self.job_number = job_number
        self.nodes_per_job = nodes_per_job
        self.cpus_per_job = cpus_per_job
        self.timeout_per_job = timeout_per_job
        self.memory_per_job = memory_per_job
        self.slurm_extra_options = slurm_extra_options
        self.slurm_wckey = slurm_wckey
        #
        self.class_name = type(callable).__name__
        self.callable = callable
        self.callable_file = inspect.getfile(type(callable))

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
                f"+ job_number--------{self.job_number}\n"
                f"+ cpus_per_job------{self.cpus_per_job}\n"
                f"+ timeout_per_job---{self.timeout_per_job} minutes\n"
                f"+ memory_per_job----{self.memory_per_job} MB\n"
            )
        # print(self.callable_file)

    def _exec_sample(self, X):
        X = ot.Sample(X)
        outputs = ot.Sample(len(X), self.getOutputDimension())
        jobs = self.executor.map_array(self.callable, X)
        for i in range(len(X)):
            outputs[i] = jobs[i].result()
        return outputs


# TODO:
# Allow to have batches instead of the current 1 job per evaluation
