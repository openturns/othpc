#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: otwrapy
"""

from tempfile import mkdtemp
import shutil
import os


class TempWorkDir(object):

    """Implement a context manager that creates a temporary working directory.

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

    def __init__(self, work_dir=None, prefix='simu-', cleanup=False,
                 transfer=None):
        if work_dir is not None:
            if not os.path.exists(work_dir):
                try:
                # Without the TRY, this line seems to be executed multiple times when using Dask. 
                # Maybe two processes enter it at the same time. 
                    os.makedirs(work_dir)
                except:
                    pass
        self.dirname = mkdtemp(dir=work_dir, prefix=prefix)
        self.cleanup = cleanup
        self.transfer = transfer

    def __enter__(self):
        if self.transfer is not None:
            for file in self.transfer:
                if os.path.isfile(file):
                    shutil.copy(file, self.dirname)
                elif os.path.isdir(file):
                    shutil.copytree(file, os.path.join(self.dirname,
                                    file.split(os.sep)[-1]))
                else:
                    raise Exception('In otwrapy.TempWorkDir : the current '
                                    + 'path "{}" is not a file '.format(file)
                                    + 'nor a directory to transfer.')
        return self.dirname

    def __exit__(self, type, value, traceback):
        if self.cleanup:
            shutil.rmtree(self.dirname)