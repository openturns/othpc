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
my_results_directory = os.path.abspath("my_results")
cb = CantileverBeam(input_template_file, executable_file, my_results_directory)
# cb = CantileverBeam("template/beam_input_template.xml", "template/beam", "my_results")
dw = othpc.DaskFunction(cb, csv_dump_file="my_results/inout_summary.csv")
dwfun = ot.Function(dw)
#
X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
Y = dwfun(X)
print(Y)