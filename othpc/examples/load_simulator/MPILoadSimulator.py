#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""
import os
import openturns as ot
import openturns.coupling_tools as otct
import othpc
from subprocess import CalledProcessError

class MPILoadSimulator(ot.OpenTURNSPythonFunction):
    """
    TBD
    """
    def __init__(self, executable_file="./bin/myMPIProgram", nb_mpi_proc=10, simu_duration=10, nb_slurm_nodes=1, slurm_timeout=5, results_directory="my_results"):
        super().__init__(2, 1)
        #
        if not os.path.isfile(executable_file):
            raise ValueError(f"The executable {executable_file} does not exist.")
        self.executable_file = os.path.abspath(executable_file)
        #
        if not os.path.exists(results_directory):
            raise ValueError(f"The working directory {results_directory} does not exist.")
        self.results_directory = os.path.abspath(results_directory)
        self.nb_mpi_proc = nb_mpi_proc
        self.nb_slurm_nodes = nb_slurm_nodes
        self.simu_duration = simu_duration
        self.slurm_timeout = slurm_timeout

    def _parse_output(self, simulation_directory):
        """
        Parses outputs in the simulation directory related to one evaluation and returns output value. 

        Parameters
        ----------
        simulation_directory : str
            Simulation directory dedicated to the evaluation of the input point x. 
        """
        try:
            result_file = open(os.path.join(simulation_directory, 'result.txt'), "r")
            lines = result_file.readlines()
            y = float(lines[-1].split(":")[-1])
            result_file.close()
        except FileNotFoundError as err:
            print(err)
            print(f"WARNING: the following file was not found: {simulation_directory}")
            y = float('nan')
        return y

    def _exec(self, x):
        """
        Executes one evaluation of the black-box model for one input x. 

        Parameters
        ----------
        x : list
            Input point to be evaluated, in this example, inputs are (F, E, L, I).
        """
        with othpc.TempSimuDir(res_dir=self.results_directory) as simu_dir:
            # Execution
            try: 
                otct.execute(f"salloc --nodes={self.nb_slurm_nodes} --ntasks-per-node={self.nb_mpi_proc//self.nb_slurm_nodes} --time={self.slurm_timeout} --wckey=P120K:SALOME mpiexec -n {self.nb_mpi_proc} {self.executable_file} {x[0]} {x[1]} --cpu-interval={self.simu_duration}", shell=True, cwd=simu_dir)
                print("SBATCH DONE")
                # Parse outputs
                y = self._parse_output(simu_dir)
            except CalledProcessError as error:
                # othpc.evaluation_error_log(error, simu_dir, "CantileverBeam_RuntimeError.txt")
                y = float("nan")
            # Write input-output summary csv file
            # othpc.make_report_file(simu_dir, x, [y])
        return [y]


if __name__ == "__main__":
    g = MPILoadSimulator()
    X = [[1, 2], [3, 4]]
    Y = g(X)
    print(Y)
