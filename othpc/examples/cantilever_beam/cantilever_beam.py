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

from xml.dom import minidom

class CantileverBeam(ot.OpenTURNSPythonFunction):
    """
    This class allows to evaluate the executable of the cantilever beam on various input points. 

    Parameters: 
    ----------
    input_template_file : str
        This input file has been modified with tags replacing the numerical values of the input variables. 
        
    executable_file : str
        TBD

    results_directory : str 
        TBD
    """
    def __init__(self, input_template_file, executable_file, results_directory):
        super().__init__(4, 1)
        #
        if not os.path.isfile(input_template_file):
            raise ValueError(f"The input template {input_template_file} file does not exist.")
        self.input_template_file = os.path.abspath(input_template_file)
        #
        if not os.path.isfile(executable_file):
            raise ValueError(f"The executable {executable_file} does not exist.")
        self.executable_file = os.path.abspath(executable_file)
        #
        if not os.path.exists(results_directory):
            raise ValueError(f"The working directory {results_directory} does not exist.")
        self.results_directory = os.path.abspath(results_directory)


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
            y = float(itemlist[0].attributes['deviation'].value)
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
        temp_simu_dir_maker = othpc.TempSimuDir(res_dir=self.results_directory)
        with temp_simu_dir_maker as simu_dir:
            # Create input files
            self._create_input_files(x, simu_dir)
            # Execution
            try: 
                otct.execute(f"{self.executable_file} -x beam_input.xml", cwd=simu_dir)
            except RuntimeError:
                # TODO: implement a logging option 
                return [float("nan")]
            # Parse outputs
            y = self._parse_output(simu_dir)
            # Write input-output summary csv file
            temp_simu_dir_maker.make_summary_file(x, [y], "summary.csv")
        return [y]

# TODO 
# ----
# Modify the beam example to include requirement file that should be copied in each simu_dir
# Work on cache management. Case when I have existing simulations >> the summary_table should be loaded in a MemoizeFunction.  
# Improve description management in summary files and table
# 

# QUESTIONS 
# ---------
# What are the arguments in the exit from TempSimuDir?
