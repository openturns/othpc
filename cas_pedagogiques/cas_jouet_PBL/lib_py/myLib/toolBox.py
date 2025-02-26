import os
import sys
import subprocess
import pandas as pd
from glob import glob


def dumpFinishComputation(case_path, run_id, dict_inputs, file_basename):

    Write = False

    header = "run_id" + ","

    line = run_id + ","

    for elt in sorted(dict_inputs.items()):
        header += elt[0] + ","
        line += "%.16e," % (float(elt[1]))

    header = header.rstrip(",")
    line = line.rstrip(",")

    fileName = os.path.join(case_path, file_basename)

    while Write == False:
        Write = writeFile(fileName=fileName, header=header, line=line)


def writeFile(fileName, header, line):
    Write = True

    f = open(fileName, "a")
    size = os.stat(fileName).st_size
    try:
        if size == 0:  # file is empty, dump header
            f.write(header + "\n")
        f.write(line + "\n")
    except:
        Write = False

    f.close()

    return Write


def setRunid(case_path, run_prefix="OT_Persalys_"):

    idx = 0

    # run_prefix='OT_Persalys_'
    run_prefix = run_prefix.rstrip("_") + "_"

    search_dir = os.path.join(case_path, "RESU", run_prefix) + "*"

    # search already existing result file
    dirlist = glob(search_dir)

    dirlist.sort()

    if len(dirlist) > 0:
        idx = int(dirlist[-1].split("_")[-1])

    run_id = run_prefix + "{:0>5}".format(idx + 1)

    resu_dir = os.path.join(case_path, "RESU", run_id)

    return run_id


def createResultDir(case_path, run_prefix="OT_Persalys_"):
    success = False

    while success == False:
        run_id = setRunid(case_path=case_path, run_prefix=run_prefix)
        resu_dir = os.path.join(case_path, "RESU", run_id)
        try:
            os.makedirs(resu_dir)
            success = True
        except:
            pass

    return run_id


def checkSuccessfullRun(case_path, file_basename, separator=",", **dict_parameters):
    """
    Function to check if the case has already been runned.
    Usefull is additional output are added to an already runned experience plan
    Output can be retrieve without re running the case

    Parameters
    ----------
    case_path : string
        root directory of the code saturne case
    file_basename : string
        name of the file storing successul runs
    separator : string
        csv separator
    **dict_parameters : TYPE
        list of _exec arg

    Returns
    -------
    run_id : string
        return run_id (folder name)
        none if id not found

    """

    filename = os.path.join(case_path, file_basename)
    run_id = None
    if os.path.exists(filename):
        df_sucessRun = pd.read_csv(filename, delimiter=separator)
    else:
        return None  # should be first run when SucessFullRun file not yeat created

    # check paramater name are included in provided sucessfullrun file
    for elt in dict_parameters.keys():
        if elt not in df_sucessRun.columns:
            print(
                "Provided SuccessFullRun header files does not match _exec parameter name"
            )
            return None
        if "run_id" not in df_sucessRun.columns:
            print("Provided SuccessFullRun does not contain 'run_id' column ")
            return None

    for r_id in range(len(df_sucessRun)):  # loop on each row of the result file
        match = True
        for elt in dict_parameters.items():
            key = elt[0]
            value = float(elt[1])
            if abs(df_sucessRun[key][r_id] - value) > 1e-8:
                match = False
                break

        if match == True:  # meaning that previous loop match all parameters
            run_id = df_sucessRun["run_id"][r_id]
            # dot not break the loop to ensure the last match is used

    return run_id
