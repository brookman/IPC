import bpy
import os
import shutil

from ipc_docker import IpcDocker
from simulation import *

input_directory = os.path.join(os.path.dirname(bpy.data.filepath), 'input')
output_parent_directory = os.path.dirname(bpy.data.filepath)
output_directory = os.path.join(output_parent_directory, 'output')

if os.path.exists(input_directory):
    shutil.rmtree(input_directory)
if os.path.exists(output_directory):
    shutil.rmtree(output_directory)

os.mkdir(input_directory)

ipc = IpcDocker()

simulation = Simulation(ipc)
simulation.prepare(input_directory)
simulation.run(input_directory, output_parent_directory, output_directory)
