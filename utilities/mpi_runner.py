import functools
import logging as log
import os

import argparse
from osgeo import gdal

from utilities.convert import Converter, create_sub_dirs_for_convert
from utilities.parallel import attempt_parallel


def parallelise_convert_on_tiles(data_path, comm):
    """
    MPI wrapper to parallelize tile conversion on NCI

    :param data_path: `string` location of sheilding, terrain
                    and topographic data
    :param comm: `tuple` MIP.COMM_WORLD object
    """

    if comm.rank == 0:
        tiles = list({file.split('_')[0] for file in
                     os.listdir(os.path.join(data_path, 'shielding'))})
        tiles = [tiles[i::comm.size] for i in range(comm.size)]
    else:
        tiles = None

    tiles = comm.scatter(tiles, root=0)
    log.info("Processing converter tile "
             f"{tiles} on {comm.rank} of {comm.size}")

    converter = Converter(tiles, data_path)
    results = converter.run()

    log.info("Returning {} from {}".format(results, comm.rank))
    results = comm.gather(results, root=0)

    if comm.rank == 0:
        if len(results) > 0:
            log.info("Creating virtual raster table")
            tile_files = functools.reduce(lambda total, element:
                                          total + element[0], results, [])
            max_tile_files = functools.reduce(lambda total, element:
                                              total + element[1], results, [])
            gdal.BuildVRT(os.path.join(data_path, 'M3',
                                       'wind-multipliers.vrt'),
                          tile_files)
            gdal.BuildVRT(os.path.join(data_path, 'M3_max',
                                       'wind-multipliers.vrt'),
                          max_tile_files)
        else:
            log.warning("No raster file found to build virtual raster table")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('-p', '--path',
                   help="Base path of multiplier data to convert")

    args = p.parse_args()

    global MPI, comm
    MPI = attempt_parallel()
    comm = MPI.COMM_WORLD
    if comm.rank == 0:
        create_sub_dirs_for_convert(args.path)

    parallelise_convert_on_tiles(args.path, comm)
