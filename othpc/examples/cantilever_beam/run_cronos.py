#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""
import othpc
import openturns as ot
from cantilever_beam import CantileverBeam

X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
cb = CantileverBeam("template/beam_input_template.xml", "template/beam")
dw = othpc.DaskFunction(cb)
dwfun = ot.Function(dw)
Y = dwfun(X)
print(Y)