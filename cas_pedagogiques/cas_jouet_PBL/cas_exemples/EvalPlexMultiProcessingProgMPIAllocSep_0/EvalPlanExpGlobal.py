#!/usr/bin/env python3
# SBATCH --nodes=1
# SBATCH --ntasks-per-node=34
# SBATCH --partition=cn
# SBATCH --qos=test
# SBATCH --time=00:30:00
# SBATCH --wckey=P120F:PYTHON
# SBATCH --output=job_%j.out.log
# SBATCH --error=job_%j.err.log

import sys
import os

sys.path.append("./")
from multiprocessing import Process, Pool
import multiprocessing
import pandas as pd
from optparse import OptionParser
import importlib
import openturns as ot

sys.path.insert(0, "../../lib_py")
import myLib.toolBox as tb


def process_cmd_line(argv):
    """Processes the passed command line arguments."""
    parser = OptionParser(
        usage="usage: %prog DE.csv module_exec.py [options]",
        description="Run an CS and OM (optional) Design Experience plan, each point is launched with sbatch",
    )

    parser.add_option(
        "--auto-restart",
        action="store_true",
        dest="auto_restart",
        default=False,
        help="relauch eval of exp plan while point need restart (manage through needRestart csv file)",
    )

    parser.add_option(
        "--n-batch",
        dest="nbatch",
        type="int",
        help="number of parallel launch of sbatch command, default 45",
    )

    (options, args) = parser.parse_args(argv)
    return options, args


class DE:
    """
    class to manage CS DE csv file based
    """

    def __init__(self, DE_csv, classExec, nbatch, delimiter=";"):
        self.DE_csv = DE_csv
        self.nBatch = nbatch
        # exec function use to run each point
        self.classExec = classExec
        self._exec = classExec._exec
        self.SuccessfullRun_f = classExec.successfullRunFileName
        self.NeedRestartRun_f = classExec.needRestartRunFileName
        self.FailedRun_f = classExec.failedRunFileName
        self.case_path = classExec.casePath

        self.df_de = pd.read_csv(self.DE_csv, delimiter=delimiter)

        self.buildDictPoints()

    def buildDictPoints(self):
        """
        method to build a list of dictionnary, one dict per point
        """
        dicts = []
        df_de = self.df_de
        sample = []

        for p_id in range(len(df_de)):
            p_dict = {}
            point = []
            for k_id in range(len(df_de.columns)):
                key = df_de.columns[k_id]
                p_dict[key] = float(df_de.iloc[p_id, k_id])
                point.append(float(df_de.iloc[p_id, k_id]))

            failRunid = self.checkNonPreviousRunFail(p_dict)
            if failRunid == None:  # launch eval only if previous run has not fail
                dicts.append(p_dict)
                sample.append(point)

            self.dicts = dicts
            self.sampleToEvaluate = sample

    def checkNonPreviousRunFail(self, dict_inputs):
        """
        For a given point, check run eval has not previously fail
        """

        check_run_id = tb.checkSuccessfullRun(
            case_path=self.case_path, file_basename=self.FailedRun_f, **dict_inputs
        )
        return check_run_id

    def checkNeedRestart(self):
        """
        method to check if at least a run need restart
        """
        df_de = self.df_de

        needRestart = False

        for p_id in range(len(df_de)):
            p_dict = {}
            for k_id in range(len(df_de.columns)):
                key = df_de.columns[k_id]
                p_dict[key] = float(df_de.iloc[p_id, k_id])

            failRunid = self.checkNonPreviousRunFail(p_dict)
            check_run_id = tb.checkSuccessfullRun(
                case_path=self.case_path, file_basename=self.SuccessfullRun_f, **p_dict
            )
            checkRestart_run_id = tb.checkSuccessfullRun(
                case_path=self.case_path, file_basename=self.NeedRestartRun_f, **p_dict
            )

            if check_run_id != None:
                if check_run_id == checkRestart_run_id:
                    if failRunid == None:
                        needRestart = True

        return needRestart

    def runDE(self):
        """
        method to launch DE eval
        """

        pool = Pool(processes=self.nBatch)
        results = []

        for p_id in range(len(self.dicts)):
            # pool.apply_async(self._exec, kwds=self.dicts[p_id])
            X = self.sampleToEvaluate[p_id]
            results.append(pool.apply_async(self._exec, args=(X,)))
        pool.close()
        pool.join()
        Y = [result.get() for result in results]

        YSample = ot.Sample(Y)
        YSample.setDescription(self.classExec.getOutputDescription())
        globalSample = ot.Sample(self.sampleToEvaluate)
        globalSample.setDescription(self.classExec.getInputDescription())
        globalSample.stack(YSample)
        globalSample.exportToCSVFile("PLEXEvaluationResult.csv")


def main(args, options, funcExec):

    nbatch = 3
    if options.nbatch:
        nbatch = options.nbatch

    # Create a Design Experiment object
    de = DE(args[0], funcExec, nbatch)

    # run the design of experiment
    de.runDE()

    if options.auto_restart:
        needRestart = de.checkNeedRestart()
        while needRestart == True:
            # read control file to check user inloop action
            if os.path.isfile("control_file"):
                with open("control_file", "r") as f:
                    d = str(f.readlines()[-1]).replace("\n", "")
                    if d.split(" ")[-1] == "stop":
                        needRestart = False

                os.remove("control_file")

            if needRestart == True:
                de.runDE()
                needRestart = de.checkNeedRestart()


if __name__ == "__main__":
    options, args = process_cmd_line(sys.argv[1:])

    # load module and environement of given _exec module
    module_def_exec = importlib.import_module(args[1].replace(".py", ""))
    funcExec = module_def_exec.funcPythonCode()

    # launch main loop
    main(args, options, funcExec)
