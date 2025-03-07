#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""
import os
import othpc
import openturns as ot
from cantilever_beam import CantileverBeam

input_template_file = "template/beam_input_template.xml"
executable_file = "template/beam"
my_results_directory = "my_results"
try: 
    os.mkdir(my_results_directory)
except FileExistsError:
    pass
cb = CantileverBeam(input_template_file, executable_file, my_results_directory)
# X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
X = ot.Sample.ImportFromCSVFile("input_doe/doe_with_failure.csv", ",")
Y = cb(X)
print(Y)
othpc.make_summary_file(my_results_directory)
