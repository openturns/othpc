import openturns as ot

class MyCode(ot.OpenTURNSPythonFunction):
    """
      Minimalistic example of a study function.
    """
    def __init__(self):
        super().__init__(2,1)

    def _exec(self, X):
        s = [sum(X)]
        return s
