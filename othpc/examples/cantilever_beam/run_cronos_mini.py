#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""
import othpc
import openturns as ot
from cantilever_beam import CantileverBeam

cb = CantileverBeam("template/beam_input_template.xml", "template/beam", "my_results")
dw = othpc.DaskFunction(cb, nodes_per_job=1, cpus_per_job=95, job_number=1, verbose=True)
X = ot.Sample.ImportFromCSVFile("input_doe/doe100.csv", ",")
Y = dw(X)
print(Y)
othpc.make_summary_file("my_results", summary_file="summary_table.csv")