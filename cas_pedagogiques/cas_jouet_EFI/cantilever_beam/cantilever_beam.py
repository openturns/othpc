from wrapper_dask import *
from xml.dom import minidom
import openturns.coupling_tools as otct
from datetime import datetime
import tempfile

class CantileverBeam(ot.OpenTURNSPythonFunction):
    def __init__(self, input_template, executable):
        super().__init__(4, 1)
        # TODO : check that these files and folders do exist
        self.input_template = os.path.abspath(input_template)
        self.my_executable = os.path.abspath(executable)

    def _exec(self, X):
        """
        Executes one evaluation of the black-box model for one input. 

        Parameters
        ----------
        x : list
            This input design of experiment should present an evaluation index in the first colum. 
            Since this example presents four inputs (F, E, L, I), the number of columns is five. 
        """
        # Tout se passe dans un repertoire temporaire
        with tempfile.TemporaryDirectory() as xsimu_dir:
            # Creation du fichier d'entree
            otct.replace(
                # File template including your tokens to be replaced by values from a design of exp.
                self.input_template,
                # File written after replacing the tokens by the values in X
                os.path.join(xsimu_dir, 'beam_input.xml'),
                ['@F@', '@E@', '@L@', '@I@'],
                [X[0], X[1], X[2], X[3]],
                )
            # Execution
            os.chdir(xsimu_dir)
            try:
                myexec = os.system(self.my_executable + " -x beam_input.xml")
            except Exception as err:
                print(f"ERROR: type {myexec} in {xsimu_dir}")
                print(err)
            # Lecture de la sortie
            try:
                xmldoc = minidom.parse(os.path.join(xsimu_dir, '_beam_outputs_.xml'))
                itemlist = xmldoc.getElementsByTagName('outputs')
                deviation = float(itemlist[0].attributes['deviation'].value)
            except FileNotFoundError as err:
                print(err)
                print(f"WARNING: the following file was not found: {xsimu_dir}")
                deviation = float('nan')
        return [deviation]

if __name__ == "__main__":
    cb = CantileverBeam("template/beam_input_template.xml", "template/beam")
    dw = DaskWrapper(cb)
    dwfun = ot.Function(dw)
    X = ot.Sample.ImportFromCSVFile("input_doe/doe100.csv", ",")[:,1:]
    Y = dwfun(X)
    print(Y)
