import functools
import logging as log
import os

import argparse
from osgeo import gdal

from convert import Converter
from parallel import attempt_parallel, disable_on_workers


def parallelise_convert_on_tiles(data_path, comm):
    # MPI wrapper to parallelize tile conversion on NCI

    if comm.rank == 0:
        tiles = list({file.split('_')[0] for file in os.listdir(os.path.join(data_path, 'shielding'))})
        tiles = [tiles[i::comm.size] for i in range(comm.size)]
    else:
        tiles = None

    tiles = comm.scatter(tiles, root=0)
    log.info("Processing converter tile {} on {} of {}".format(tiles, comm.rank, comm.size))

    converter = Converter(tiles, data_path)
    results = converter.run()

    log.info("Returning {} from {}".format(results, comm.rank))
    results = comm.gather(results, root=0)

    if comm.rank == 0:
        if len(results) > 0:
            log.info("Creating virtual raster table")
            tile_files = functools.reduce(lambda total, element: total + element[0], results, [])
            max_tile_files = functools.reduce(lambda total, element: total + element[1], results, [])
            gdal.BuildVRT(os.path.join(data_path, 'M3', 'wind-multipliers.vrt'), tile_files)
            gdal.BuildVRT(os.path.join(data_path, 'M3_max', 'wind-multipliers.vrt'), max_tile_files)
        else:
            log.warning("No raster file found to build virtual raster table")


@disable_on_workers
def _create_sub_dirs(data_path):
    os.makedirs(os.path.join(data_path, 'M3'), exist_ok=True)
    os.makedirs(os.path.join(data_path, 'M3_max'), exist_ok=True)


if __name__ == '__main__':
    log.getLogger().setLevel('DEBUG')

    p = argparse.ArgumentParser()
    p.add_argument('-p', '--path', help="Base path of multiplier data to convert")

    args = p.parse_args()

    global MPI, comm
    MPI = attempt_parallel()
    comm = MPI.COMM_WORLD
    if comm.rank == 0:
        _create_sub_dirs(args.path)

    parallelise_convert_on_tiles(args.path, comm)
