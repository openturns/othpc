#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2024

@authors: Elias Fekhari
"""

import os
import time
import pickle
import openturns as ot
from datetime import datetime


class OpenTURNSWrapper:
    """
    The aim of this base class is to plug an black-box model to an OpenTURNS.PythonFunction object in a HPC environment. 
    Here, the toy-case model used to illustrate the present class is a C++ code that computes the deviation of a cantilever beam.
    Further details regarding this toy-case are available in https://openturns.github.io/openturns/latest/usecases/use_case_cantilever_beam.html. 
    
    Parameters
    ----------
    input_dimension : integer
        Input dimension of the wrapper.

    output_dimension : integer
        Output dimension of the wrapper. 

    index_col : integer
        This variable is set to None by default, otherwise, it can be used to set the index column for a design of experiments to evaluate.
    """
    def __init__(self, input_dimension, output_dimension, index_col=None):
        self.input_dimension = input_dimension
        self.output_dimension = output_dimension
        self.index_col = index_col
        # When the index column is not defined ahead
        if index_col is None:
            # Keeps track of the last index evaluated
            self.last_index = 0

        self.slurm_resources = {
        "nodes-per-job": 1,
        "cpus-per-job": 1,
        "mem-per-job": 512, # 512 MB
        "timeout": "00:05:00", # 5 minutes
        "nb-jobs": 1
        }

        date_time = datetime.now()
        self.date_tag = date_time.strftime("%d-%m-%Y_%H-%M")
        # Current directory
        self.work_dir = os.getcwd()
        # Create current directory
        self.results_dir = os.path.join(self.work_dir, "results_" + self.date_tag)
        try: 
            os.mkdir(self.results_dir)
        except FileExistsError as err:
            print(err)
            print(f"WARNING: the following folder already existed: {self.results_dir}")
            pass

    def _build_subtree(self, X, indexes):
        """
        Builds the tree of results folders corresponding to an input design of experiment X to be evaluated. 
        The results of each evaluation of the black-box model are stored in the following structure: 
        ├── cantilever_beam
        |   ├── template
        |   ├── input_doe
        |   ├── wrapper_jobarray.py
        |   ├── results_26-08-2024_14-57
        |   |    ├── SIMU_157
        |   |    ├── SIMU_756
        |   |    ├── ...
        Note that the folders indexes correspond to the first column from the input design of experiment X.

        Parameters
        ----------
        X : OpenTURNS.Sample
            Input design of experiment to be evaluated. 
        
        indexes : list
            List of indexes associated with each row of the sample X.
        """
        for r, i in enumerate(indexes):
            xsimu_dir = os.path.join(self.results_dir, f"SIMU_{i}")
            try:
                os.mkdir(xsimu_dir)
            except FileExistsError as err:
                print(err)
                print(f"WARNING: the following folder already existed: {xsimu_dir}")
                pass
            self.replace(X, r, xsimu_dir)
            
    def replace(self, X, r, xsimu_dir):
        """
        TBD

        I personally think that giving the entire _build_subtree method to the user might be easier
        """
        # raise NotImplementedError
        raise AttributeError("The replace() method must be adapted to your case! See the documentation example.")

    def _drop_index_col(self, X):
        """
        Drops the index column when present in the sample X. 

        Parameters
        ----------
        X : OpenTURNS.Sample
            Input design of experiment to be evaluated. 

        Returns
        -------
        X : OpenTURNS.Sample
            Input design of experiment to be evaluated, without the index column.
        """
        cols = list(range(self.input_dimension))
        cols.remove(self.index_col)
        return X[:, cols]
    
    def _parse_outputs(self, indexes):
        """
        Retrieves the outputs of the black-box model evaluated at the input design of experiments X.  

        Parameters
        ----------
        indexes : list
            List of indexes associated with each row of the sample X.
        
        Returns
        -------
        Y : OpenTURNS.Sample
            This object contains the output results. 
            Here, the output is of dimension one, therefore, Y is a vector. 
        """
        # Make sure that all the output files exist
        tempo = 0
        output_file_list = [os.path.join(self.results_dir, f"SIMU_{int(i)}", "_beam_outputs_.xml") for i in indexes]
        
        while sum([os.path.exists(output_file) for output_file in output_file_list]) < len(indexes):
            tempo += 5
            time.sleep(5)
            if tempo == 60 * self.slurm_resources["timeout"]:
                raise FileNotFoundError
        Y = []
        for i in indexes:
            xsimu_dir = os.path.join(self.results_dir, f"SIMU_{i}")
            try:
                y = self.parse_output(xsimu_dir)
                Y.append([y])
            except FileNotFoundError as err:
                print(err)
                print(f"WARNING: the following file was not found: {xsimu_dir}")
                Y.append([float('nan')])
                pass
        return Y
    
    def parse_output(self, xsimu_dir): 
        # raise NotImplementedError
        raise AttributeError("The parse_output() method must be adapted to your case! See the documentation example.")

    def _set_indexes(self, X):
        """
        Returns a list of indexes associated with each row of the sample X. 
        The indexes can either be included as a column of the sample X or automatically defined. 

        Parameters
        ----------
        X : OpenTURNS.Sample
            Input design of experiment to be evaluated. 

        Returns
        -------
        indexes : list
            List of indexes associated with each row of the sample X.
        """
        if self.index_col is not None: 
            indexes = [int(val[0]) for val in X[:, 0]]
            # Check that all indexes are unique 
            if len(indexes) > len(set(indexes)): 
                raise ValueError("Some rows in the input design of experiment have the same index!")
        else:
            indexes = list(range(self.last_index, self.last_index + len(X[:, 0])))
            self.last_index = self.last_index + len(X[:, 0])
        return indexes
    
    @staticmethod
    def _set_function_cache(function, previous_evals_file=None):
        """
        This method starts a cache mechanism based on the OpenTURNS.MemoizeFunction to save in each input-output calls associated to the function. 
        Loads the previous wrapper evaluations which were stored in a pickle file. 
        
        Parameters
        ----------
        function : OpenTURNS.PythonFunction
            OpenTURNS object allowing to call the black-box model in a Python environment. 
        
        previous_evals_file: string
            This pickle file should store the previous evaluations of the same exact wrapper. 

        Returns
        -------
        memoize_function: OpenTURNS.MemoizeFunction
            This object carries the previous calls to the wrapper.  
        """
        # Define the memoize function, saving all the function calls in cache 
        memoize_function = ot.MemoizeFunction(function)
        if previous_evals_file is not None: 
            try: 
                # Load previous function 
                with open(previous_evals_file, "rb") as ot_study:
                    previous_function = pickle.load(ot_study)
                # Load input-output tuples previously evaluated and stored in a pickle file
                if function.getDescription() == previous_function.getDescription():
                    memoize_function.addCacheContent(previous_function.getCacheInput(), previous_function.getCacheOutput())
            except FileNotFoundError as err:
                print(err)
                print(f"WARNING: the following file was not found: {previous_evals_file}")
                pass
        return memoize_function
    
    def get_function(self, previous_evals_file=None):
        """
        Accessor to the OpenTURNS.PythonFunction calling the wrapper. 

        Parameters
        ----------
        previous_evals_file: string
            This pickle file should store the previous evaluations of the same exact wrapper. 

        Returns
        -------
        memoize_function: OpenTURNS.MemoizeFunction
            This object saves in cache the calls to the wrapper, possibly including previous calls saved in a pickle file passed as an input.
        """
        # Define an OT function
        g = ot.PythonFunction(self.input_dimension, self.output_dimension, func_sample=self._exec_sample)
        # Load previous evaluations of this wrapper, stored in the pickle file
        g_memoize = self._set_function_cache(g, previous_evals_file)
        return g_memoize

    def make_inputoutput_file(self, function, X, remove_out_dir=False):
            """
            Makes a csv file gathering the input design of experiments and the corresponding outputs executed. 
            
            Parameters
            ----------
            function : OpenTURNS.MemoizeFunction
                This object saved in cache the inputs-outputs evaluations of the wrapper.

            X : OpenTURNS.Sample
                Input design of experiment that was evaluated.

            remove_out_dir : Boolean
                when set to True, all the output directories are deleted after saving the input-outputs couples in a .csv file.

            Returns
            -------
            XY : OpenTURNS.Sample
                Stacked inputs and the corresponding outputs evaluated.
            """

            if function.getClassName() != "MemoizeFunction":
                raise TypeError("The function used should be an OpenTURNS.MemoizeFunction to set the cache mechanism.")            
            XY = function.getInputHistory()
            XY.setDescription(X.getDescription())
            Y = function.getOutputHistory()
            Y.setDescription(function.getOutputDescription())
            XY.stack(Y)
            XY.exportToCSVFile(os.path.join(self.results_dir, "inout_results.csv"), ',')
            if remove_out_dir: 
                os.system(f"rm -r {self.results_dir}/SIMU_*")
            return XY


