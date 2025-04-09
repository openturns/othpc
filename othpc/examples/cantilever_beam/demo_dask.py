from dask_jobqueue import SLURMCluster
from dask.distributed import Client, progress

# Define dask SLURM cluster
cluster = SLURMCluster(
    cores=5,
    memory="512 MB",
    job_extra_directives=[
        "--wckey=P120K:SALOME",
        "--time=5",
        "--output=wrapper.log",
        "--error=wrapper_error.log",
    ],
)
cluster.scale(3)  # Creates two jobs with the specs above
# Define dask client
client = Client(cluster)
