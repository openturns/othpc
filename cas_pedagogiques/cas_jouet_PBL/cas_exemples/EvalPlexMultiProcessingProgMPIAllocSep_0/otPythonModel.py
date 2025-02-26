import subprocess
import os
import sys
import openturns as ot
import math

if "../bin" not in os.environ["PATH"].split(":"):
    os.environ["PATH"] = "%s:%s" % ("../bin", os.environ["PATH"])

sys.path.insert(0, "../../lib_py")
import myLib.toolBox as tb


class funcPythonCode(ot.OpenTURNSPythonFunction):
    """
    class to define _exec function wrapping a MPI code
    """

    def __init__(self):
        self.successfullRunFileName = "successfull_Run.csv"
        self.needRestartRunFileName = "needRestart_Run.csv"
        self.failedRunFileName = "failed_Run.csv"
        self.casePath = "./"
        self.binPath = "../bin"  # optional, if bin not in regular PATH directory

        # SBATCH infos
        self.ntasksPerNode = 44
        self.wckey = "P120F:PYTHON"
        self.maxNodes = 2
        self.maxDuration = "00:30:00"
        self.sbatchOption = """#SBATCH --partition=cn
"""
        self.mpiexec = "srun"
        self.mpiexec_options = ""

        outputDimension = 1
        inputDimension = 2
        super().__init__(inputDimension, outputDimension)

    def run_myMPIProgram_sbatch(
        self, resultDir, dictInputs, nNodes, ntasks, duration, name, restartPath=None
    ):
        """
        run myMPIProgram with subprocess
        """
        code_sbatch_ressource = """#!/bin/bash
#SBATCH --nodes=@Nodes
#SBATCH --ntasks-per-node=@ntasksPerNode
#SBATCH --ntasks-per-core=1
#SBATCH --time=@Duration
#SBATCH --wckey=@wckey
#SBATCH --output=job_%j.out.log
#SBATCH --error=job_%j.err.log
#SBATCH --job-name=@name
"""
        code_runcase_launcher = """#!/bin/bash

jobid=$(sbatch --wait --parsable runcase &)
wait

fail=$(sacct --format JobId,ExitCode,State | grep $jobid | grep -c FAILED)
if [ $fail -ne 0 ]; then
 echo "failure running run jobid : $jobid"
 exit 1
fi
"""

        code_sbatch_ressource = code_sbatch_ressource.replace(
            "@ntasksPerNode", str(self.ntasksPerNode)
        )
        code_sbatch_ressource = code_sbatch_ressource.replace("@wckey", str(self.wckey))
        code_sbatch_ressource = code_sbatch_ressource.replace("@Nodes", str(nNodes))
        code_sbatch_ressource = code_sbatch_ressource.replace("@Duration", duration)
        code_sbatch_ressource = code_sbatch_ressource.replace("@name", name)

        runcaseFilename = os.path.join(resultDir, "runcase")
        runcaseLauncherFilename = os.path.join(resultDir, "runcase_launcher.sh")

        command = []
        command.append(self.mpiexec)
        command.append(self.mpiexec_options)
        if self.mpiexec != "":
            command.append("-n %d" % (ntasks))
        command.append(os.path.join(os.path.abspath(self.binPath), "myMPIProgram"))

        for elt in sorted(dictInputs.items()):
            command.append(
                r"' %s'" % (elt[1])
            )  # myProgram make the sum of args, order of args is not important in this example

        command.append("-r")
        command.append(os.path.abspath(resultDir))
        command.append("--cpu-interval=%d" % (120))

        if restartPath != None:
            command.append("--restart-path")
            command.append(os.path.abspath(restartPath))

        command_line = ""
        for elt in command:
            command_line += " %s" % (elt)

        command_line = " ".join(command)

        with open(runcaseFilename, "w") as f:
            f.write(code_sbatch_ressource)
            if self.sbatchOption != "":
                f.write(self.sbatchOption)
            f.write("\n")
            f.write(command_line)

        with open(runcaseLauncherFilename, "w") as f:
            f.write(code_runcase_launcher)

        # launch myMPIProgram
        proc = subprocess.Popen(
            "bash runcase_launcher.sh",
            shell=True,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            cwd=os.path.dirname(runcaseFilename),
        )

        log_file = os.path.join(resultDir, "log.txt")

        try:
            proc.wait(timeout=86400 * 3)  # time to be set by user if relevant

            f = open(log_file, "a")
            f.write(command_line)
            f.write("\n")
            for line in proc.stdout.readlines():
                f.write(line)

            f.close()
            return_code = proc.returncode

        except subprocess.TimeoutExpired:
            proc.kill()

            f = open(log_file, "a")
            f.write(command_line)
            f.write("\n")
            for line in proc.stdout.readlines():
                f.write(line)

            f.write("Simulation stoppe because of TimeOut")
            f.close()

            return_code = 2

        return return_code

    def _exec(self, X):
        """
        typical _exec function used to build and :class:`~openturns.PythonFunction` wrapping
        the execution of a single core program taking as parameter information contain in X

        Parameters
        -----------
        X : 1-d sequence of float
            sequence of float of parameter to be passed to myProgram for evaluation

        Returns
        --------
        Y : 1-d sequence of float
        """
        # build input dictionnary to run the program
        dict_inputs = {
            "X0": " %.16e" % (X[0]),
            "X1": " %.16e" % (X[1]),
        }  # Transform float to string needed for the example with myProgram but not generic

        # most of program will write their result in a directory
        # in this example it is propose to write result in case_path/RESU/OT_PERSALYS_XXXX directory
        case_path = self.casePath

        # parsing case_path/Successfull_Run.csv to check if point has already been run
        check_run_id = tb.checkSuccessfullRun(
            case_path=case_path,
            file_basename=self.successfullRunFileName,
            **dict_inputs
        )

        # parse case_path/needRestart_run.csv to check if run point need a restart
        checkRestart_run_id = tb.checkSuccessfullRun(
            case_path=case_path,
            file_basename=self.needRestartRunFileName,
            **dict_inputs
        )

        # parse case_path/failed_Run.csv to check if point computation has alread been attempted and failed
        checkFailed_run_id = tb.checkSuccessfullRun(
            case_path=case_path, file_basename=self.failedRunFileName, **dict_inputs
        )

        newComputation = False
        r = 3

        # check_run_id == None mean the point has not yet been evaluated
        if check_run_id == None:
            checkRestart_run_id = None

        if check_run_id == checkRestart_run_id and checkFailed_run_id == None:
            run_id = tb.createResultDir(case_path=case_path)

            # Estimate ressource needed for computation
            ntasks = 30  # here can be function of the input
            nNodes = math.ceil(ntasks / self.ntasksPerNode)
            nNodes = min(nNodes, self.maxNodes)
            ntasks = min(self.ntasksPerNode * nNodes, ntasks)
            duration = (
                "00:10:00"  # for true code, perfom estimation of estimated duration
            )
            name = "PLEX_%s" % (run_id.split("_")[-1])

            if checkRestart_run_id == None:
                r = self.run_myMPIProgram_sbatch(
                    os.path.join(case_path, "RESU", run_id),
                    dictInputs=dict_inputs,
                    nNodes=nNodes,
                    ntasks=ntasks,
                    duration=duration,
                    name=name,
                )
                newComputation = True

            if (
                checkRestart_run_id != None
            ):  # Perform actions required by code to restart from the previous run
                restartPath = os.path.join(case_path, "RESU", checkRestart_run_id)
                r = self.run_myMPIProgram_sbatch(
                    os.path.join(case_path, "RESU", run_id),
                    dictInputs=dict_inputs,
                    nNodes=nNodes,
                    ntasks=ntasks,
                    duration=duration,
                    name=name,
                    restartPath=restartPath,
                )
                newComputation = True

        elif check_run_id != None:
            run_id = check_run_id
            r = 0

        if r == 0:
            if newComputation == True:
                tb.dumpFinishComputation(
                    case_path=case_path,
                    run_id=run_id,
                    dict_inputs=dict_inputs,
                    file_basename=self.successfullRunFileName,
                )

            # example of result read, myProgram produce a file with
            # ''result : X.XXXXXXX+EXX'
            resultFileName = os.path.join(case_path, "RESU", run_id, "result.txt")
            resultFile = open(resultFileName, "r")
            lines = resultFile.readlines()
            Y1 = float(lines[-1].split(":")[-1])
            resultFile.close()

            # check convergence : arbitrary criteria here to mimic convergence tracking
            needRestart = True
            if checkRestart_run_id != None:
                resultFileName = os.path.join(
                    case_path, "RESU", check_run_id, "result.txt"
                )
                resultFile = open(resultFileName, "r")
                lines = resultFile.readlines()
                Y0 = float(lines[-1].split(":")[-1])
                resultFile.close()
                if abs(Y1 - Y0) > 1e-3:
                    needRestart = True
                else:
                    needRestart = False

            if newComputation == True and needRestart == True:
                tb.dumpFinishComputation(
                    case_path=case_path,
                    run_id=run_id,
                    dict_inputs=dict_inputs,
                    file_basename=self.needRestartRunFileName,
                )

        if r != 0:  # failed run
            if newComputation == True:
                tb.dumpFinishComputation(
                    case_path=case_path,
                    run_id=run_id,
                    dict_inputs=dict_inputs,
                    file_basename=self.failedRunFileName,
                )
            Y1 = float("nan")

        return [Y1]


if __name__ == "__main__":
    F = funcPythonCode()
    Y = F([-11, 20])
    print(Y[0])
