#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""
import os
import time
import openturns as ot
import openturns.coupling_tools as otct
import othpc
from subprocess import CalledProcessError
from xml.dom import minidom
from othpc.utils import fake_load


class CantileverBeam(ot.OpenTURNSPythonFunction):
    """
    This class allows to evaluate the executable of the cantilever beam on various input points.

    Parameters:
    ----------
    results_directory : str
        Name of the result directory where the result sub-folders are written.

    n_cpus : integer
        Number of parallel evaluations realized by multiprocessing.

    fake_load_time : int
        Duration in seconds of a fake computational load used to simulate long computations.
    """

    def __init__(self, results_directory, n_cpus=1, fake_load_time=10):
        super().__init__(4, 1)
        self.setInputDescription(["F", "E", "L", "I"])
        self.setOutputDescription(["Y"])
        self.fake_load_time = fake_load_time
        #
        template_dir = os.path.join(os.path.dirname(__file__), "template")
        input_template_file = os.path.join(template_dir, "beam_input_template.xml")
        if not os.path.isfile(input_template_file):
            raise ValueError(
                f"The input template {input_template_file} file does not exist."
            )
        self.input_template_file = input_template_file
        #
        license_file = os.path.join(template_dir, "LICENCE.xml")
        if not os.path.isfile(license_file):
            raise ValueError(f"The license file {license_file} does not exist.")
        self.license_file = license_file
        executable_file = os.path.join(template_dir, "beam")
        if not os.path.isfile(executable_file):
            raise ValueError(f"The executable {executable_file} does not exist.")
        self.executable_file = executable_file
        #
        results_directory = os.path.abspath(results_directory)
        try:
            os.mkdir(results_directory)
        except FileExistsError:
            pass
        self.results_directory = results_directory
        self.n_cpus = n_cpus

    def _create_input_files(self, x, simulation_directory):
        """
        Creates one input file which includes the values of the input point x.

        Parameters
        ----------
        x : list
            Input point to be evaluated, in this example, inputs are (F, E, L, I).

        simulation_directory : str
            Simulation directory dedicated to the evaluation of the input point x.
        """
        # Creation du fichier d'entree
        otct.replace(
            # File template including your tokens to be replaced by values from a design of exp.
            self.input_template_file,
            # File written after replacing the tokens by the values in X
            os.path.join(simulation_directory, "beam_input.xml"),
            ["@F@", "@E@", "@L@", "@I@"],
            [x[0], x[1], x[2], x[3]],
        )

    def _parse_output(self, simulation_directory):
        """
        Parses outputs in the simulation directory related to one evaluation and returns output value.

        Parameters
        ----------
        simulation_directory : str
            Simulation directory dedicated to the evaluation of the input point x.
        """
        # Lecture de la sortie
        try:
            xmldoc = minidom.parse(
                os.path.join(simulation_directory, "_beam_outputs_.xml")
            )
            itemlist = xmldoc.getElementsByTagName("outputs")
            y = float(itemlist[0].attributes["deviation"].value)
        except FileNotFoundError as err:
            print(err)
            print(f"WARNING: the following file was not found: {simulation_directory}")
            y = float("nan")
        return y

    def _exec(self, x):
        """
        Executes one evaluation of the black-box model for one input x.

        Parameters
        ----------
        x : list
            Input point to be evaluated, in this example, inputs are (F, E, L, I).
        """
        with othpc.TempSimuDir(
            res_dir=self.results_directory, to_be_copied=[self.license_file]
        ) as simu_dir:
            # Create input files
            self._create_input_files(x, simu_dir)
            # Execution
            try:
                otct.execute(
                    f"{self.executable_file} -x beam_input.xml",
                    cwd=simu_dir,
                    capture_output=True,
                )
                # Parse outputs
                y = self._parse_output(simu_dir)
                fake_load(
                    self.fake_load_time
                )  # Creates a fake load simulator for x sec.
                print(f"RUN {simu_dir[-30:]} - {time.ctime(time.time())}")
            except CalledProcessError as error:
                othpc.evaluation_error_log(
                    error, simu_dir, "CantileverBeam_RuntimeError.txt"
                )
                y = float("nan")
            # Write input-output summary csv file
            othpc.make_report_file(simu_dir, x, [y])
        return [y]
