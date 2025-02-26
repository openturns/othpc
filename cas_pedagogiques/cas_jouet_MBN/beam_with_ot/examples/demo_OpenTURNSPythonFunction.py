"""
Le but de ce script est de présenter une démonstration de la classe 
OpenTURNSPythonFunction et son fonctionnement.
Michaël Baudin, 2024

Références
----------
- Python functions overview. Michaël Baudin. July 4, 2024
  https://github.com/openturns/openturns.github.io/blob/master/presentation/master/python_function.pdf
  https://github.com/openturns/presentation/tree/master/developer/python_function

"""

# %%
import openturns as ot
import numpy as np


# %%
class IshigamiFunction(ot.OpenTURNSPythonFunction):
    def __init__(self, a, b):
        super().__init__(3, 1)
        self.a = a
        self.b = b
        self.setInputDescription(["First input", "Second input", "Third input"])
        self.setOutputDescription(["Y"])

    def _exec(self, x):
        y0 = (
            np.sin(x[0])
            + self.a * np.sin(x[1]) ** 2
            + self.b * x[2] ** 4 * np.sin(x[0])
        )
        return [y0]


# %%
a = 7.0
b = 0.1
ishigamiFunction = IshigamiFunction(a, b)  # Create the object
gFunction = ot.Function(ishigamiFunction)  # Convert to a Function
x = [0.5, 1.0, 1.5]
print(f"x = {x}")
y = gFunction(x)
print(f"y = {y}")
print(f"Input description = {gFunction.getInputDescription()}")


# %%
class IshigamiFunctionVectorized(ot.OpenTURNSPythonFunction):
    def __init__(self, a, b):
        super().__init__(3, 1)
        self.a = a
        self.b = b
        self.setInputDescription(["X0", "X1", "X2"])
        self.setOutputDescription(["Y"])

    def _exec_sample(self, x):
        x = ot.Sample(x)  # ot.MemoryView > ot.Sample
        # ot.Sample > np.array
        x0 = np.array(x[:, 0].asPoint())
        x1 = np.array(x[:, 1].asPoint())
        x2 = np.array(x[:, 2].asPoint())
        y = np.sin(x0) + self.a * np.sin(x1) ** 2 + self.b * x2**4 * np.sin(x0)
        y = ot.Sample.BuildFromPoint(y)
        return y


# %%
a = 7.0
b = 0.1
ishigamiFunction = IshigamiFunctionVectorized(a, b)  # Create the object
gFunction = ot.Function(ishigamiFunction)  # Convert to a Function
input_distribution = ot.JointDistribution([ot.Uniform(-np.pi, np.pi)] * 3)
x_sample = input_distribution.getSample(10)
print(f"x_sample")
print(x_sample)
y_sample = gFunction(x_sample)
print(f"y_sample")
print(y_sample)

# %%
