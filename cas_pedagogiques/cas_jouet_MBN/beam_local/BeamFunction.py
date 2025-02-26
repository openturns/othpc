#!/usr/bin/env python

"""
A wrapper of the beam function in OpenTURNS.

Source : 
https://github.com/openturns/otwrapy/blob/master/otwrapy/examples/beam/wrapper.py

With modifications from Michaël Baudin (septembre 2024)
"""

import openturns as ot
import openturns.coupling_tools as otct
import os
import time
from xml.dom import minidom

__all__ = ["BeamFunction"]


class BeamFunction(ot.OpenTURNSPythonFunction):

    def __init__(
        self,
        input_template_filename,
        beam_executable,
        sleep=0.0,
        beam_option="-x",
        actual_beam_filename="beam.xml",
        beam_output_filename="_beam_outputs_.xml",
        verbose=False,
    ):
        """
        Wrapper of a C++ code that computes the deviation of a beam.

        The C++ code computes the deviation with the given formula:

        .. math::

            y = \\frac{FL^{3}}{3EI}

        with :

        - :math:`E` : Young modulus
        - :math:`F` : Load
        - :math:`L` : Length
        - :math:`I` : Inertia

        The wrapped code is an executable that is run from the shell as follows :

        .. code-block:: sh

            $ ./beam -x beam.xml

        where :file:`beam.xml` is the input file containing the four parameters
        :math:`E, F, L, I`.

        The output of the code is an xml output file :file:`_beam_outputs_.xml`
        containing the deviation and its derivates.

        Parameters
        ----------
        input_template_filename : string
            The name of the template input file.
            This file is not necessarily located in simulation_directory,
            because it is read, but not written.
        beam_executable : string
            The command to run the program.
            This file is not necessarily located in simulation_directory,
            because it is read, but not written.
        sleep : float
            Intentional delay (in seconds) to demonstrate the effect of
            parallelizing.
        beam_option : string
            The option given to the program, in front of the actual input file.
        actual_beam_filename : string
            The name of the actual input XML file
            This file is written in the current directory.
        beam_output_filename : string
            The name of the output file of the beam program
            This file is written in the current directory.
        verbose : bool
            Set to True to print intermediate messages
        """

        if not os.path.isfile(input_template_filename):
            raise ValueError(
                f"The input template {input_template_filename} file does not exist."
            )
        self.input_template_filename = input_template_filename
        if not os.path.isfile(beam_executable):
            raise ValueError(f"The executable {beam_executable} does not exist.")
        self.beam_executable = beam_executable
        self.command = f"\"{self.beam_executable}\" {beam_option} {actual_beam_filename}"
        self.actual_beam_filename = actual_beam_filename
        self.beam_output_filename = beam_output_filename
        self.beam_option = beam_option
        self.sleep = sleep
        self.verbose = verbose

        # Number of input/output values:
        super().__init__(4, 1)
        self.setInputDescription(["Young modulus", "Load", "Length", "Inertia"])
        self.setOutputDescription(["Deviation"])

    def _exec(self, X):
        """Evaluate the model for a single point :math:`X`.

        This is the default OpenTURNS method that executes the function on a
        given point.
        Semantically speaking, the function is divided in three parts :

        - Create an input file with values of :math:`X`
        - Run the executable on the shell
        - Read the value of the output from the XML output file

        The three steps are executed in the current working directory.

        Parameters
        ----------
        X : sequence of floats
            Input vector of dimension 4 on which the model will be evaluated: E, F, L, I.

        Returns
        -------
        Y : sequence of 1 float
            The deviation of the beam.
        """
        X = ot.Point(X)  # ot.MemoryView > ot.Point
        if self.verbose:
            print(f"Execute beam at {X}")
        # Create intentional delay
        time.sleep(self.sleep)

        # Create actual input file from templace and X
        if self.verbose:
            print(
                f"From {self.input_template_filename}, write {self.actual_beam_filename}"
            )
        otct.replace(
            self.input_template_filename,
            self.actual_beam_filename,
            ["@E@", "@F@", "@L@", "@I@"],
            X,
        )
        # Execute
        time_start = time.time()
        if self.verbose:
            print(f'Execute: "{self.command}"')
        cp = otct.execute(self.command, shell=True)
        time_stop = time.time()
        # Read return code
        if cp.returncode != 0:
            raise ValueError(f"Beam return code = {cp.returncode}")
        # Read output
        if self.verbose:
            print(f"Read {self.beam_output_filename}")
        xmldoc = minidom.parse(self.beam_output_filename)
        itemlist = xmldoc.getElementsByTagName("outputs")
        deviation = float(itemlist[0].attributes["deviation"].value)
        if self.verbose:
            print(f"Y = {deviation}")
        Y = [deviation]
        return Y

    def getInputDistribution(self):
        """
        Returns the input distribution of the beam model

        Returns
        -------
        distribution : ot.Distribution(4)
            The input distribution of the beam model.
        """
        # Young's modulus E
        E = ot.Beta(0.9, 3.5, 65.0e9, 75.0e9)  # in N/m^2
        E.setDescription("E")
        E.setName("Young modulus")

        # Load F
        F = ot.LogNormal()  # in N
        F.setParameter(ot.LogNormalMuSigma()([300.0, 30.0, 0.0]))
        F.setDescription("F")
        F.setName("Load")

        # Length L
        L = ot.Uniform(2.5, 2.6)  # in m
        L.setDescription("L")
        L.setName("Length")

        # Moment of inertia I
        II = ot.Beta(2.5, 4.0, 1.3e-7, 1.7e-7)  # in m^4
        II.setDescription("I")
        II.setName("Inertia")

        # correlation matrix
        R = ot.CorrelationMatrix(4)
        R[2, 3] = -0.2
        copula = ot.NormalCopula(
            ot.NormalCopula.GetCorrelationFromSpearmanCorrelation(R)
        )
        distribution = ot.ComposedDistribution([E, F, L, II], copula)
        return distribution
