#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari
"""

import os
import pickle
import pandas as pd
import openturns as ot
import openturns.coupling_tools as otct
from argparse import ArgumentParser, FileType

from wrapper_base import OpenTURNSWrapper

class GlostWrapper(OpenTURNSWrapper):
    """
    The aim of this class is to plug an black-box model to an OpenTURNS.PythonFunction object in a HPC environment. 
    This class gives an example of a HPC wrapper for an executable black-box model using the module GLOST (Greedy Launcher Of Small Tasks), developed by the CEA (see https://github.com/cea-hpc/glost/tree/master). 
    This class inherits the methods and attributes from the base class "OpenTURNSWrapper" and uses the same cantilever beam example. 

    Parameters
    ----------
    batch_size : integer        
        This parameter defines the number of evaluations (i.e., tasks) gathered in a single job.  
        Then, the number of batches correspond to the number of jobs simultaneously submitted to SLURM. 
        Since jobs requesting large amounts of resources are unlikely to have the priority, it is recommended to split the tasks between multiple jobs. 
        In the case of a sequential back-box model (i.e, requiring one CPU per evaluation), one should split the evaluation of a design of experiments into several small jobs. 
        

    Examples
    --------
    >>> input_file_path = "input_doe/doe.csv"
    >>> df_doe = pd.read_csv(input_file_path, index_col=0).reset_index()
    >>> X = ot.Sample.BuildFromDataFrame(df_doe)
    >>> my_wrapper = GlostWrapper(input_dimension=df_doe.shape[1], output_dimension=1, index_col=0, batch_size=5)
    >>> g = my_wrapper.get_function()
    >>> Y = g(X)
    """
    def __init__(self, input_dimension, output_dimension, index_col=None, batch_size=1):
        # Inherit methods and attributes from the base class "OpenTURNSWrapper"
        super().__init__(input_dimension=input_dimension, output_dimension=output_dimension, index_col=index_col)
        self.batch_size = batch_size
        # Write an executable file
        f = open("glost/glost_exe.sh", "w")
        f.write(
f"""
#!/bin/bash

cd {self.results_dir}/SIMU_$1
{self.base_dir}/template/beam -x beam_input.xml
"""
        )
        f.close()

    def _exec_sample(self, X):
        """
        Launches the parallel evaluations black-box model evaluated at the input design of experiments X. 

        Parameters
        ----------
        X : OpenTURNS.Sample
            This input design of experiment should present an evaluation index in the first colum. 
            Since this example presents four inputs (F, E, L, I), the number of columns is five. 
            The number of rows defines the number of evaluations. 
        
        Returns
        -------
        Y : OpenTURNS.Sample
            This object contains the output results. 
            Here, the output is of dimension one, therefore, Y is a vector. 
        """
        X = ot.Sample(X)
        indexes = self._set_indexes(X)
        if self.index_col is not None: 
            X = self._drop_index_col(X)
        self._build_subtree(X, indexes)
        doe_size = len(indexes)

        if doe_size % self.batch_size==0:
            batch_nb = doe_size // self.batch_size
        else:
            batch_nb = (doe_size // self.batch_size) + 1

        for batch_idx in range(batch_nb):
            if batch_idx==(batch_nb-1):
                batch_indexes = indexes[batch_idx * self.batch_size:]
            else:
                batch_indexes = indexes[batch_idx * self.batch_size : (batch_idx + 1) * self.batch_size]
            batch_indexes_string = [str(val) for val in batch_indexes]
            batch_indexes_string = " ".join(batch_indexes_string)
            otct.execute(f"sbatch --cpus-per-task={self.batch_size} --nodes={self.slurm_resources["nodes-per-job"]} --mem={self.slurm_resources["mem-per-job"]} --time={self.slurm_resources["timeout"]} glost_launcher.sh {batch_idx} {batch_indexes_string}")
        Y = self._parse_outputs(indexes)
        return Y


if __name__ == "__main__":
    ## Usage 1: "python wrapper_jobarray.py input_doe/doe.csv &"
    ## Adding the "nohup" option allows to run the python process in a background on one frontal HPC node, even after a disconnection:
    ## Usage 2: "nohup python -u wrapper_jobarray.py input_doe/doe.csv 2>&1 &" 

    # Input file parser
    parser = ArgumentParser()
    parser.add_argument("inputfile", type=FileType("r"), help="input file defining the design of experiments to evaluate")
    args = parser.parse_args()
    input_file_path = os.path.join("./", args.inputfile.name)
    X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")

    # Declare Wrapper class
    my_wrapper = GlostWrapper(input_dimension=X.getDimension(), output_dimension=1, index_col=0, batch_size=5)
    g = my_wrapper.get_function(previous_evals_file="beam_evals.pkl")
    Y = g(X)
    # Save evaluations in a pickle file
    with open("beam_evals.pkl", "wb") as ot_study:
        pickle.dump(g, ot_study)
    # Save evaluations in an input output file  
    XY = my_wrapper.make_inputoutput_file(g, X)
    print(XY)
