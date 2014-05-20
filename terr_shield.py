# ---------------------------------------------------------------------------
# Purpose: transfer the landsat classied image into shielding multplier
# Input: loc, input raster file format: loc + '_terrain_class.img', dem
# Output: loc + '_ms' in each direction
# Created on 12 08 2011 by Tina Yang
# ---------------------------------------------------------------------------

    
# Import system & process modules
import sys, string, os, time, inspect, shutil, numpy as np, osgeo.gdal as gdal, logging as log
import terrain.terrain
import shielding.shielding
import topographic.topomult
import ConfigParser
from osgeo.gdalconst import *
from files import flStartLog
from _execute import execute
from os.path import join as pjoin
from functools import wraps


class TileGrid(object):    
    """    
    Tiling to minimise MemoryErrors and enable parallelisation.
    
    Parameters:    
    -----------        
    
    :param gridLimit: :class:`dict` the domain where the hazard will                       
                        be calculated. The :class:`dict` should contain                       
                        the keys :attr:`xMin`, :attr:`xMax`,                       
                        :attr:`yMin` and :attr:`yMax`. The *x* variable                       
                        bounds the longitude and the *y* variable bounds                      
                        the latitude.    
    
    :param wf_lon: `numpy.ndarray` of longitudes of the wind field    
    :param wf_lat: `numpy.ndarray` of latitudes of the wind field    
    :param xstep: `int` size of the tile in the x-direction.    
    :param ystep: `int` size of the tile in the y-direction.    
    
    """    
    
    def __init__(self, upwind_length, terrain_map):        
        """        
        Initialise the tile grid for dividing up the domain                
        
        Parameters:        
        -----------        
        
        :param gridLimit: :class:`dict` describing the domain where the                           
                            tracks will be generated.                          
                            The :class:`dict` should contain the keys :attr:`xMin`,                          
                            :attr:`xMax`, :attr:`yMin` and :attr:`yMax`. The *y*                          
                            variable bounds the latitude and the *x* variable                           
                            bounds the longitude.                
                            
        :param wf_lon: `numpy.ndarray` of longitudes in thw wind field.        
        :param wf_lat: `numpy.ndarray` of latitudes of the wind field.        
        :param xstep: `int` size of the tile in the x-direction.        
        :param ystep: `int` size of the tile in the y-direction.        
        
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
        log.info('The input land cover raster format is %s' % ds.GetDriver().ShortName + '/ %s' % ds.GetDriver().LongName)
        log.info('Image size is %s' % str(self.x_dim) + 'x %s' % str(self.y_dim))
    
        # get georeference info
        geotransform = ds.GetGeoTransform()
        self.x_Left = geotransform[0]
        self.y_Upper = -geotransform[3]
        self.pixelWidth = geotransform[1]
        self.pixelHeight = -geotransform[5]
        log.info('Top left corner X,Y: %s' % str(self.x_Left) + ' %s' % str(self.y_Upper))
        log.info('Resolution %s' % str(self.pixelWidth) + 'x %s' % str(self.pixelHeight)) 
        
        self.x_step = int(np.ceil(1.0/float(self.pixelWidth))) 
        self.y_step = int(np.ceil(1.0/float(self.pixelHeight)))
        log.info('Tile size is %s' % str(self.x_step) + 'x %s' % str(self.y_step))
        self.upwind_length = upwind_length        
        self.x_buffer = int(upwind_length/self.pixelWidth)
        self.y_buffer = int(upwind_length/self.pixelHeight)
        log.info('Tile buffer size is %s' % str(self.x_buffer) + 'x %s' % str(self.y_buffer))             
        
        self.tileGrid()         
         
      
        
    def tileGrid(self):        
        """        
        Defines the indices required to subset a 2D array into smaller        
        rectangular 2D arrays (of dimension x_step * y_step).          
        """        
        
        subset_maxcols = int(np.ceil(self.x_dim/float(self.x_step)))        
        subset_maxrows = int(np.ceil(self.y_dim/float(self.y_step)))        
        self.num_tiles = subset_maxcols * subset_maxrows        
        self.x_start = np.zeros(self.num_tiles, 'i')        
        self.x_end = np.zeros(self.num_tiles, 'i')        
        self.y_start = np.zeros(self.num_tiles, 'i')        
        self.y_end = np.zeros(self.num_tiles, 'i')        
        k = 0 
        
        for i in xrange(subset_maxcols):  
            for j in xrange(subset_maxrows):
                self.x_start[k] = max(0, i*self.x_step - self.x_buffer)             
                self.x_end[k] = min(((i+1)*self.x_step + self.x_buffer), self.x_dim)-1                
                self.y_start[k] = max(0, j*self.y_step - self.y_buffer)              
                self.y_end[k] = min(((j+1)*self.y_step + self.y_buffer), self.y_dim)-1                
                k += 1        
                        
                
    def getGridLimit_buffer(self, k):        
        """        
        Return the limits for tile `k`. x-indices correspond to the         
        east-west coordinate, y-indices correspond to the north-south        
        coordinate.        
        
        Parameters:        
        -----------        
        
        :param k: `int` tile number        
        
        Returns:        
        --------        
        
        :param x1: minimum x-index for tile `k`        
        :param x2: maximum x-index for tile `k`        
        :param y1: minimum y-index for tile `k`        
        :param y2: maximum y-index for tile `k`        
        
        """        
        
        x1 = int(self.x_start[k])        
        x2 = int(self.x_end[k] + 1)        
        y1 = int(self.y_start[k])        
        y2 = int(self.y_end[k] + 1)        
        
        return x1, x2, y1, y2    
    
    
    def getGridLimit(self, k):        
        """        
        Return the limits for tile `k`. x-indices correspond to the         
        east-west coordinate, y-indices correspond to the north-south        
        coordinate.        
        
        Parameters:        
        -----------        
        
        :param k: `int` tile number        
        
        Returns:        
        --------        
        
        :param x1: minimum x-index for tile `k`        
        :param x2: maximum x-index for tile `k`        
        :param y1: minimum y-index for tile `k`        
        :param y2: maximum y-index for tile `k`        
        
        """        
        if int(self.x_start[k]) != 0:
            x1 = int(self.x_start[k]+self.x_buffer)
        else:
            x1 = self.x_start[k]
        
        if int(self.y_start[k]) != 0:
            y1 = int(self.y_start[k]+self.y_buffer)
        else:
            y1 = self.y_start[k]           
           
        x2 = int(self.x_end[k] - self.x_buffer + 1)      
        y2 = int(self.y_end[k] - self.y_buffer + 1)        
        
        return x1, x2, y1, y2    
        
    
    def getStartCord(self, k):        
        """        
        Return the longitude and latitude values that lie within        
        the modelled domain  
               
        Returns:        
        --------        
        
        :param lon: :class:`numpy.ndarray` containing longitude values                
        :param lat: :class:`numpy.ndarray` containing latitude values        
        
        """ 
        limits = self.getGridLimit(k)
        tile_x_cord = self.x_Left + limits[0] * self.pixelWidth
        tile_y_cord = self.y_Upper + limits[2] * self.pixelHeight               
        
        return tile_x_cord, tile_y_cord

    
    def getTileName(self, k):        
        """        
        Return the longitude and latitude values that lie within        
        the modelled domain  
               
        Returns:        
        --------        
        
        :param lon: :class:`numpy.ndarray` containing longitude values                
        :param lat: :class:`numpy.ndarray` containing latitude values        
        
        """ 
        
        startCord = self.getStartCord(k)
        name = 'e' + str(startCord[0])[:8] + 's' + str(startCord[1])[:7]               
        
        return name
        
    # get the tile extent
    def getTileExtent_buffer(self, k):
        
        tile_x_start = self.x_start[k] * self.pixelWidth + self.x_Left
        tile_y_start = - (self.y_start[k] * self.pixelHeight + self.y_Upper)
        tile_x_end = self.x_end[k] * self.pixelWidth + self.x_Left
        tile_y_end = - (self.y_end[k] * self.pixelHeight + self.y_Upper)

        return tile_x_start, tile_y_start, tile_x_end, tile_y_end


class Multipliers(object):
    
    def __init__(self, tilegrid, sourceimg, dem, cyclone_area):
        self.tilegrid = tilegrid
        self.input_img = sourceimg
        
        self.ds = gdal.Open(self.input_img, GA_ReadOnly)
        if self.ds is None:
            log.info('Could not open ' + self.input_img)
            sys.exit(1)
        
        geotransform = self.ds.GetGeoTransform()
        self.pixelWidth = geotransform[1]
        self.pixelHeight = -geotransform[5]
        
        self.dem = dem
        self.dem_ds = gdal.Open(self.dem, GA_ReadOnly)
        if self.dem_ds is None:
            log.info('Could not open ' + self.dem)
            sys.exit(1)
        
        geotransform_dem = self.dem_ds.GetGeoTransform()
        self.pixelWidth_dem = geotransform_dem[1]
        self.pixelHeight_dem = -geotransform_dem[5]
    
        self.cyclone_area = cyclone_area
        self.cyclone_ds = gdal.Open(self.cyclone_area, GA_ReadOnly)
        if self.cyclone_ds is None:
            log.info('Could not open ' + self.dem)
            sys.exit(1)
            
        geotransform_dem = self.cyclone_ds.GetGeoTransform()
        self.pixelWidth_cycl = geotransform_dem[1]
        self.pixelHeight_cycl = -geotransform_dem[5]
    
    def multipliers_calculate(self, tile_info):
#        import pdb
#        pdb.set_trace()
        
        tile_name = tile_info[0]
        tile_extents = tile_info[1]
        
        # get the tile name without buffer using coordinates with 4 decimals         
        log.info('The working tile is  %s' % tile_name)
        
        # create the temperal tile for terrain class
        temp_tile = pjoin(output_folder, tile_name + '.img')
                                                             
        log.debug('tile_extents = %s', tile_extents)
        
        command_string = 'gdalwarp'
        command_string += ' -t_srs %s -te %f %f %f %f -tr %f %f -tap -tap ' % (
            self.ds.GetProjection(),
            tile_extents[0], tile_extents[3], tile_extents[2], tile_extents[1], 
            self.pixelWidth, self.pixelHeight
            )    
    #        if nodata_value is not None:
    #            command_string += ' -srcnodata %d -dstnodata %d' % (None, None)                                                              
        command_string += ' -of HFA'                 
        command_string += ' -overwrite %s %s' % (
            self.input_img,
            temp_tile
            )
        #print command_string
        
        log.debug('command_string = %s', command_string)        
        result = execute(command_string=command_string)#        
        if result['stdout']:
            log.info(result['stdout'] + 'stdout from %s' % command_string + '\t')         
        if result['returncode']:
            log.error(result['stderr'] + 'stderr from %s' % command_string + '\t')
            raise Exception('%s failed' % command_string) 
        
        # check the maximum value of the terrain map tile, if it greater than 0, go ahead        
        temp_tile_stat = pjoin(output_folder, tile_name + '_stat.img')
        gdal_translate_str = 'gdal_translate -stats %s %s'% (temp_tile, temp_tile_stat)
        execute(gdal_translate_str)
        os.remove(temp_tile)
        
        temp_dataset = gdal.Open(temp_tile_stat) 
        band = temp_dataset.GetRasterBand(1) 
        stats = band.GetStatistics(0,1)
        print stats
        max_value = stats[1]
        
        if max_value > 0:
            # create the temperal tile for DEM
            temp_tile_dem = pjoin(output_folder, tile_name + '_dem.img')
                                                                 
            log.debug('tile_extents = %s', tile_extents)
            
            command_string = 'gdalwarp'
            command_string += ' -t_srs %s -te %f %f %f %f -tr %f %f -tap -tap ' % (
                self.dem_ds.GetProjection(),
                tile_extents[0], tile_extents[3], tile_extents[2], tile_extents[1], 
                self.pixelWidth_dem, self.pixelHeight_dem
                )    
        #        if nodata_value is not None:
        #            command_string += ' -srcnodata %d -dstnodata %d' % (None, None)                                                              
            command_string += ' -of HFA'                 
            command_string += ' -overwrite %s %s' % (
                self.dem,
                temp_tile_dem
                )
            
            #print command_string
            log.debug('command_string = %s', command_string)        
            result = execute(command_string=command_string)#        
            if result['stdout']:
                log.info(result['stdout'] + 'stdout from %s' % command_string + '\t')         
            if result['returncode']:
                log.error(result['stderr'] + 'stderr from %s' % command_string + '\t')
                raise Exception('%s failed' % command_string) 
                       
            
            # create the temperal tile for Cyclone area
            temp_tile_cyclone = pjoin(output_folder, tile_name + '_cycl.img')
                                                                 
            log.debug('tile_extents = %s', tile_extents)
            
            command_string = 'gdalwarp'
            command_string += ' -t_srs %s -te %f %f %f %f -tr %f %f -tap -tap ' % (
                self.cyclone_ds.GetProjection(),
                tile_extents[0], tile_extents[3], tile_extents[2], tile_extents[1], 
                self.pixelWidth_cycl, self.pixelHeight_cycl
                )    
        #        if nodata_value is not None:
        #            command_string += ' -srcnodata %d -dstnodata %d' % (None, None)                                                              
            command_string += ' -of HFA'                 
            command_string += ' -overwrite %s %s' % (
                self.cyclone_area,
                temp_tile_cyclone
                )
            
            #print command_string
            log.debug('command_string = %s', command_string)        
            result = execute(command_string=command_string)#        
            if result['stdout']:
                log.info(result['stdout'] + 'stdout from %s' % command_string + '\t')         
            if result['returncode']:
                log.error(result['stderr'] + 'stderr from %s' % command_string + '\t')
                raise Exception('%s failed' % command_string) 
            
             # check the maximum value of the terrain map tile, if it greater than 0, go ahead        
            cyclone_stat = pjoin(output_folder, tile_name + '_cycl_stat.img')
            gdal_translate_str = 'gdal_translate -stats %s %s'% (temp_tile_cyclone, cyclone_stat)
            execute(gdal_translate_str)
            os.remove(temp_tile_cyclone)
            
            temp_dataset_cycl = gdal.Open(cyclone_stat) 
            band = temp_dataset_cycl.GetRasterBand(1) 
            stats = band.GetStatistics(0,1)
            max_value_cycl = stats[1]            
            
            #resmaple the terrain as DEM
            temp_dataset_DEM = gdal.Open(temp_tile_dem)             
            
            terrain_resample = pjoin(output_folder, tile_name + '_terr_resamp.img')
            driver = gdal.GetDriverByName('HFA')
            terrain_resample_ds = driver.Create(terrain_resample, temp_dataset_DEM.RasterXSize, temp_dataset_DEM.RasterYSize, 1, GDT_Int32)
            terrain_resample_ds.SetGeoTransform(temp_dataset_DEM.GetGeoTransform())
            terrain_resample_ds.SetProjection(temp_dataset_DEM.GetProjection())     
            
            gdal.ReprojectImage(temp_dataset, terrain_resample_ds, temp_dataset.GetProjection(), temp_dataset_DEM.GetProjection(), GRA_Bilinear)            
            
            terrain_resample_ds.GetRasterBand(1).GetStatistics(0,1)
            
            terrain_resample_ds = None
             
            # start to calculate the multipliers 
            log.info('producing Terrain multipliers ...')
            if max_value_cycl > 0:
                cyclone_area = cyclone_stat
            else:
                cyclone_area = None
                
            terrain.terrain.terrain(cyclone_area, terrain_resample)
        
            log.info('producing Shielding multipliers ...')
            shielding.shielding.shield(terrain_resample, temp_tile_dem)
            
            log.info('producing Topographic multipliers ...')
            topographic.topomult.topomult(temp_tile_dem)
            
            os.remove(temp_tile_dem)
            os.remove(temp_tile_stat)
            os.remove(terrain_resample)
            os.remove(cyclone_stat)
        else:   
            os.remove(temp_tile_stat)
        
        
        
    def paralleliseOnTiles(self, tiles, progressCallback=None):        
        """        
        Iterate over tiles to calculate return period hazard levels        
        Parameters:        
        -----------                
        
        :param tileiter: `generator` that yields tuples of tile dimensions.        
        
        """      

        work_tag = 0         
        result_tag = 1        
        if (pp.rank() == 0) and (pp.size() > 1):            
            w = 0            
            for d in range(1, pp.size()):                
                pp.send(tiles[w], destination=d, tag = work_tag)                
                w += 1            
                
            terminated = 0            
            while(terminated < pp.size() - 1):                
                
                result, status = pp.receive(pp.any_source, tag=result_tag,                                              
                                            return_status=True)                
                   
                d = status.source
                
                if w < len(tiles):                    
                    pp.send(tiles[w], destination=d, tag=work_tag)                    
                    w += 1                
                else:                    
                    pp.send(None, destination=d, tag=work_tag)                    
                    terminated += 1                
                    
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
    Generate a list of tuples of the x- and y- limits of a tile   
    
    Parameters:    
    -----------    
    
    :param tilegrid: :class:`TileGrid` instance        
    
    :param tilenums: list of tile numbers (must be sequential)    
    
    Returns:    
    --------        
    
    :param tilelimits: list of tuples of tile imits    
    
    """    
    
    #tilelimits_buffer = [tilegrid.getGridLimit_buffer(t) for t in tilenums]
#    tilename = [tilegrid.getTileName(t) for t in tilenums]
#    tile_extents = [tilegrid.getTileExtent_buffer(t) for t in tilenums]     
#    return tilename, tile_extents
    tile_info = [[tilegrid.getTileName(t), tilegrid.getTileExtent_buffer(t)] for t in tilenums]
    return tile_info
    

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
    
    :param str root: Name of root directory    
    :raises OSError: If the directory tree cannot be created.        
    
    """  
    output = pjoin(root, 'output')
    
    log.info('Output will be stored under %s', output)    
    
    subdirs_1 = ['terrain', 'shielding', 'topographic'] 
    subdirs_2 = ['raster', 'netcdf']               
    
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



def run(callback=None):    
    """    
    Run the hazard calculations.    
    
    This will attempt to run the calculation in parallel by tiling the    
    domain, but also provides a sane fallback mechanism to execute     
    in serial.    
    
    :param configFile: str    
    
    """        
    
    # start timing
    startTime = time.time()
    
#    import pdb
#    pdb.set_trace()
    
    # add subfolders into path
    cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe()))[0]))   
    if cmd_folder not in sys.path:
        sys.path.insert(0, cmd_folder)

    #cmd_subfolder1 = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe()))[0],"terrain")))
    cmd_subfolder1 = pjoin(cmd_folder,"terrain")
    if cmd_subfolder1 not in sys.path:
        sys.path.insert(0, cmd_subfolder1)

    #cmd_subfolder2 = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe()))[0],"shielding")))
    cmd_subfolder2 = pjoin(cmd_folder,"shielding")    
    if cmd_subfolder2 not in sys.path:
        sys.path.insert(0, cmd_subfolder2)        
    
    config = ConfigParser.RawConfigParser()
    config.read(pjoin(cmd_folder, 'terr_shield.cfg'))

    root = config.get('inputValues', 'root')
    upwind_length = float(config.get('inputValues', 'upwind_length'))
    
    logfile = 'terr_shield.log'    
    loglevel = 'INFO'
    verbose = False    
    
    flStartLog(logfile, loglevel, verbose) 
    
    attemptParallel() 
    
    # set input map and output folder
    #terrain_map = pjoin(pjoin(root, 'input'), "lc_terrain_class.img")
    terrain_map = pjoin(pjoin(root, 'input'), "lc_terrain_class.img")
    dem = pjoin(pjoin(root, 'input'), "dems1_whole.img")
    cyclone_area =  pjoin(pjoin(root, 'input'), "cyclone_dem_extent.img")
    
    doOutputDirectoryCreation(root)
    
    global output_folder
    output_folder = pjoin(root, 'output')
    
    log.info("get the tiles")    
    TG = TileGrid(upwind_length, terrain_map)    
    tiles = getTiles(TG)
    
    log.info('the number of tiles is %s' % str(len(tiles)))
#    import pdb
#    pdb.set_trace()
    #def progress(i):    
    #    callback(i, len(tiles))                 
    
    pp.barrier()    
    terrain_shield = Multipliers(TG, terrain_map, dem, cyclone_area)            
                          
    terrain_shield.paralleliseOnTiles(tiles)     
    
    pp.barrier()      
    
    
    log.info("Successfully completed wind multipliers calculation")    
    
    # figure out how long the script took to run
    stopTime = time.time()
    sec = stopTime - startTime
    days = int(sec / 86400)
    sec -= 86400*days
    hrs = int(sec / 3600)
    sec -= 3600*hrs
    mins = int(sec / 60)
    sec -= 60*mins
    log.info('The scipt totally took %3i ' % days + 'days, %2i ' % hrs + 'hours, %2i ' % mins + 'minutes %.2f ' %sec + 'seconds')
    print 'finish successfully at last!'


    


if __name__ == '__main__':
    run()
