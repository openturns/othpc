#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré, Michaël Baudin
"""

import openturns as ot
import time
from .SLURMJobArrayMachine import SLURMJobArrayMachine


class SLURMJobArrayFunction(ot.OpenTURNSPythonFunction):

    def __init__(
        self,
        slurm_machine,
        wait_time=1.0,
        timeout=60.0,
        verbose=False,
    ):
        """
        Create a parallel function evaluated using the jobarray option of SLURM.

        References
        ----------
        - https://slurm.schedmd.com/job_array.html
        - https://slurm.schedmd.com/sbatch.html

        Parameters
        ----------
        slurm_machine : SLURMJobArrayMachine
            The SLURM machine.
        wait_time : float, > 0
            The time (in seconds) the code waits before checking if all the output
            files are available.
        timeout : float, > 0
            The time (in seconds) after which the code stops to wait for outputs.
        verbose : bool
            Set to True to print intermediate messages.

        Examples
        --------

        The next script is the beam example.
        >>> import openturns as ot
        >>> from BeamFunction import BeamFunction
        >>> from SLURMJobArrayFunction import SLURMJobArrayFunction
        >>> beamModel = BeamFunction()
        >>> X_distribution = beamModel.getInputDistribution()
        >>> X = X_distribution.getSample(10)
        >>> model = ot.Function(beamModel)
        >>> cwd = os.getcwd()
        >>> user_resources = [
        >>>     os.path.join(cwd, "beam_input_template.xml"),
        >>>     os.path.join(cwd, "beam"),
        >>>     os.path.join(cwd, "BeamFunction.py"),
        >>> ]
        >>> base_directory = os.getcwd()
        >>> slurm_machine = SLURMJobArrayMachine(
        >>>     model,
        >>>     user_resources=user_resources,
        >>>     base_directory=base_directory
        >>> )
        >>> slurm_wrapper = SLURMJobArrayFunction(slurm_machine)
        >>> slurm_function = ot.Function(slurm_wrapper)
        >>> Y = slurm_wrapper(X)

        In the next example, we fine-tune the sbatch options.
        >>> sbatch_extra_options = '--output="logs/output.log" ' \
        >>>     '--error="logs/error.log"' \
        >>>     '--nodes=1' \
        >>>     ' --cpus-per-task=1' \
        >>>     ' --mem=512' \
        >>>     ' --time="00:05:00"'
        >>> slurm_machine = SLURMJobArrayMachine(
        >>>     model, user_resources=user_resources, base_directory=base_directory,
        >>>     sbatch_extra_options=sbatch_extra_options
        >>> )
        """
        # Store the SLURM machine
        self.slurm_machine = slurm_machine
        if not isinstance(self.slurm_machine.model, ot.Function):
            raise ValueError(
                f"The model must be a ot.Function, but "
                f"model has type {type(model)}."
            )
        input_dimension = self.slurm_machine.model.getInputDimension()
        output_dimension = self.slurm_machine.model.getOutputDimension()
        super(SLURMJobArrayFunction, self).__init__(input_dimension, output_dimension)
        self.setInputDescription(self.slurm_machine.model.getInputDescription())
        self.setOutputDescription(self.slurm_machine.model.getOutputDescription())
        # Other options
        if wait_time <= 0.0:
            raise ValueError(f"The wait_time is {wait_time}, but it should be > 0.")
        self.wait_time = wait_time
        if timeout <= 0.0:
            raise ValueError(f"The timeout is {timeout}, but it should be > 0.")
        self.timeout = timeout
        self.verbose = verbose

    def _exec_sample(self, X):
        """
        Launches the parallel evaluations black-box model evaluated at the input design of experiments X.

        This function implements _exec_sample() so that the sample is
        evaluated in N different local simulation directories.
        Each local simulation directory is first created.
        Then the associated user_resources are copied in this local simulation directory.
        All simulations are performed using the "array" option of SLURM.
        SLURMJobArrayFunction waits until all the results are available, then
        gathers the data in all local simulation directories.

        TODO : cut the sample into blocks?

        Parameters
        ----------
        X : OpenTURNS.Sample
            The input sample.

        Returns
        -------
        Y : OpenTURNS.Sample
            The output sample.
        """
        job = self.slurm_machine.create(X)
        command = self.slurm_machine.submit()
        # Wait until finished
        tempo = 0.0
        finished = False
        while not finished and tempo < self.timeout:
            if self.verbose:
                print(f"Wait for results after {tempo}")
            tempo += self.wait_time
            time.sleep(self.wait_time)
            finished = job.is_finished()

        _, Y = job.get_input_output(self.verbose)
        return Y

    def __str__(self):
        """
        Convert the object into a string.

        This method is typically called with the "print" statement.

        Parameters
        ----------
        None.

        Returns
        -------
        s: str
            The string corresponding to the object.
        """
        s = ""
        s += f"machine = {self.slurm_machine}\n"
        s += f"wait_time = {self.wait_time}\n"
        s += f"timeout = {self.timeout}\n"
        s += f"verbose = {self.verbose}\n"
        return s
