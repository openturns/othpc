# %%
import os
import openturns as ot
from BeamFunction import BeamFunction

# %%
#
print("Test the BeamFunction")
simulation_directory = os.getcwd()
input_template_filename = os.path.join(simulation_directory, "beam_input_template.xml")
beam_executable = os.path.join(simulation_directory, "beam")
beamModel = BeamFunction(input_template_filename, beam_executable, verbose=True)
input_distribution = beamModel.getInputDistribution()
print("Create X sample")
sample_size = 10
input_sample = input_distribution.getSample(sample_size)
print("X = ")
print(input_sample)
print("Convert model into Function")
model = ot.Function(beamModel)  # Optionnel ici, mais significatif (***)
print("Compute Y")
output_sample = model(input_sample)
print("Y = ")
print(output_sample)

# %%
