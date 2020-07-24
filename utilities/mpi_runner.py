import argparse

from mpi4py import MPI
import os
from convert import Converter
import functools
import operator
from osgeo import gdal
import logging as log

# MPI wrapper to parallelize tile conversion on NCI
comm = MPI.COMM_WORLD

p = argparse.ArgumentParser()
p.add_argument('-p', '--path', help="Base path of multiplier data to convert")

args = p.parse_args()
datapath = args.path

if comm.rank == 0:
    tiles = list({file.split('_')[0] for file in os.listdir(os.path.join(datapath, 'shielding/'))})
    tiles = [tiles[i::comm.size] for i in range(comm.size)]
else:
    tiles = None

tiles = comm.scatter(tiles, root=0)

results = []
converter = Converter(tiles, datapath)
results = converter.run()

results = comm.gather(results, root=0)

log.info("Creating virtual raster table")
if comm.rank == 0:
    tile_files = functools.reduce(operator.iconcat, results, [])

    if len(tile_files) > 0:
        gdal.BuildVRT(os.path.join(datapath, 'wind-multipliers.vrt'), tile_files)
