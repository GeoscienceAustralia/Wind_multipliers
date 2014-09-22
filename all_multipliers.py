"""
:mod:`all_multipliers` -- Calculate terrain, shielding and
topographic multipliers
================================================================================

This module can be run in parallel using MPI if the
:term:`pypar` library is found and all_multipliers is run using the
:term:`mpirun` command. For example, to run with 8 processors::

    mpirun -n 8 python all_multipliers.py

:moduleauthor: Tina Yang <tina.yang@ga.gov.au>

"""


import sys
import os
import time
import inspect
import shutil
import numpy as np
import osgeo.gdal as gdal
import logging as log
import terrain.terrain_mult
import shielding.shield_mult
import topographic.topomult
import ConfigParser
from osgeo.gdalconst import *
from utilities.files import flStartLog
from utilities._execute import execute
from os.path import join as pjoin
from functools import wraps
from functools import reduce

__version__ = '1.0'


class TileGrid(object):

    """
    Tiling to minimise MemoryErrors and enable parallelisation.

    """

    def __init__(self, upwind_length, terrain_map):
        """
        Initialise the tile grid for dividing up the input landcover raster

        :param upwind_length: `float` buffer size of a tile
        :param terrain_map: `file` the input landcover file.

        """

        # register all of the drivers
        gdal.AllRegister()

        # open the image
        ds = gdal.Open(terrain_map, GA_ReadOnly)
        if ds is None:
            log.info('Could not open ' + terrain_map)
            sys.exit(1)

        # get image size, format, projection
        self.x_dim = ds.RasterXSize
        self.y_dim = ds.RasterYSize
        log.info(
            'The input land cover raster format is %s' %
            ds.GetDriver().ShortName +
            '/ %s' %
            ds.GetDriver().LongName)
        log.info('Image size is %s' %
                 str(self.x_dim) +
                 'x %s' %
                 str(self.y_dim))

        # get georeference info
        geotransform = ds.GetGeoTransform()
        self.x_Left = geotransform[0]
        self.y_Upper = -geotransform[3]
        self.pixelWidth = geotransform[1]
        self.pixelHeight = -geotransform[5]
        log.info('Top left corner X,Y: %s' %
                 str(self.x_Left) +
                 ' %s' %
                 str(self.y_Upper))
        log.info('Resolution %s' %
                 str(self.pixelWidth) +
                 'x %s' %
                 str(self.pixelHeight))

        # calculte the size of a tile and its buffer
        self.x_step = int(np.ceil(1.0 / float(self.pixelWidth)))
        self.y_step = int(np.ceil(1.0 / float(self.pixelHeight)))
        log.info('Maximum no. of cells per tile is %s' %
                 str(self.x_step) +
                 'x %s' %
                 str(self.y_step))
        self.x_buffer = int(upwind_length / self.pixelWidth)
        self.y_buffer = int(upwind_length / self.pixelHeight)
        log.info('No. of cells in the buffer of each tile in x and y is %s' %
                 str(self.x_buffer) +
                 ', %s' %
                 str(self.y_buffer))

        self.tileGrid()

    def tileGrid(self):
        """
        Defines the indices required to subset a 2D array into smaller
        rectangular 2D arrays (of dimension x_step * y_step plus buffer
        size for each side if available).

        """

        subset_maxcols = int(np.ceil(self.x_dim / float(self.x_step)))
        subset_maxrows = int(np.ceil(self.y_dim / float(self.y_step)))
        self.num_tiles = subset_maxcols * subset_maxrows
        self.x_start = np.zeros(self.num_tiles, 'i')
        self.x_end = np.zeros(self.num_tiles, 'i')
        self.y_start = np.zeros(self.num_tiles, 'i')
        self.y_end = np.zeros(self.num_tiles, 'i')
        k = 0

        for i in xrange(subset_maxcols):
            for j in xrange(subset_maxrows):
                self.x_start[k] = max(0, i * self.x_step - self.x_buffer)
                self.x_end[k] = min(
                    ((i + 1) * self.x_step + self.x_buffer),
                    self.x_dim) - 1
                self.y_start[k] = max(0, j * self.y_step - self.y_buffer)
                self.y_end[k] = min(
                    ((j + 1) * self.y_step + self.y_buffer),
                    self.y_dim) - 1
                k += 1

    def getGridLimit_buffer(self, k):
        """
        Return the limits with buffer for tile `k`. x-indices correspond to the
        east-west coordinate, y-indices correspond to the north-south
        coordinate.

        :param k: `int` tile number

        :return: minimum, maximum x-index and y-index for tile `k`

        """

        x1 = int(self.x_start[k])
        x2 = int(self.x_end[k] + 1)
        y1 = int(self.y_start[k])
        y2 = int(self.y_end[k] + 1)

        return x1, x2, y1, y2

    def getGridLimit(self, k):
        """
        Return the limits without buffer for tile `k`. x-indices correspond to
        the east-west coordinate, y-indices correspond to the north-south
        coordinate.

        :param k: `int` tile number

        :return: minimum, maximum x-index and y-index for tile `k`

        """

        if int(self.x_start[k]) != 0:
            x1 = int(self.x_start[k] + self.x_buffer)
        else:
            x1 = self.x_start[k]

        if int(self.y_start[k]) != 0:
            y1 = int(self.y_start[k] + self.y_buffer)
        else:
            y1 = self.y_start[k]

        if int(self.x_end[k]) != (self.x_dim - 1):
            x2 = int(self.x_end[k] - self.x_buffer + 1)
        else:
            x2 = self.x_dim

        if int(self.y_end[k]) != (self.y_dim - 1):
            y2 = int(self.y_end[k] - self.y_buffer + 1)
        else:
            y2 = self.y_dim

        return x1, x2, y1, y2

    def getStartCord(self, k):
        """
        Return starting longitude and latitude value of the tile without buffer

        :param k: `int` tile number

        :return: `float` starting x and y coordinate of a tile without buffer

        """
        limits = self.getGridLimit(k)
        tile_x_cord = self.x_Left + limits[0] * self.pixelWidth
        tile_y_cord = self.y_Upper + limits[2] * self.pixelHeight

        return tile_x_cord, tile_y_cord

    def getTileName(self, k):
        """
        Return the name of a tile

        :param k: `int` tile number

        :return: `string` name of a tile composing of starting coordinates

        """

        startCord = self.getStartCord(k)
        name = 'e' + str(startCord[0])[:8] + 's' + str(startCord[1])[:7]

        return name

    def getTileExtent_buffer(self, k):
        """
        Return the exntent for tile `k`. x corresponds to the
        east-west coordinate, y corresponds to the north-south
        coordinate.

        :param k: `int` tile number

        :return: minimum, maximum x and y coordinate for tile `k`

        """

        limits = self.getGridLimit_buffer(k)
        tile_x_start = self.x_Left + limits[0] * self.pixelWidth
        tile_y_start = -(self.y_Upper + limits[2] * self.pixelHeight)
        tile_x_end = self.x_Left + limits[1] * self.pixelWidth
        tile_y_end = -(self.y_Upper + limits[3] * self.pixelHeight)

        return tile_x_start, tile_y_start, tile_x_end, tile_y_end


class Multipliers(object):

    """
    Computing multipliers parallelly based on tiles.

    """

    def __init__(self, terrain_map, dem, cyclone_area):
        """
        Initialise the tile grid for dividing up the input landcover raster

        :param terrain_map: `file` the input landcover file.
        :param dem: `file` the input dem file.
        :param cyclone_area: `file` the input cyclone area file.

        """

        self.input_img = terrain_map
        self.dem = dem
        self.cyclone_area = cyclone_area

    def multipliers_calculate(self, tile_info):
        """
        Calculate the multiplier values for a specific tile

        :param tile_info: `tuple` the input tile info

        """

        tile_name = tile_info[0]
        tile_extents = tile_info[1]

        # get the tile name without buffer using coordinates with 4 decimals
        log.info('The working tile is  %s' % tile_name)

        # extract the temporary tile from terrain class map
        temp_tile = pjoin(output_folder, tile_name + '_input.img')

        log.info('tile_extents = %s', tile_extents)

        command_string = 'gdal_translate -projwin %f %f %f %f ' % (
            tile_extents[0], tile_extents[1], tile_extents[2], tile_extents[3]
        )
        command_string += ' -a_ullr %f %f %f %f ' % (
            tile_extents[0], tile_extents[1], tile_extents[2], tile_extents[3]
        )
        command_string += ' -of HFA'
        command_string += ' %s %s' % (
            self.input_img,
            temp_tile
        )

        log.info(
            'Extract the working tile from the input landcover:\n %s',
            command_string)
        result = execute(command_string=command_string)
        if result['stdout']:
            log.info(
                result['stdout'] +
                'stdout from %s' %
                command_string +
                '\t')
        if result['returncode']:
            log.error(
                result['stderr'] +
                'stderr from %s' %
                command_string +
                '\t')
            raise Exception('%s failed' % command_string)

        # check the checksum value of the terrain map tile, if it is greater
        # than 0, go ahead
        temp_dataset = gdal.Open(temp_tile)
        assert temp_dataset, 'Unable to open dataset %s' % temp_tile
        band = temp_dataset.GetRasterBand(1)
        checksum = band.Checksum()
        log.info('This landcover tile checksum is %s ' % str(checksum))
        print 'landcover checksum ' + str(checksum)

        if checksum > 0:
            # extract the temporary tile from DEM
            temp_tile_dem = pjoin(output_folder, tile_name + '_dem.img')

            command_string = 'gdal_translate -projwin %f %f %f %f ' % (
                tile_extents[0], tile_extents[1],
                tile_extents[2], tile_extents[3]
            )
            command_string += ' -a_ullr %f %f %f %f ' % (
                tile_extents[0], tile_extents[1],
                tile_extents[2], tile_extents[3]
            )
            command_string += ' -of HFA'
            command_string += ' %s %s' % (
                self.dem,
                temp_tile_dem
            )

            log.info(
                'Extract the working tile from the input DEM:\n %s',
                command_string)
            result = execute(command_string=command_string)
            if result['stdout']:
                log.info(
                    result['stdout'] +
                    'stdout from %s' %
                    command_string +
                    '\t')
            if result['returncode']:
                log.error(
                    result['stderr'] +
                    'stderr from %s' %
                    command_string +
                    '\t')
                raise Exception('%s failed' % command_string)

            # extract the temporary tile from Cyclone area
            temp_tile_cyclone = pjoin(output_folder, tile_name + '_cyc.img')

            command_string = 'gdal_translate -projwin %f %f %f %f ' % (
                tile_extents[0], tile_extents[1],
                tile_extents[2], tile_extents[3]
            )
            command_string += ' -a_ullr %f %f %f %f ' % (
                tile_extents[0], tile_extents[1],
                tile_extents[2], tile_extents[3]
            )
            command_string += ' -of HFA'
            command_string += ' %s %s' % (
                self.cyclone_area,
                temp_tile_cyclone
            )

            log.info(
                'Extract the working tile from input cyclonic region:\n %s',
                command_string)
            result = execute(command_string=command_string)
            if result['stdout']:
                log.info(
                    result['stdout'] +
                    'stdout from %s' %
                    command_string +
                    '\t')
            if result['returncode']:
                log.error(
                    result['stderr'] +
                    'stderr from %s' %
                    command_string +
                    '\t')
                raise Exception('%s failed' % command_string)

            # check the checksum value of the cyclone map tile, if it greater
            # than 0, it is cyclone area
            temp_dataset_cycl = gdal.Open(temp_tile_cyclone)
            band = temp_dataset_cycl.GetRasterBand(1)
            checksum = band.Checksum()
            log.info(
                'This cyclonic region tile checksum is %s ' %
                str(checksum))
            print 'cyclone checksum ' + str(checksum)

            if checksum > 0:
                cyclone_area = temp_tile_cyclone
            else:
                cyclone_area = None

            # resample the terrain as DEM
            temp_dataset_DEM = gdal.Open(temp_tile_dem)

            terrain_resample = pjoin(output_folder, tile_name + '_ter.img')

            command_string = 'gdal_translate -outsize %i %i' % (
                temp_dataset_DEM.RasterXSize, temp_dataset_DEM.RasterYSize
            )
            command_string += ' -of HFA'
            command_string += ' %s %s' % (
                temp_tile,
                terrain_resample
            )

            log.info(
                'Resample the landcover tile the same as the DEM tile:\n %s',
                command_string)
            result = execute(command_string=command_string)
            if result['stdout']:
                log.info(
                    result['stdout'] +
                    'stdout from %s' %
                    command_string +
                    '\t')
            if result['returncode']:
                log.error(
                    result['stderr'] +
                    'stderr from %s' %
                    command_string +
                    '\t')
                raise Exception('%s failed' % command_string)

            # start to calculate the multipliers
            log.info('producing Terrain multipliers ...')
            terrain.terrain_mult.terrain(cyclone_area, terrain_resample)

            log.info('producing Shielding multipliers ...')
            shielding.shield_mult.shield(terrain_resample, temp_tile_dem)

            log.info('producing Topographic multipliers ...')
            topographic.topomult.topomult(temp_tile_dem)

            os.remove(temp_tile_dem)
            os.remove(temp_tile)
            os.remove(terrain_resample)
            os.remove(temp_tile_cyclone)
        else:
            if os.path.exists(temp_tile):
                os.remove(temp_tile)

    def paralleliseOnTiles(self, tiles, progressCallback=None):
        """
        Iterate over tiles to calculate the wind multipliers

        :param tiles: `generator` that yields tuples of tile dimensions.

        """

        work_tag = 0
        result_tag = 1
        if (pp.rank() == 0) and (pp.size() > 1):
            w = 0
            p = pp.size() - 1
            for d in range(1, pp.size()):
                if w < len(tiles):
                    pp.send(tiles[w], destination=d, tag=work_tag)
                    log.debug("Processing tile %d of %d" % (w, len(tiles)))
                    w += 1
                else:
                    pp.send(None, destination=d, tag=work_tag)
                    p = w

            terminated = 0

            while(terminated < p):

                result, status = pp.receive(pp.any_source, tag=result_tag,
                                            return_status=True)

                d = status.source

                if w < len(tiles):
                    pp.send(tiles[w], destination=d, tag=work_tag)
                    log.debug("Processing tile %d of %d" % (w, len(tiles)))
                    w += 1
                else:
                    pp.send(None, destination=d, tag=work_tag)
                    terminated += 1

                log.debug("Number of terminated threads is %d" % terminated)

                if progressCallback:
                    progressCallback(w)

        elif (pp.size() > 1) and (pp.rank() != 0):
            while(True):
                W = pp.receive(source=0, tag=work_tag)
                if W is None:
                    break
                status = self.multipliers_calculate(W)
                pp.send(status, destination=0, tag=result_tag)

        elif pp.size() == 1 and pp.rank() == 0:
            # Assumed no Pypar - helps avoid the need to extend DummyPypar()
            for i, tile in enumerate(tiles):
                log.debug("Processing tile %d of %d" % (i, len(tiles)))
                self.multipliers_calculate(tile)

                if progressCallback:
                    progressCallback(i)


def getTiles(tilegrid):
    """
    Helper to obtain a generator that yields tile numbers

    :param tilegrid: :class:`TileGrid` instance

    """

    tilenums = range(tilegrid.num_tiles)
    return getTileInfo(tilegrid, tilenums)


def getTileInfo(tilegrid, tilenums):
    """
    Generate a list of tuples of the name and extent of a tile

    :param tilegrid: :class:`TileGrid` instance
    :param tilenums: list of tile numbers (must be sequential)

    :returns: tileinfo: list of tuples of tile names and extents

    """

    tile_info = [
        [tilegrid.getTileName(t), tilegrid.getTileExtent_buffer(t)]
        for t in tilenums]
    return tile_info


def timer(f):
    """
    Basic timing functions for entire process
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        t1 = time.time()
        res = f(*args, **kwargs)

        tottime = time.time() - t1
        msg = "%02d:%02d:%02d " % \
            reduce(lambda ll, b: divmod(ll[0], b) + ll[1:],
                   [(tottime,), 60, 60])

        log.info("Time for %s: %s" % (f.func_name, msg))
        return res

    return wrap


def disableOnWorkers(f):
    """
    Disable function calculation on workers. Function will
    only be evaluated on the master.
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        if pp.size() > 1 and pp.rank() > 0:
            return
        else:
            return f(*args, **kwargs)
    return wrap


@disableOnWorkers
def doOutputDirectoryCreation(root):
    """
    Create all the necessary output folders.

    :param root: `string` Name of root directory
    :raises OSError: If the directory tree cannot be created.

    """

    output = pjoin(root, 'output')

    log.info('Output will be stored under %s', output)

    subdirs_1 = ['terrain', 'shielding', 'topographic']
    subdirs_2 = ['netcdf']

    if os.path.exists(output):
        shutil.rmtree(output)
    try:
        os.makedirs(output)
    except OSError:
        raise

    for subdir in subdirs_1:
        out_sub1 = pjoin(output, subdir)
        if os.path.exists(out_sub1):
            shutil.rmtree(out_sub1)
        try:
            os.makedirs(out_sub1)
        except OSError:
            raise

        for sub2 in subdirs_2:
            out_sub2 = pjoin(out_sub1, sub2)
            if os.path.exists(out_sub2):
                shutil.rmtree(out_sub2)
            try:
                os.makedirs(out_sub2)
            except OSError:
                raise


def balanced(iterable):
    """
    Balance an iterator across processors.

    This partitions the work evenly across processors. However, it requires
    the iterator to have been generated on all processors before hand. This is
    only some magical slicing of the iterator, i.e., a poor man version of
    scattering.
    """

    P, p = pp.size(), pp.rank()
    return itertools.islice(iterable, p, None, P)


def balance(N):
    """
    Compute p'th interval when N is distributed over P bins
    """

    P, p = pp.size(), pp.rank()
    L = int(np.floor(float(N) / P))
    K = N - P * L
    if p < K:
        Nlo = p * L + p
        Nhi = Nlo + L + 1
    else:
        Nlo = p * L + K
        Nhi = Nlo + L

    return Nlo, Nhi


def attemptParallel():
    """
    Attempt to load Pypar globally as `pp`.  If pypar cannot be loaded then a
    dummy `pp` is created.
    """

    global pp

    try:
        # load pypar for everyone

        import pypar as pp
        import atexit
        atexit.register(pp.finalize)

    except ImportError:

        # no pypar, create a dummy one

        class DummyPypar(object):

            def size(self):
                return 1

            def rank(self):
                return 0

            def barrier(self):
                pass

            def finalize(self):
                pass

        pp = DummyPypar()


@timer
def run(callback=None):
    """
    Run the wind multiplier calculations.

    This will attempt to run the calculation in parallel by tiling the
    domain, but also provides a sane fallback mechanism to execute
    in serial.

    """

    # add subfolders into path
    cmd_folder = os.path.realpath(
        os.path.abspath(
            os.path.split(
                inspect.getfile(
                    inspect.currentframe()))[0]))
    if cmd_folder not in sys.path:
        sys.path.insert(0, cmd_folder)

    cmd_subfolder1 = pjoin(cmd_folder, "terrain")
    if cmd_subfolder1 not in sys.path:
        sys.path.insert(0, cmd_subfolder1)

    cmd_subfolder2 = pjoin(cmd_folder, "shielding")
    if cmd_subfolder2 not in sys.path:
        sys.path.insert(0, cmd_subfolder2)

    cmd_subfolder3 = pjoin(cmd_folder, "topographic")
    if cmd_subfolder3 not in sys.path:
        sys.path.insert(0, cmd_subfolder2)

    cmd_subfolder4 = pjoin(cmd_folder, "utilities")
    if cmd_subfolder4 not in sys.path:
        sys.path.insert(0, cmd_subfolder2)

    config = ConfigParser.RawConfigParser()
    config.read(pjoin(cmd_folder, 'multiplier_conf.cfg'))

    root = config.get('inputValues', 'root')
    upwind_length = float(config.get('inputValues', 'upwind_length'))

    logfile = 'multipliers.log'
    loglevel = 'INFO'
    verbose = False

    attemptParallel()

    if pp.size() > 1 and pp.rank() > 0:
        logfile += '_' + str(pp.rank())
        verbose = False
    else:
        pass

    flStartLog(logfile, loglevel, verbose)

    # set input maps and output folder
    terrain_map = pjoin(pjoin(root, 'input'), "lc_terrain_class_test_5.img")
    #terrain_map = pjoin(pjoin(root, 'input'), "lc_terrain_class.img")
    #terrain_map = pjoin(pjoin(root, 'input'), "TestLandCoverData.img")
    dem = pjoin(pjoin(root, 'input'), "dems1_whole.img")
    #dem = pjoin(pjoin(root, 'input'), "TestDEMFlatTerrain.img")
    #dem = pjoin(pjoin(root, 'input'), "testDEMPercentSlope.img")
    #dem = pjoin(pjoin(root, 'input'), "ZeroBackground.img")
    cyclone_area = pjoin(pjoin(root, 'input'), "cyclone_dem_extent.img")

    doOutputDirectoryCreation(root)
    global output_folder
    output_folder = pjoin(root, 'output')

    log.info("get the tiles")
    TG = TileGrid(upwind_length, terrain_map)
    tiles = getTiles(TG)
    log.info('the number of tiles is %s' % str(len(tiles)))

    pp.barrier()

    multiplier = Multipliers(terrain_map, dem, cyclone_area)
    multiplier.paralleliseOnTiles(tiles)

    pp.barrier()

    log.info("Successfully completed wind multipliers calculation")


if __name__ == '__main__':
    run()
