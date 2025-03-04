import os
import openturns as ot
import ydefxwrapper
import pydefx
from cantilever_beam import CantileverBeam

# Les chemins sont ceux attendus à l'exécution
cb = CantileverBeam("beam_input_template.xml", "beam")
#dw = DaskWrapper(cb)
params = pydefx.Parameters("cronos") # Create default values for cronos
params.nb_branches = 8
params.salome_parameters.job_name = "myjob"
params.salome_parameters.resource_required.nb_proc = 8
params.salome_parameters.resource_required.nb_node = 1
params.salome_parameters.wckey = "P120K:SALOME"
# default value for work_directory for cronos is /scratch/users/{NNI}/workingdir
params.salome_parameters.work_directory = os.path.join(params.salome_parameters.work_directory, "mycase")
params.createResultDirectory("/tmp") # local work directory.

# mycode.py has to be installed in the execution environnement
mycode_path = os.path.join(os.getcwd(), "cantilever_beam.py")
params.salome_parameters.in_files.append(mycode_path)
# Les chemins sont ceux sur la machine d'où le calcul est lancé
params.salome_parameters.in_files.append(os.path.join(os.getcwd(),
                                            "template/beam_input_template.xml"))
params.salome_parameters.in_files.append(os.path.join(os.getcwd(),
                                            "template/beam"))

dw = ydefxwrapper.YdefxWrapper(cb, params=params)

dwfun = ot.Function(dw)
X = ot.Sample.ImportFromCSVFile("doe100.csv", ",")[:,1:]
Y = dwfun(X)
print(Y)
