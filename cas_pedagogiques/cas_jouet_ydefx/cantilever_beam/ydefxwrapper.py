import openturns as ot
import pydefx
import pickle
import os

FUNCTION_DUMP_FILE_NAME = "function_dump.pkl"

class YdefxWrapper(ot.OpenTURNSPythonFunction):
    def __init__(self, callable, params=None, study=None):
        """
        :param callable: Study function of type ot.OpenTURNSPythonFunction.
        :param params: Job parameters of type pydefx.Parameters.
        :param study: pydefx study model. pydefx.PyStudy used by default.

        By default, the job parameters are configured for local evaluation.

        Several study models are available with pydefx:

        - pydefx.PyStudy : All the points are evaluated in one job and YACS is
          used for distribution.
        - pydefx.MultiJobStudy : Each point is evaluated in a different job.
        - pydefx.SlurmStudy : All the points are evaluated in one job and srun
          is used for distribution. Slurm resource is needed.
        """
        super().__init__(callable.getInputDimension(),
                         callable.getOutputDimension())
        self._callable = callable
        if params is None:
            # Local evaluation by default.
            # The second argument (4) is the number of parallel evaluations.
            params = pydefx.Parameters("localhost", 4)
            params.salome_parameters.work_directory = os.path.join(
                                        params.salome_parameters.work_directory,
                                        "mycase")
            params.createResultDirectory("/tmp")
        self._params =  params
        if study is None:
            study = pydefx.PyStudy()
        self._study = study

    def _exec_sample(self, X):
        local_work_dir = self._params.salome_parameters.result_directory
        callable_dump_file = os.path.join(local_work_dir,
                                          FUNCTION_DUMP_FILE_NAME)
        nb_inputs = self._callable.getInputDimension()
        args = "p0"
        for i in range(1, nb_inputs):
            args += f", p{i}"
        with open(callable_dump_file, "wb") as f:
            pickle.dump(self._callable, f)
        self._params.salome_parameters.in_files.append(callable_dump_file)
        run_script = pydefx.PyScript()
        run_script.loadString(f"""
import pickle
def _exec({args}):
    with open("{FUNCTION_DUMP_FILE_NAME}", "rb") as f:
        callable = pickle.load(f)
    point = [{args}]
    res = callable(point)
    return res
""")
        ydefx_sample = run_script.CreateEmptySample()
        dict_sample = {}
        for i in range(nb_inputs):
            dict_sample[f"p{i}"] = []
        for point in X:
            for i in range(nb_inputs):
                dict_sample[f"p{i}"].append(point[i])
        #ydefx_sample.setInputValues({ "point": [list(i) for i in X] })
        ydefx_sample.setInputValues(dict_sample)
        self._study.createNewJob(run_script, ydefx_sample, self._params)
        self._study.launch()
        self._study.wait()
        result = self._study.getResult()
        # how to deal with errors ?
        if result.hasErrors() :
            print("Errors found during evaluation!")
            print(result.getErrors())
            print(self._study.sample.getMessages())
        return self._study.sample.getOutput("res")
