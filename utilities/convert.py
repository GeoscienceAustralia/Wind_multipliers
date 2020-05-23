from functools import reduce
from os import listdir

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
    def __init__(self, tiles):
        self.tiles = tiles
        self.directions = ['e', 'n', 'ne', 'nw', 's', 'se', 'sw', 'w']
        self.types = {'shielding': 'Ms', 'terrain': 'Mz', 'topographic': 'Mt'}
        self.tile_files = []

    def process_tile(self, tile):
        '''Convert NetCDF tiles into GeoTIFF tile

        Each direction NetCDF becomes a band in the GeoTIFF, 
        the pre-multiplied wind multiplier is stored in the band (Ms * Mz * Mt)
        '''

        # Create the raster in-memory to allow manipulating the bands
        driver = gdal.GetDriverByName('MEM')
        out_ds = driver.Create('', 3600, 3600, 1, gdal.GDT_Float32)

        # Add a band for each direction
        for _ in range(1, len(self.directions)):
            out_ds.AddBand(gdal.GDT_Float32)

        band_index = 1

        first = True

        for direction in self.directions:
            bands = []

            # Read the wind multipliers for the current direction
            for folder, unit in self.types.items():
                ds = gdal.Open('/g/data/fj6/multipliers/{0}/{1}_{2}_{3}.nc'.format(folder, tile, unit.lower(), direction))
                bands.append(ma.masked_values(BandReadAsArray(ds.GetRasterBand(1)), -9999))
                if first:
                    transform = ds.GetGeoTransform()
                    first = False

            # Multiply the wind multipliers from NetCDF
            multiplied = reduce(np.multiply, bands)

            # Write the pre-multiplied value to a band
            band = out_ds.GetRasterBand(band_index)
            band.WriteArray(multiplied.data)
            band.SetDescription(direction)
            band.ComputeStatistics(False)
            band.SetNoDataValue(-9999)

            band_index += 1

        # Georeference the raster
        out_ds.SetProjection(PROJECTION)
        out_ds.SetGeoTransform(transform)

        filename = '/g/data/fj6/multipliers/{0}/{1}.nc'.format('M3', tile)
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
