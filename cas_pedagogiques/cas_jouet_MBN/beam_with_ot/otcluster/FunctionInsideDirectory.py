#!/usr/bin/env python

"""
Evaluates a function inside a directory.

TODO : Finish this.
"""

import openturns as ot
import os
import shutil
from uuid import uuid4

class FunctionInsideDirectory(ot.OpenTURNSPythonFunction):
    def __init__(
        self,
        base_function,
        main_directory,
        simulation_directory="evaluation_",
        cleanup_on_delete=False,
        verbose=False,
    ):
        """
        Evaluates the beam model inside a directory.
        
        TODO: implement a cleanup_on_success
        
        TODO: what happens within a parallel framework?

        Parameters
        ----------
        base_function : ot.Function()
            The function.
        main_directory : str
            The name of the main simulation directory
        simulation_directory : str
            The prefix of the simulation sub-directories.
            The actual name of each simulation directory is main_directory/simulation_directory_counter
            where counter is the number of evaluations of the function.
        cleanup_on_delete : bool
            If True, then deletes the main_directory when the object is deleted.
            Otherwise, keep the directory.
            This can be handy to check each function evaluation.
        verbose : bool
            Set to True to print intermediate messages
        """
        if not isinstance(base_function, ot.Function):
            raise ValueError(
                f"The model must be a ot.Function, but "
                f"model has type {type(base_function)}."
            )
        self.base_function = base_function
        self.verbose = verbose
        if os.path.isdir(main_directory):
            raise ValueError(f"The directory {main_directory} already exists.")
        self.main_directory = main_directory
        self.simulation_directory = simulation_directory
        self.cleanup_on_delete = cleanup_on_delete
        # Create the function
        super().__init__(
            base_function.getInputDimension(), base_function.getOutputDimension()
        )
        self.setInputDescription(base_function.getInputDescription())
        self.setOutputDescription(base_function.getOutputDescription())
        # Create the main directory, if possible
        if self.verbose:
            print("Create directory = ", main_directory)
        try:
            os.mkdir(main_directory)
        except FileExistsError as err:
            print(err)
            print(f"WARNING: the following folder already existed: {main_directory}")
            pass

    def _exec(self, X):
        """Evaluate the model for a single point :math:`X`.

        Parameters
        ----------
        X : sequence of floats
            Input vector.

        Returns
        -------
        Y : sequence of floats
            Output vectory.
        """
        # Gets the current directory
        cwd = os.getcwd()
        # Creates unique suffix
        suffix = uuid4().hex[0:6]
        # Create simulation directory
        local_simulation_directory = os.path.join(
            self.main_directory, self.simulation_directory + f"{suffix}"
        )
        if self.verbose:
            print("Create directory = ", local_simulation_directory)
        try:
            os.mkdir(local_simulation_directory)
        except FileExistsError as err:
            print(err)
            print(
                f"WARNING: the following folder already existed: {local_simulation_directory}"
            )
            pass
        # Gets into it
        os.chdir(local_simulation_directory)
        # Evaluates the function
        Y = self.base_function(X)
        # Go back to the origin directory
        os.chdir(cwd)
        return Y

    def __del__(self):
        # Remove directory, even if there are sub-directories
        if self.cleanup_on_delete:
            shutil.rmtree(self.main_directory, ignore_errors=True)
