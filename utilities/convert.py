from functools import reduce
from os import listdir
from os.path import join as pjoin
import logging as log
from osgeo import gdal, osr
from osgeo.gdal_array import BandReadAsArray
import numpy as np
import numpy.ma as ma


gdal.UseExceptions()
gdal.SetConfigOption('GDAL_PAM_ENABLED', 'NO')

SRS = osr.SpatialReference()
SRS.ImportFromEPSG(4326)
PROJECTION = SRS.ExportToWkt()


class Converter:
    def __init__(self, tiles, datapath):
        self.tiles = tiles
        self.directions = ['e', 'n', 'ne', 'nw', 's', 'se', 'sw', 'w']
        self.types = {'shielding': 'Ms', 'terrain': 'Mz', 'topographic': 'Mt'}
        self.tile_files = []
        self.max_tile_files = []
        self.path = datapath
        self.missing_value = -9999

    def process_max_tile(self, tile):
        """
        Calculate maximum of all directions for a tile

        """

        driver = gdal.GetDriverByName('MEM')
        # Get dimensions of tile:
        inds = gdal.Open(pjoin(self.path, f"M3/{tile}.tif"))
        transform = inds.GetGeoTransform()
        nx = inds.RasterXSize
        ny = inds.RasterYSize
        bands = []
        band_index = 1
        for direction in self.directions:
            bands.append(ma.masked_values(
                    BandReadAsArray(inds.GetRasterBand(band_index)),
                    self.missing_value))
            band_index += 1

        maxima = np.max(np.dstack(bands), axis=2)
        # Create output dataset - single band required (maximum only)
        out_ds = driver.Create('', nx, ny, 1, gdal.GDT_Float32)
        out_ds.AddBand(gdal.GDT_Float32)
        band = out_ds.GetRasterBand(1)
        band.WriteArray(maxima.data)
        band.SetDescription("Maximum of all directions")
        band.ComputeStatistics(False)
        band.SetNoDataValue(-9999)

        out_ds.SetProjection(PROJECTION)
        out_ds.SetGeoTransform(transform)

        filename = pjoin(self.path, f"M3_max/{tile}.tif")
        log.info(f"Saving data to {filename}")
        # Write out a GeoTIFF
        tif = gdal.Translate(filename, out_ds,
                             options=gdal.TranslateOptions(
                                 gdal.ParseCommandLine(
                                     "-co COMPRESS=LZW -co TILED=YES")))
        self.max_tile_files.append(filename)

        del tif

    def process_tile(self, tile):
        '''Convert NetCDF tiles into GeoTIFF tile

        Each direction NetCDF becomes a band in the GeoTIFF, 
        the pre-multiplied wind multiplier is stored in the band (Ms * Mz * Mt)
        '''

        # Create the raster in-memory to allow manipulating the bands
        driver = gdal.GetDriverByName('MEM')

        # Get/set dimensions for the output bands:
        tmpds = gdal.Open(pjoin(self.path, f"shielding/{tile}_ms_n.nc"))
        nx = tmpds.RasterXSize
        ny = tmpds.RasterYSize

        out_ds = driver.Create('', nx, ny, 1, gdal.GDT_Float32)

        del tmpds

        # Add a band for each direction
        for _ in range(1, len(self.directions)):
            out_ds.AddBand(gdal.GDT_Float32)

        band_index = 1

        first = True

        for direction in self.directions:
            bands = []

            # Read the wind multipliers for the current direction
            for folder, unit in self.types.items():
                filename = pjoin(self.path, f"{folder}/{tile}_{unit.lower()}_{direction}.nc")
                log.info(f"Opening {filename}")
                try:
                    ds = gdal.Open(filename)
                except RuntimeError:
                    log.error(f"Cannot open {filename}")
                    log.error("Replacing all data with ones")
                    ds = driver.Create('', nx, ny, 1, gdal.GDT_Float32)
                    ds.SetGeoTransform(transform)
                    band = ds.GetRasterBand(1)
                    band.WriteArray(np.ones((nx, ny)))
                
                bands.append(ma.masked_values(BandReadAsArray(ds.GetRasterBand(1)),
                                              self.missing_value))

                if first:
                    transform = ds.GetGeoTransform()
                    first = False

            # Multiply the wind multipliers from NetCDF
            multiplied = reduce(np.multiply, bands)

            # Write the pre-multiplied value to a band
            band = out_ds.GetRasterBand(band_index)
            try:
                band.WriteArray(multiplied.data)
            except ValueError:
                log.error("Mismatch between output file and data array")
                log.error(multiplied.data.shape)
            band.SetDescription(direction)
            band.ComputeStatistics(False)
            band.SetNoDataValue(-9999)

            band_index += 1

        # Georeference the raster
        out_ds.SetProjection(PROJECTION)
        out_ds.SetGeoTransform(transform)

        filename = pjoin(self.path, f"M3/{tile}.tif")
        log.info(f"Saving data to {filename}")
        # Write out a GeoTIFF
        tif = gdal.Translate(filename, out_ds,
                             options=gdal.TranslateOptions(gdal.ParseCommandLine("-co COMPRESS=LZW -co TILED=YES")))
        self.tile_files.append(filename)

        del tif

    def run(self):
        for tile in self.tiles:
            self.process_tile(tile)
            self.process_max_tile(tile)
        return self.tile_files


if __name__ == '__main__':
    tilelist = {file.split('_')[0] for file in listdir('shielding')}
    converter = Converter(tilelist)
    tile_files = converter.run()

    if len(tile_files) > 0:
        gdal.BuildVRT('wind-multipliers.vrt', tile_files)
