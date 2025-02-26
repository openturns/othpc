#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari, Joseph Muré
"""

import openturns as ot
import openturns.coupling_tools as otct
from otwrap import OpenTURNSWrapper

class SLURMJobArrayWrapper(OpenTURNSWrapper):
    """
    The aim of this class is to plug an black-box model to an OpenTURNS.PythonFunction object in a HPC environment. 
    This class gives an example of a HPC wrapper for an executable black-box model using the Job Array option from SLURM (see e.g., https://slurm.schedmd.com/job_array.html). 
    This class inherits the methods and attributes from the base class "OpenTURNSWrapper" and uses the same cantilever beam example. 

    Examples
    --------
    >>> input_file_path = "input_doe/doe.csv"
    >>> df_doe = pd.read_csv(input_file_path, index_col=0).reset_index()
    >>> X = ot.Sample.BuildFromDataFrame(df_doe)
    >>> my_wrapper = SLURMJobArrayWrapper(input_dimension=df_doe.shape[1], output_dimension=1, index_col=0)
    >>> g = my_wrapper.get_function()
    >>> Y = g(X)
    """
    def __init__(self, input_dimension, output_dimension, index_col=None):
        # Inherit methods and attributes from the base class "OpenTURNSWrapper"
        super().__init__(input_dimension=input_dimension, output_dimension=output_dimension, index_col=index_col)

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
        indexes_string = [str(val) for val in indexes]
        indexes_string = ",".join(indexes_string)
        otct.execute(f"sbatch --array={indexes_string} --nodes={self.slurm_resources["nodes-per-job"]} --cpus-per-task={self.slurm_resources["cpus-per-job"]} --mem={self.slurm_resources["mem-per-job"]} --time={self.slurm_resources["timeout"]} jobarray_launcher.sh {self.date_tag}")
        Y = self._parse_outputs(indexes)
        return Y
