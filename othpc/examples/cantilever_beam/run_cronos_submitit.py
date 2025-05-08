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
dw = othpc.SubmitItFunction(cb, tasks_per_job=2, cpus_per_job=2, timeout_per_job=5)
dwfun = ot.Function(dw)
#
X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
Y = dwfun(X)
print(Y)
othpc.make_summary_file("my_results", summary_file="summary_table.csv")
