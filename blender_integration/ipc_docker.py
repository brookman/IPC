import os

class IpcDocker:

    def __init__(self):
        self.mesh_container_name = 'ipc_mesh'
        self.run_container_name = 'ipc_run'

        self.delete_container(self.mesh_container_name)
        self.delete_container(self.run_container_name)

        self.run_container(self.mesh_container_name, ['mkdir -p /app/convert', 'cd /app/convert', '/app/src/Projects/MeshProcessing/meshprocessing 0 /app/convert/mesh.obj 3 5e-1 0'])
        self.run_container(self.run_container_name, ['mkdir -p /app/run/input', 'cd /app/run/input', '/app/build/IPC_bin 100 /app/run/input/scene.txt -o /app/run/output'])

    def delete_container(self, name):
        os.system('docker rm {}'.format(name))

    def run_container(self, name, bash_commands):
        joined = ' && '.join(bash_commands)
        os.system('docker run --name {} -d ipc /bin/bash -c "{}"'.format(name, joined))

    def convert_to_msh(self, obj_path, msh_path):
        os.system('docker cp {} {}:/app/convert/mesh.obj'.format(obj_path, self.mesh_container_name))
        os.system('docker start -a {}'.format(self.mesh_container_name))
        os.system('docker cp {}:/app/convert/mesh.msh {}'.format(self.mesh_container_name, msh_path))

    def run_simulation(self, input_directory, output_parent_directory):
        os.system('docker cp {} {}:/app/run'.format(input_directory, self.run_container_name))
        os.system('docker start -a {}'.format(self.run_container_name))
        os.system('docker cp {}:/app/run/output/ {}'.format(self.run_container_name, output_parent_directory))
