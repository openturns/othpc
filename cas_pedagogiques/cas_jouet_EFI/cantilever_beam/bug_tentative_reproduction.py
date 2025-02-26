import openturns as ot
class MyBaseClass(ot.OpenTURNSPythonFunction):
    def __init__(self):
        super().__init__(1,1)
    def _exec(self, X):
        return X

class MyChildClass(MyBaseClass):
    def __init__(self):
        super().__init__()
    def _exec(self, X):
        return super()._exec(X)

bc = MyBaseClass()
fun_bc = ot.Function(bc)
cc = MyChildClass()
fun_cc = ot.Function(cc)