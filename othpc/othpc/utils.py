#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: otwrapy
"""
from datetime import datetime
from tempfile import mkdtemp
import pandas as pd
import shutil
import os
import openturns as ot


class TempSimuDir(object):

    """
    Implement a context manager that creates a temporary working directory.

    Create a temporary working directory on `work_dir` preceded by
    `prefix` and clean up at the exit if necessary.
    See: http://sametmax.com/les-context-managers-et-le-mot-cle-with-en-python/

    Parameters
    ----------
    work_dir : str (optional)
        Root path where the temporary working directory will be created. If None,
        it will default to the platform dependant temporary working directory
        Default = None

    prefix : str (optional)
        String that preceeds the directory name.
        Default = 'run-'

    cleanup : bool (optional)
        If True erase the directory and its children at the exit.
        Default = False

    transfer : list (optional)
        List of files or folders to transfer to the temporary working directory

    Examples
    --------
    In the following example, everything that is executed inside the `with`
    environment will happen at a temporary working directory created at
    :file:`/tmp` with :file:`/run-` as a prefix. The created directory will be
    erased upon the exit of the  `with` environment and python will go
    back to the preceding working directory, even if an Exception is raised.

    >>> import otwrapy as otw
    >>> import os
    >>> print "I'm on my project directory"
    >>> print os.getcwd()
    >>> with otw.TempWorkDir('/tmp', prefix='run-', cleanup=True):
    >>>     #
    >>>     # Do stuff
    >>>     #
    >>>     print "..."
    >>>     print "Now I'm in a temporary directory"
    >>>     print os.getcwd()
    >>>     print "..."
    >>> print "I'm back to my project directory :"
    >>> print os.getcwd()
    I'm on my project directory
    /home/aguirre/otwrapy
    ...
    Now I'm in a temporary directory
    /tmp/run-pZYpzQ
    ...
    I'm back to my project directory :
    /home/aguirre/otwrapy
    """

    def __init__(self, res_dir, prefix='simu_', cleanup=False, to_be_copied=None):
        date_tag = datetime.now().strftime("%Y-%m-%d_%H-%M_")
        self.simu_dir = mkdtemp(dir=res_dir, prefix=prefix + date_tag)
        self.cleanup = cleanup
        self.to_be_copied = to_be_copied

    def __enter__(self):
        if self.to_be_copied is not None:
            for file in self.to_be_copied:
                if os.path.isfile(file):
                    shutil.copy(file, self.simu_dir)
                elif os.path.isdir(file):
                    shutil.copytree(file, os.path.join(self.simu_dir,
                                    file.split(os.sep)[-1]))
                else:
                    raise Exception('In othpc.TempSimuDir : the current '
                                    + 'path "{}" is not a file '.format(file)
                                    + 'nor a directory to transfer.')
        return self.simu_dir

    def __exit__(self, type, value, traceback):
        if self.cleanup:
            shutil.rmtree(self.simu_dir)

def make_report_file(simu_dir, x, y=None, report_file="report.csv", input_description=None, output_description=None):
    if input_description is None:
        input_description = [f'X{i}' for i in range(len(x))]
    else:
        input_description = list(input_description)
    if y is None:
        df = pd.DataFrame([], columns=input_description, index=[simu_dir])
    else:
        if output_description is None:
            output_description = [f'Y{i}' for i in range(len(y))]
        else:
            output_description = list(output_description)
        df = pd.DataFrame([], columns=input_description + output_description, index=[simu_dir])
    df.loc[simu_dir, input_description] = x
    if y is not None:
        df.loc[simu_dir, output_description] = y
    df.to_csv(os.path.join(simu_dir, report_file), na_rep="NaN")

def make_summary_file(res_dir, summary_file="summary.csv", report_file="report.csv"):
    df_table = pd.DataFrame([])
    subfolders = [ f.path for f in os.scandir(res_dir) if f.is_dir() ]
    for simu_dir in subfolders:
        try:
            df = pd.read_csv(os.path.join(simu_dir, report_file), index_col=0, na_values=["NaN", ""])
            df_table = pd.concat([df_table, df])
        except FileNotFoundError: 
            pass
    df_table.to_csv(os.path.join(res_dir, summary_file), na_rep="NaN")
        
def evaluation_error_log(error, simulation_directory, name="evaluation_error.txt"):
    f  = open(os.path.join(simulation_directory, name), "w")
    f.write(error.__str__())
    f.close()

class MemoizeWithSave(ot.MemoizeFunction):
    """
    It provides additionnal methods to save and load cache input and output to the OT Function
 
    Class that inherits from openturns.MemoizeFunction
 
    Parameters
    ----------
    function : :class:`~openturns.Function`
        The function in which the cache is loaded or saved.
    cache_filename : str
        Path to the cache filename, it must be a csv file.
    logger_name : str
        Name of the logger to use, default is None which is the root logger.
    """
    def __init__(self, function, cache_filename, logger_name=None):
        self.cache_filename = cache_filename
        self.logger = logging.getLogger(logger_name)
        # transfer parameters of the original wrapper function
        self.__dict__.update(function.__dict__)
 
        super().__init__(function)
 
    def save_cache(self, logging=True):
        """
        Save the input and output cache to a csv file.
        """
 
        # get the cache sample
        cache_data = self.getCacheInput()
        cache_data.stack(self.getCacheOutput())
        cache_data.setDescription(self.getDescription())
        cache_data.exportToCSVFile(self.cache_filename)
 
        # internal flag to avoid repeated log message in FunctionAdvanced
        if logging:
            # print the number of saved evaluations
            self.logger.info(f'Saved successfully {cache_data.getSize()} evaluations in '
                             f'"{self.cache_filename}".')
 
    def load_cache(self):
        """
        Load a csv file and add it to the cache of the function
        """
 
        # retreive the number of input
        n_input = self.getInputDimension()
 
        if os.path.isfile(self.cache_filename):
            # load the cache from the file
            cache_data = ot.Sample.ImportFromCSVFile(self.cache_filename)
 
            # add the cache to the function
            input_sample = cache_data[:, :n_input]
            output_sample = cache_data[:, n_input:]
            self.addCacheContent(input_sample, output_sample)
 
            # print the number of loaded evaluations
            self.logger.info(f'Loaded successfully {cache_data.getSize()} evaluations from '
                             f'{self.cache_filename}.')
        else:
            self.logger.info(f'Cache filename "{self.cache_filename}" not found. '
                             'No evaluations loaded !')

# def explicit_error(cp):
#   if cp.returncode != 0:
#     print(''.join(['=']*20) + ' cmd ' + ''.join(['=']*20))
#     print(cmd)
#     print(''.join(['=']*20) + ' exit code ' + ''.join(['=']*20))
#     print(cp.returncode)
#     print(''.join(['=']*20) + ' stdout ' + ''.join(['=']*20))
#     print(cp.stdout.decode(platform_arg['encoding'][os.name]))
#     print(''.join(['=']*20) + ' stderr ' + ''.join(['=']*20))
#     print(cp.stderr.decode(platform_arg['encoding'][os.name]))
#     print(''.join(['=']*20) + '  ' + ''.join(['=']*20))
#     raise RuntimeError(cp.stderr.decode(platform_arg['encoding'][os.name]))
