#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin
"""

import os
import time
import numpy as np
import openturns as ot

from dask_jobqueue import SLURMCluster
from dask.distributed import Client, print
from .WcKeyChecker import WcKeyChecker


class DaskFunction(ot.OpenTURNSPythonFunction):
    def __init__(
        self,
        model,
        sbatch_wckey,
        slurm_extra_options="",
        dask_cores=1,
        dask_nb_jobs=1,
        dask_memory="512 MB",
        wait_time=1.0,
        verbose=False,
    ):
        """
        Create a Dask function from a model.

        Parameters
        ----------
        sbatch_wckey : string
            The WCKEY of the project.
            Please contact your project manager to see which one to use.
            Generates an exception if the key is unknown.
        slurm_extra_options : string
            The extra options of sbatch.
            None of these options should contain "wckey", as this option is
            directly managed by DaskFunction.
            See https://slurm.schedmd.com/sbatch.html for details.
        dask_nb_jobs : integer
            Defines the number of jobs submitted.
        dask_cores : integer
            Defines the number of CPUs requested per job.
        dask_memory : integer
            Defines the memory per job.
        wait_time : float, > 0
            The time (in seconds) the code waits before checking if all the output
            files are available.
        verbose : bool
            Set to True to print intermediate messages.
        """
        super().__init__(model.getInputDimension(), model.getOutputDimension())
        self.setInputDescription(model.getInputDescription())
        self.setOutputDescription(model.getOutputDescription())
        self.verbose = verbose
        self.slurm_extra_options = slurm_extra_options
        self.model = model
        checker = WcKeyChecker()
        _, _ = checker.check(sbatch_wckey)
        self.sbatch_wckey = sbatch_wckey
        self.dask_options = [
            f"--wckey={sbatch_wckey}",
            f"{slurm_extra_options}",
        ]
        # TODO: check that slurm_extra_options has no wckey
        # TODO: check values of input arguments
        self.dask_cores = dask_cores
        self.dask_nb_jobs = dask_nb_jobs
        self.dask_memory = dask_memory
        self.wait_time = wait_time

    def _wait_until_finished(self, futures, text=None):
        """
        Waits for the jobs to be finished

        The jobs are finished:
        - if the execution are done or
        - by reaching a timeout threshold.

        Parameters
        ----------
        futures : Dask.Futures
                Futures refer to results that may not be completed yet.
        text : string
                Text displayed ahead of the verbose option.
        """
        if self.verbose:
            print("_" * 55)
        start = time.time()
        if text is None:
            text = "progress"
        statuses = np.array([future.status for future in futures])
        nb_submissions = len(futures)
        nb_finished = np.sum(statuses == "finished")
        counter = 0
        while nb_finished < nb_submissions:
            if self.verbose and (counter % 10) == 0:
                pc = int((100 * nb_finished / nb_submissions) // 1)
                print(
                    f"{text}:\t {pc}%\t|"
                    + "#" * (pc // 5)
                    + " " * (20 - pc // 5)
                    + f"| {nb_finished} / {nb_submissions}"
                )
            time.sleep(self.wait_time)
            statuses = np.array([future.status for future in futures])
            nb_finished = np.sum(statuses == "finished")
            nb_lost = np.sum(statuses == "lost")
            if nb_lost > 1:
                print(f"Slurm timeout")
                break
            counter += 1
        print(f"{text}:\t 100%\t|" + "#" * (20) + f"| {nb_finished} / {nb_submissions}")
        elapsed = time.time() - start
        hours = int(elapsed // 3600)
        minutes = int((elapsed - 3600 * hours) // 60)
        seconds = int(elapsed - 3600 * hours - 60 * minutes)
        print(f"ELAPSED: ({hours:02d}:{minutes:02d}:{seconds:02d}) " + "_" * 26)

    def _exec_sample(self, X):
        """
        Launches the parallel evaluations black-box model evaluated at the input design of experiments X.

        Parameters
        ----------
        X : ot.Sample(size, input_dimension)
            The input sample.

        Returns
        -------
        Y : ot.Sample(size, output_dimension)
            The output sample.
        """
        X = ot.Sample(X)
        if self.verbose:
            print("Create SLURMCluster")
        nb_total_cores = self.dask_cores * self.dask_nb_jobs
        if self.verbose:
            print(
                f"dask_cores = {self.dask_cores}, "
                f"dask_nb_jobs = {self.dask_nb_jobs}, "
                f"nb_total_cores = {nb_total_cores}"
            )
        # Define Dask object SLURMCluster
        cluster = SLURMCluster(
            cores=self.dask_cores,
            memory=f"{self.dask_memory}",
            job_extra_directives=self.dask_options,
        )
        cluster.scale(self.dask_nb_jobs)
        if self.verbose:
            print("cluster=")
            print(cluster)
        # print(f'> The dashboard link: {cluster.dashboard_link}')
        # Define Dask client
        client = Client(cluster)
        if self.verbose:
            print("client=")
            print(client)
        # Check that all the workers are up
        nb_total_running_cores = sum(client.ncores().values())
        while (
            nb_total_running_cores < nb_total_cores
        ):  # Waiting for all the CPUs to be up is not the fastest
            if self.verbose:
                pc = int((100 * nb_total_running_cores / nb_total_cores) // 1)
                print(
                    f"RUNNING CORES: {pc}%\t|"
                    + "#" * (pc // 5)
                    + " " * (20 - pc // 5)
                    + f"| {nb_total_running_cores} / {nb_total_cores}"
                )
            time.sleep(self.wait_time)
            nb_total_running_cores = sum(client.ncores().values())
        if self.verbose:
            pc = int((100 * nb_total_running_cores / nb_total_cores) // 1)
            print(
                f"RUNNING CORES: {pc}%\t|"
                + "#" * (pc // 5)
                + " " * (20 - pc // 5)
                + f"| {nb_total_running_cores} / {nb_total_cores}"
            )
        if self.verbose:
            print("client=")
            print(client)

        futures = client.map(self.model, X)
        if self.verbose:
            print("futures = ", futures)
        self._wait_until_finished(
            futures,
            text="SIMULATE",
        )
        outputs = client.gather(futures)  # liste de Points
        cluster.close()
        client.shutdown()
        return outputs  # liste de Points = Sample
