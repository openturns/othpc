from dask_jobqueue import SLURMCluster
from dask.distributed import Client
from MPILoadSimulator import MPILoadSimulator

# Define dask SLURM cluster
cluster = SLURMCluster(
    cores=44,
    memory="512 MB",
    walltime=5,
    job_extra_directives=[
        "--wckey=P120K:SALOME",
        "-n 2"
        # "--output=wrapper.log",
        # "--error=wrapper_error.log",
    ],
    # job_directives_skip=['-n 1']
)
cluster.scale(2)  # Creates two jobs with the specs above
print(cluster.job_script())

# Define dask client
client = Client(cluster)
cb = MPILoadSimulator(executable_file="./bin/myMPIProgram", nb_proc=80, simu_duration=30)
X = [[1, 2], [3, 4]]
# Current option
futures = client.map(cb, X)
outputs = client.gather(futures)
print(outputs)

# # Option 2
# futures = client.submit(cb, X)
# outputs = futures.result()