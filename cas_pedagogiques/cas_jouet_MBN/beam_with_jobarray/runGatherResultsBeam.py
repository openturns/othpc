"""
Collecte les résultats après une étude paramétrique
du modèle de poutre encastrée.

Exemple
-------
python3 runGatherResultsBeam.py
"""
import shutil
import numpy as np
import os.path as osp
import os
import re
from xml.dom import minidom
import openturns as ot

masterDir = "/scratch/users/C61372/beam"
workDir = osp.join(masterDir, "work")

os.chdir(workDir)

njobs = len([name for name in os.listdir(".") if os.path.isdir(name)])
print(f"Number of jobs = {njobs}")

output_data = []
for job in range(1, 1 + njobs):
    curDir = osp.join(workDir, f"{job}")
    print(f"Current directory {curDir}")
    
    # Retrieve output
    output_xml_file = osp.join(curDir, "_beam_outputs_.xml")
    xmldoc = minidom.parse(output_xml_file)
    itemlist = xmldoc.getElementsByTagName("outputs")
    deviation = float(itemlist[0].attributes["deviation"].value)
    output_data.append([deviation])
    

# Crée un Sample vide, que l'on complète ensuite
output_sample = ot.Sample(output_data)
output_sample.setDescription(["Deviation"])
output_filename = osp.join(workDir, "output.csv")
print(f"Write output data into {output_filename}")
output_sample.exportToCSVFile(output_filename)

