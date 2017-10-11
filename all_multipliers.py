"""
:mod:`all_multipliers` - Calculate terrain, shielding & topographic multipliers
===============================================================================

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
from osgeo import osr, gdal
import logging as log
import terrain.terrain_mult
import shielding.shield_mult
import topographic.topo_mult
import ConfigParser
from osgeo.gdalconst import GA_ReadOnly, GRA_NearestNeighbour
from osgeo.gdalconst import GDT_Float32, GDT_Int32
from utilities.files import fl_start_log
from os.path import join as pjoin, realpath, isdir, dirname
from functools import wraps
import itertools

__version__ = '2.0'


class TileGrid(object):

    """
    Tiling to minimise MemoryErrors and enable parallelisation.

    """

    def __init__(self, upwind_length, raster_ds):
        """
        Initialise the tile grid for dividing up the input raster

        :param upwind_length: `float` buffer size of a tile
        :param raster_ds: `file` the input raster file.

        """

        # register all of the drivers
        gdal.AllRegister()

        # open the image
        ds = gdal.Open(raster_ds, GA_ReadOnly)
        if ds is None:
            log.info('Could not open ' + raster_ds)
            sys.exit(1)

        # get image size, format
        self.x_dim = ds.RasterXSize
        self.y_dim = ds.RasterYSize
        log.info('The input raster format is %s' %
                 ds.GetDriver().ShortName + '/ %s' %
                 ds.GetDriver().LongName)
        log.info('Image size is %s' %
                 str(self.x_dim) + 'x %s' %
                 str(self.y_dim))

        # get georeference info
        geotransform = ds.GetGeoTransform()
        self.x_left = geotransform[0]
        self.y_upper = -geotransform[3]
        self.pixelwidth = geotransform[1]
        self.pixelheight = -geotransform[5]
        log.info('Top left corner X,Y: %s' %
                 str(self.x_left) + ' %s' %
                 str(self.y_upper))
        log.info('Resolution %s' %
                 str(self.pixelwidth) + 'x %s' %
                 str(self.pixelheight))

        # calculte the size of a tile and its buffer
        self.x_step = int(np.ceil(1.0 / float(self.pixelwidth)))
        self.y_step = int(np.ceil(1.0 / float(self.pixelheight)))
        log.info('Maximum no. of cells per tile is %s' %
                 str(self.x_step) + 'x %s' %
                 str(self.y_step))
        self.x_buffer = int(upwind_length / self.pixelwidth)
        self.y_buffer = int(upwind_length / self.pixelheight)
        log.info('No. of cells in the buffer of each tile in x and y is %s' %
                 str(self.x_buffer) + ', %s' %
                 str(self.y_buffer))

        self.subset_maxcols = int(np.ceil(self.x_dim / float(self.x_step)))
        self.subset_maxrows = int(np.ceil(self.y_dim / float(self.y_step)))
        self.num_tiles = self.subset_maxcols * self.subset_maxrows
        self.x_start = np.zeros(self.num_tiles, 'i')
        self.x_end = np.zeros(self.num_tiles, 'i')
        self.y_start = np.zeros(self.num_tiles, 'i')
        self.y_end = np.zeros(self.num_tiles, 'i')

        self.tile_grid()

        ds = None

    def tile_grid(self):
        """
        Defines the indices required to subset a 2D array into smaller
        rectangular 2D arrays (of dimension x_step * y_step plus buffer
        size for each side if available).

        """

        k = 0

        for i in xrange(self.subset_maxcols):
            for j in xrange(self.subset_maxrows):
                self.x_start[k] = max(0, i * self.x_step - self.x_buffer)
                self.x_end[k] = min(
                    ((i + 1) * self.x_step + self.x_buffer),
                    self.x_dim) - 1
                self.y_start[k] = max(0, j * self.y_step - self.y_buffer)
                self.y_end[k] = min(
                    ((j + 1) * self.y_step + self.y_buffer),
                    self.y_dim) - 1
                k += 1

    def get_gridlimit_buffer(self, k):
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

    def get_gridlimit(self, k):
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

    def get_startcord(self, k):
        """
        Return starting longitude and latitude value of the tile without buffer

        :param k: `int` tile number

        :return: `float` starting x and y coordinate of a tile without buffer

        """
        limits = self.get_gridlimit(k)
        tile_x_cord = self.x_left + limits[0] * self.pixelwidth
        tile_y_cord = self.y_upper + limits[2] * self.pixelheight

        return tile_x_cord, tile_y_cord

    def get_tilename(self, k):
        """
        Return the name of a tile

        :param k: `int` tile number

        :return: `string` name of a tile composing of starting coordinates

        """

        start_cord = self.get_startcord(k)
        name = 'e' + str(start_cord[0])[:8] + 's' + str(start_cord[1])[:7]

        return name

    def get_tile_extent_buffer(self, k):
        """
        Return the exntent for tile `k`. x corresponds to the
        east-west coordinate, y corresponds to the north-south
        coordinate.

        :param k: `int` tile number

        :return: minimum, maximum x and y coordinate for tile `k`

        """

        limits = self.get_gridlimit_buffer(k)
        tile_x_start = self.x_left + limits[0] * self.pixelwidth
        tile_y_start = -(self.y_upper + limits[2] * self.pixelheight)
        tile_x_end = self.x_left + limits[1] * self.pixelwidth
        tile_y_end = -(self.y_upper + limits[3] * self.pixelheight)

        return tile_x_start, tile_y_start, tile_x_end, tile_y_end

    def get_tile_extent(self, k):
        """
        Return the exntent without buffer for tile `k`. x corresponds to the
        east-west coordinate, y corresponds to the north-south
        coordinate.

        :param k: `int` tile number

        :return: minimum, maximum x and y coordinate for tile `k`

        """

        limits = self.get_gridlimit(k)
        tile_x_start = self.x_left + limits[0] * self.pixelwidth
        tile_y_start = -(self.y_upper + limits[2] * self.pixelheight)
        tile_x_end = self.x_left + limits[1] * self.pixelwidth
        tile_y_end = -(self.y_upper + limits[3] * self.pixelheight)

        return tile_x_start, tile_y_start, tile_x_end, tile_y_end


class Multipliers(object):

    """
    Computing multipliers parallelly based on tiles.

    """

    def __init__(self, landcover, dem):
        """
        Initialise the tile grid for dividing up the input landcover raster

        :param landcover: `file` the input landcover file.
        :param dem: `file` the input dem file.

        """

        # initialising the multiplier class
        self.lcv = landcover
        self.dem = dem
        self.dem_ds = None

    def open_dem(self):
        """
        Open the DEM file

        """

        if not os.path.exists(self.dem):
            log.critical('DEM file does not exist: {0}'.format(self.dem))
            raise OSError
        self.dem_ds = gdal.Open(self.dem, GA_ReadOnly)
        if self.dem_ds is None:
            log.critical('Could not open {0}. Check file format?'.format(self.dem))
            raise IOError
        
        # get georeference info
        geotransform = self.dem_ds.GetGeoTransform()
        self.pixelwidth = geotransform[1]
        self.pixelheight = -geotransform[5]

        dem_band = self.dem_ds.GetRasterBand(1)
        self.dem_type = dem_band.ReadAsArray().dtype

        self.dem_proj = self.dem_ds.GetProjection()

    def cut_dem(self, tile_info):
        """
        Cut from the input DEM for a tile

        :param tile_info: `tuple` the input tile info

        :return: `file` the output dem for a tile

        """

        tile_name = tile_info[0]
        tile_extents = tile_info[1]

        # get the tile name without buffer using coordinates with 4 decimals
        log.info('The working tile is {0}'.format(tile_name))
        log.info('tile_extents = %s', tile_extents)
        log.info('Extract the working tile from the input DEM')

        # extract the temporary tile from the dem
        temp_tile_dem = pjoin(output_folder, tile_name + '_dem.img')
        self.clip_dataset(tile_extents, temp_tile_dem)

        return temp_tile_dem

    def clip_dataset(self, extent, dst_filename):
        """
        Clip the DEM using an extent and save the clipped to a new file.

        :param extent: `tuple` the input tile extent with buffer
        :param str dst_filename: destination filename.

        """

        log.debug("Clipping the DEM using extent: {0}".format(repr(extent)))
        log.debug("into output raster: {0}".format(dst_filename))

        if self.dem_type == 'int32':
            dst_type = GDT_Int32
        else:
            dst_type = GDT_Float32

        origin_x, origin_y = extent[0], extent[1]

        wide = int(np.around((extent[2] - extent[0])/self.pixelwidth))
        high = int(np.around((extent[1] - extent[3])/self.pixelheight))

        # Output / destination
        drv = gdal.GetDriverByName('HFA')
        dst = drv.Create(dst_filename, wide, high, 1, dst_type)
        dst.SetGeoTransform((origin_x, self.pixelwidth, 0, origin_y, 0,
                             -self.pixelheight))
        dst.SetProjection(self.dem_proj)

        # Do the work
        gdal.ReprojectImage(self.dem_ds, dst, self.dem_proj, self.dem_proj)

        del dst  # Flush

        return

    def multipliers_calculate(self, temp_tile_dem, tile_info):
        """
        Calculate the multiplier values for a specific tile

        :param temp_tile_dem: `file` the input DEM tile
        :param tile_info: `tuple` the input tile info

        """

        tile_name = tile_info[0]
        tile_extents_nobuffer = tile_info[2]

        # check the checksum value of the terrain map tile, if it is greater
        # than 0, go ahead
        temp_dataset = gdal.Open(temp_tile_dem)
        assert temp_dataset, 'Unable to open dataset %s' % temp_tile_dem
        band = temp_dataset.GetRasterBand(1)
        checksum = band.Checksum()
        log.info('This DEM tile checksum is {0}'.format(str(checksum)))

        if checksum > 0:
            # extract the temporary tile from landcover
            terrain_resample = pjoin(output_folder, tile_name + '.img')

            log.info('Extract the working tile from the input landcover to '
                     'match the DEM tile')
            reproject_dataset(self.lcv, temp_dataset, terrain_resample)

            # start to calculate the multipliers
            log.info('producing Terrain multipliers ...')
            terrain.terrain_mult.terrain(terrain_resample,
                                         tile_extents_nobuffer)

            log.info('producing Shielding multipliers ...')
            shielding.shield_mult.shield(terrain_resample, temp_tile_dem,
                                         tile_extents_nobuffer)

            log.info('producing Topographic multipliers ...')
            topographic.topo_mult.topomult(temp_tile_dem,
                                           tile_extents_nobuffer)

            log.info('deleting the temporary files after calculation ...')
            log.info('deleteing the temporary DEM: {0}'
                     .format(temp_tile_dem))
            os.remove(temp_tile_dem)
            log.info('deleteing the temporary resampled landcover: {0}'
                     .format(terrain_resample))
            os.remove(terrain_resample)

            temp_dataset = None
        else:
            log.info('deleteing the temporary empty DEM: {0}'
                     .format(temp_tile_dem))
            if os.path.exists(temp_tile_dem):
                os.remove(temp_tile_dem)

            temp_dataset = None

    def parallelise_on_tiles(self, tiles, progress_callback=None):
        """
        Iterate over tiles to calculate the wind multipliers

        :param tiles: `generator` that yields tuples of tile dimensions.

        """

        work_tag = 0
        result_tag = 1
        if (pp.rank() == 0) and (pp.size() > 1):

            if not self.dem_ds:
                self.open_dem()
            w = 0
            p = pp.size() - 1
            for d in range(1, pp.size()):
                if w < len(tiles):
                    dem_tile = self.cut_dem(tiles[w])
                    pp.send([dem_tile, tiles[w]], destination=d, tag=work_tag)
                    log.debug("Processing tile {0}({1}) of {2} on {3}".format(
                              w, tiles[w], len(tiles), d))
                    w += 1
                else:
                    pp.send(None, destination=d, tag=work_tag)
                    p = w

            terminated = 0

            while(terminated < p):

                status = pp.receive(pp.any_source, tag=result_tag,
                                    return_status=True)[1]

                d = status.source
                log.debug("Returned from {0}".format(d))

                if w < len(tiles):
                    dem_tile = self.cut_dem(tiles[w])
                    pp.send([dem_tile, tiles[w]], destination=d, tag=work_tag)
                    log.debug("Processing tile {0}({1}) of {2} on {3}".format(
                              w, tiles[w], len(tiles), d))
                    w += 1
                else:
                    pp.send(None, destination=d, tag=work_tag)
                    terminated += 1

                    log.debug("Number of terminated threads is {0}".format(
                              terminated))

                if progress_callback:
                    progress_callback(w)

        elif (pp.size() > 1) and (pp.rank() != 0):
            while(True):
                ww = pp.receive(source=0, tag=work_tag)
                if ww is None:
                    break
                status = self.multipliers_calculate(ww[0], ww[1])
                pp.send(status, destination=0, tag=result_tag)

        elif pp.size() == 1 and pp.rank() == 0:
            # Assumed no Pypar - helps avoid the need to extend DummyPypar()
            if not self.dem_ds:
                self.open_dem()
            for i, tile in enumerate(tiles):
                dem_tile = self.cut_dem(tile)
                log.debug("Processing tile {0} of {1}".format(i,
                          len(tiles)))
                self.multipliers_calculate(dem_tile, tile)

                if progress_callback:
                    progress_callback(i)


def get_tiles(tilegrid):
    """
    Helper to obtain a generator that yields tile numbers

    :param tilegrid: :class:`TileGrid` instance

    """

    tilenums = range(tilegrid.num_tiles)
    return get_tileinfo(tilegrid, tilenums)


def get_tileinfo(tilegrid, tilenums):
    """
    Generate a list of tuples of the name and extent of a tile

    :param tilegrid: :class:`TileGrid` instance
    :param tilenums: list of tile numbers (must be sequential)

    :returns: tileinfo: list of tuples of tile names and extents

    """

    tile_info = [
        [tilegrid.get_tilename(t), tilegrid.get_tile_extent_buffer(t),
         tilegrid.get_tile_extent(t)] for t in tilenums]
    return tile_info


def timer(f):
    """
    Basic timing functions for entire process
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        """
        Wrap
        """

        t1 = time.time()
        res = f(*args, **kwargs)

        tottime = time.time() - t1
        msg = "%02d:%02d:%02d " % \
            reduce(lambda ll, b: divmod(ll[0], b) + ll[1:],
                   [(tottime,), 60, 60])

        log.info("Time for {0}:{1}".format(f.func_name, msg))
        return res

    return wrap


def disable_on_workers(f):
    """
    Disable function calculation on workers. Function will
    only be evaluated on the master.
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        """
        wrap
        """

        if pp.size() > 1 and pp.rank() > 0:
            return
        else:
            return f(*args, **kwargs)
    return wrap


@disable_on_workers
def do_output_directory_creation(root):
    """
    Create all the necessary output folders.

    :param root: `string` Name of root directory
    :raises OSError: If the directory tree cannot be created.

    """

    output = pjoin(root, 'output')

    log.info('Output will be stored under %s', output)

    subdirs_1 = ['terrain', 'shielding', 'topographic']

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


@timer
def reproject_dataset(src_file, match_filename, dst_filename,
                      resampling_method=GRA_NearestNeighbour,
                      match_projection=None):
    """
    Clip and reproject a source dataset to match the projection of another
    dataset and save the projected dataset to a new file.

    :param src_filename: Filename of the source raster dataset, or an
                         open :class:`gdal.Dataset`
    :param match_filename: Filename of the dataset to match to, or an
                           open :class:`gdal.Dataset`
    :param str dst_filename: Destination filename.
    :param resampling_method: Resampling method. Default is bilinear
                              interpolation.
    :param match_projection: Projection of the output

    """

    log.debug("Reprojecting {0}".format(repr(src_file)))
    log.debug("Match raster: {0}".format(repr(match_filename)))
    log.debug("Output raster: {0}".format(dst_filename))

    if type(src_file) == str:
        src = gdal.Open(src_file, GA_ReadOnly)
        if src is None:
            log.info('Could not open ' + src)
            sys.exit(1)
    else:
        src = src_file

    src_band = src.GetRasterBand(1)
    src_type = src_band.ReadAsArray().dtype

    if src_type == 'int32':
        dst_type = GDT_Int32
    else:
        dst_type = GDT_Float32

    src_proj = src.GetProjection()

    # We want a section of source that matches this:
    if type(match_filename) == str:
        match_ds = gdal.Open(match_filename, GA_ReadOnly)
        if match_ds is None:
            log.info('Could not open ' + match_ds)
            sys.exit(1)
    else:
        match_ds = match_filename

    if match_projection:
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(match_projection)
        match_proj = srs.ExportToWkt()
    else:
        match_proj = match_ds.GetProjection()

    match_geotrans = match_ds.GetGeoTransform()
    wide = match_ds.RasterXSize
    high = match_ds.RasterYSize

    # Output / destination
    drv = gdal.GetDriverByName('HFA')
    dst = drv.Create(dst_filename, wide, high, 1, dst_type)
    dst.SetGeoTransform(match_geotrans)
    dst.SetProjection(match_proj)

    # Do the work
    gdal.ReprojectImage(src, dst, src_proj, match_proj, resampling_method)

    del dst  # Flush
    if type(match_filename) == str:
        del match_ds
    if type(src_file) == str:
        del src

    return


def balanced(iterable):
    """
    Balance an iterator across processors.

    This partitions the work evenly across processors. However, it requires
    the iterator to have been generated on all processors before hand. This is
    only some magical slicing of the iterator, i.e., a poor man version of
    scattering.
    """

    s, p = pp.size(), pp.rank()
    return itertools.islice(iterable, p, None, s)


def balance(nn):
    """
    Compute p'th interval when nn is distributed over s bins
    """

    s, p = pp.size(), pp.rank()
    l = int(np.floor(float(nn) / s))
    k = nn - s * l
    if p < k:
        nlo = p * l + p
        nhi = nlo + l + 1
    else:
        nlo = p * l + k
        nhi = nlo + l

    return nlo, nhi


def attempt_parallel():
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
            """
            Create dummy pypar
            """

            def size(self):
                """
                define size
                """
                return 1

            def rank(self):
                """
                define rank
                """
                return 0

            def barrier(self):
                """
                define barrier
                """
                pass

            def finalize(self):
                """
                define finalize
                """
                pass

        pp = DummyPypar()


@timer
def run():
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
        sys.path.insert(0, cmd_subfolder3)

    cmd_subfolder4 = pjoin(cmd_folder, "utilities")
    if cmd_subfolder4 not in sys.path:
        sys.path.insert(0, cmd_subfolder4)

    config = ConfigParser.RawConfigParser()
    config.read(pjoin(cmd_folder, 'multiplier_conf.cfg'))

    root = config.get('inputValues', 'root')
    upwind_length = float(config.get('inputValues', 'upwind_length'))

    logfile = config.get('Logging', 'LogFile')
    logdir = dirname(realpath(logfile))

    # If log file directory does not exist, create it
    if not isdir(logdir):
        try:
            os.makedirs(logdir)
        except OSError:
            logfile = pjoin(os.getcwd(), 'multipliers.log')

    loglevel = config.get('Logging', 'LogLevel')
    verbose = config.getboolean('Logging', 'Verbose')

    if verbose:
        verbose = True
    else:
        verbose = False

    attempt_parallel()

    if pp.size() > 1 and pp.rank() > 0:
        logfile += '_' + str(pp.rank())
        verbose = False
    else:
        pass

    fl_start_log(logfile, loglevel, verbose)

    # set input maps and output folder
    terrain_map = config.get('inputValues', 'terrain_data')
    dem = config.get('inputValues', 'dem_data')

    do_output_directory_creation(root)
    global output_folder
    output_folder = pjoin(root, 'output')

    log.info("get the tiles based on the DEM")
    tg = TileGrid(upwind_length, dem)
    tiles = get_tiles(tg)
    log.info('the number of tiles is {0}'.format(str(len(tiles))))

    pp.barrier()

    multiplier = Multipliers(terrain_map, dem)
    multiplier.parallelise_on_tiles(tiles)

    pp.barrier()

    log.info("Successfully completed wind multipliers calculation")


if __name__ == '__main__':
    run()
