# Script à lancer depuis son poste de travail dans un environnement salome shell.

import mycode
import ydefxwrapper
import openturns as ot
import os
import pydefx

my_code_function = mycode.MyCode()

params = pydefx.Parameters("cronos") # Create default values for cronos

# Some custom parameters
params.nb_branches = 24
params.salome_parameters.job_name = "myjob"
params.salome_parameters.resource_required.nb_proc = 24
params.salome_parameters.resource_required.nb_node = 1
params.salome_parameters.wckey = "P120K:SALOME"
# default value for work_directory for cronos is /scratch/users/{NNI}/workingdir
params.salome_parameters.work_directory = os.path.join(params.salome_parameters.work_directory, "mycase")
params.createResultDirectory("/tmp") # local work directory.

# mycode.py has to be installed in the execution environnement
mycode_path = os.path.join(os.getcwd(), "mycode.py")
params.salome_parameters.in_files.append(mycode_path)

wrapper = ydefxwrapper.YdefxWrapper(my_code_function, params=params)
ot_fun = ot.Function(wrapper)
sample = ot.Sample(list(zip([ x // 10 for x in range(0,100)],
                            [ x % 10 for x in range(0,100)])))
Y = ot_fun(sample)
print(Y)
