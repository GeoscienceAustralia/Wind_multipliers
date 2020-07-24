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
        self.path = datapath

    def process_tile(self, tile):
        '''Convert NetCDF tiles into GeoTIFF tile

        Each direction NetCDF becomes a band in the GeoTIFF, 
        the pre-multiplied wind multiplier is stored in the band (Ms * Mz * Mt)
        '''

        # Create the raster in-memory to allow manipulating the bands
        driver = gdal.GetDriverByName('MEM')

        # Get/set dimensions for the output bands:
        tmpds = gdal.Open(pjoin(self.path, 'shielding/{0}_ms_n.nc'.format(tile)))
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
                filename = pjoin(self.path, '{0}/{1}_{2}_{3}.nc'.format(folder, tile, unit.lower(), direction))
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
                
                bands.append(ma.masked_values(BandReadAsArray(ds.GetRasterBand(1)), -9999))

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

        filename = pjoin(self.path, '{0}/{1}.tif'.format('M3', tile))
        log.info(f"Saving data to {filename}")
        # Write out a GeoTIFF
        tif = gdal.Translate(filename, out_ds,
                             options=gdal.TranslateOptions(gdal.ParseCommandLine("-co COMPRESS=LZW -co TILED=YES")))
        self.tile_files.append(filename)

        del tif

    def run(self):
        for tile in self.tiles:
            self.process_tile(tile)
        return self.tile_files


if __name__ == '__main__':
    tilelist = {file.split('_')[0] for file in listdir('shielding')}
    converter = Converter(tilelist)
    tile_files = converter.run()

    if len(tile_files) > 0:
        gdal.BuildVRT('wind-multipliers.vrt', tile_files)
