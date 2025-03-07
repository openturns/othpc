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
                    raise Exception('In otwrapy.TempWorkDir : the current '
                                    + 'path "{}" is not a file '.format(file)
                                    + 'nor a directory to transfer.')
        return self.simu_dir

    def __exit__(self, type, value, traceback):
        if self.cleanup:
            shutil.rmtree(self.simu_dir)

    def make_summary_file(self, x, y=None, summary_file="summary.csv"):
        input_description = [f'X{i}' for i in range(x.getDimension())]
        df = pd.DataFrame([], columns=input_description, index=[self.simu_dir])
        df.loc[self.simu_dir, input_description] = x
        if y is not None: 
            output_description = [f'Y{i}' for i in range(len(y))]
            df.loc[self.simu_dir, output_description] = y
        df.to_csv(os.path.join(self.simu_dir, summary_file))

def make_summary_table(res_dir, summary_table="summary_table.csv", summary_row="summary.csv"):
    df_table = pd.DataFrame([])
    for simu_dir in os.listdir(res_dir):
        try:
            df = pd.read_csv(os.path.join(res_dir, simu_dir, summary_row), index_col=0)
            df_table = pd.concat([df_table, df])
        except FileNotFoundError: 
            pass
    df_table.to_csv(os.path.join(res_dir, summary_table))
        

