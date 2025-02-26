# Script à lancer depuis son poste de travail dans un environnement salome shell.

import mycode
import ydefxwrapper
import openturns as ot
import os
my_code_function = mycode.MyCode()
wrapper = ydefxwrapper.YdefxWrapper(my_code_function)
# mycode.py has to be installed in the execution environnement
mycode_path = os.path.join(os.getcwd(), "mycode.py")
wrapper._params.salome_parameters.in_files.append(mycode_path)
ot_fun = ot.Function(wrapper)
sample = ot.Sample(list(zip([ x // 10 for x in range(0,100)],
                            [ x % 10 for x in range(0,100)])))
Y = ot_fun(sample)
print(Y)
