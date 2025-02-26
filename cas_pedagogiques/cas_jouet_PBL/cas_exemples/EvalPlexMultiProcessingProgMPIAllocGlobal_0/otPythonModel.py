import subprocess
import os
import sys
import openturns as ot

if "../bin" not in os.environ["PATH"].split(":"):
    os.environ["PATH"] = "%s:%s" % ("../bin", os.environ["PATH"])

sys.path.insert(0, "../../lib_py")
import myLib.toolBox as tb


class funcPythonCode(ot.OpenTURNSPythonFunction):
    """
    class to define _exec function wrapping a sequential code
    """

    def __init__(self):
        self.successfullRunFileName = "successfull_Run.csv"
        self.needRestartRunFileName = "needRestart_Run.csv"
        self.failedRunFileName = "failed_Run.csv"
        self.casePath = "./"
        self.ntasksMax = 10
        self.binPath = "../bin"

        self.mpiexec = "srun"
        self.mpiexec_options = "--exclusive"

    def run_myProgram(self, resultDir, dictInputs, ntasks, restartPath=None):
        """
        run my Program with subprocess
        """

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
        command.append(resultDir)
        command.append("--cpu-interval=%d" % (30))

        if restartPath != None:
            command.append("--restart-path")
            command.append(restartPath)

        command_line = ""
        for elt in command:
            command_line += " %s" % (elt)

        # launch myProgram
        proc = subprocess.Popen(
            command_line,
            shell=True,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

        log_file = os.path.join(resultDir, "log.txt")

        try:
            proc.wait(timeout=1200)  # time to be set by user if relevant

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

            # Estimate number of proces needed
            ntasks = 3  # here can be function of the input
            ntasks = min(ntasks, self.ntasksMax)

            if checkRestart_run_id == None:
                r = self.run_myProgram(
                    os.path.join(case_path, "RESU", run_id),
                    dictInputs=dict_inputs,
                    ntasks=ntasks,
                )
                newComputation = True

            if (
                checkRestart_run_id != None
            ):  # Perform actions required by code to restart from the previous run
                restartPath = os.path.join(case_path, "RESU", checkRestart_run_id)
                r = self.run_myProgram(
                    os.path.join(case_path, "RESU", run_id),
                    dictInputs=dict_inputs,
                    ntasks=ntasks,
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

            # check convergence : arbitraty criteria here to mimic convergence tracking
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
