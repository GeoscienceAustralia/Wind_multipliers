from mpi4py import MPI
import os
from convert import Converter
import functools
import operator
from osgeo import gdal

# MPI wrapper to parallelize tile conversion on NCI
comm = MPI.COMM_WORLD

if comm.rank == 0:
    tiles = list({file.split('_')[0] for file in os.listdir('/g/data/fj6/multipliers/shielding')})
    tiles = [tiles[i::comm.size] for i in range(comm.size)]
else:
    tiles = None

tiles = comm.scatter(tiles, root=0)

results = []
converter = Converter(tiles)
results = converter.run()

results = comm.gather(results, root=0)

if comm.rank == 0:
    tile_files = functools.reduce(operator.iconcat, results, [])

    if len(tile_files) > 0:
        gdal.BuildVRT('/g/data/w85/s3-multipliers/wind-multipliers.vrt', tile_files)
