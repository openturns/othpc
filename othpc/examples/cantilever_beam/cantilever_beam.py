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
from datetime import datetime
from xml.dom import minidom
import subprocess


class CantileverBeam(ot.OpenTURNSPythonFunction):
    def __init__(self, input_template_file, executable_file):
        super().__init__(4, 1)
        # Check that the files and folders do exist
        if not os.path.isfile(input_template_file):
            raise ValueError(
                f"The input template {input_template_file} file does not exist."
            )
        self.input_template_file = os.path.abspath(input_template_file)
        #
        if not os.path.isfile(executable_file):
            raise ValueError(f"The executable {executable_file} does not exist.")
        self.executable_file = os.path.abspath(executable_file)
        #
        date_tag = datetime.now().strftime("%d-%m-%Y_%H-%M")
        self.work_dir = os.path.join(os.getcwd(), f"workdir_{date_tag}")

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
            os.path.join(simulation_directory, 'beam_input.xml'),
            ['@F@', '@E@', '@L@', '@I@'],
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
            xmldoc = minidom.parse(os.path.join(simulation_directory, '_beam_outputs_.xml'))
            itemlist = xmldoc.getElementsByTagName('outputs')
            Y = float(itemlist[0].attributes['deviation'].value)
        except FileNotFoundError as err:
            print(err)
            print(f"WARNING: the following file was not found: {simulation_directory}")
            Y = float('nan')
        return Y

    def _exec(self, x):
        """
        Executes one evaluation of the black-box model for one input x. 

        Parameters
        ----------
        x : list
            Input point to be evaluated, in this example, inputs are (F, E, L, I).
        """
        with othpc.TempWorkDir(work_dir=self.work_dir) as simu_dir:
            # Create input files
            self._create_input_files(x, simu_dir)
            # Execution
            subprocess.run([self.executable_file, "-x", "beam_input.xml"], check=True, cwd=simu_dir)
            # Parse outputs
            Y = self._parse_output(simu_dir)
        return [Y]

