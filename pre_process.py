from utilities.shapefiles import shp_file

import logging
from shapely.geometry import shape, mapping, Polygon, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
import fiona
import itertools
import time
import sys
from rtree import index
from osgeo import ogr, gdal
import numpy as np

logger = logging.getLogger('shapefile converter')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('shapefile_converter.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


def rasterize(input, output, input_topo, crop_topo):
    """
    Function to rasterize a shapefile

    :param input: name/path of the shapefile
    :type input: str

    :param output: name/path of the tiff file
    :type output: str

    """
    source_ds = ogr.Open(input)
    source_layer = source_ds.GetLayer()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    if input_topo:
        topo_ds = ogr.Open(input_topo)
        nrows = topo_ds.RasterYsize
        ncols = topo_ds.RasterXsize
        geoTransform = topo_ds.GetGeoTransform()
        rows = nrows
        cols = ncols
        geotransfrom_output = geoTransform
        if crop_topo == "True":
            x0, dx0, _, y0, _, dy0 = geoTransform
            x_min = np.floor(np.absolute(x_min - x0) / abs(dx0)) * dx0 + x0
            y_max = np.floor(np.absolute(y_max - y0) / abs(dy0)) * dy0 + y0
            geotransform_output = (x_min, dx0, 0, y_max, 0, dy0)
            cols = int((x_max - x_min) / abs(dx0)) + 1
            rows = int((y_max - y_min) / abs(dy0)) + 1
    else:
        pixelWidth = pixelHeight = 1/3600.0
        cols = int((x_max - x_min) / pixelHeight)
        rows = int((y_max - y_min) / pixelWidth)
        print(cols, rows)
        geotransform_output = (x_min, pixelWidth, 0, y_max, 0, -1*pixelHeight)

    target_ds = gdal.GetDriverByName('GTiff').Create(
        output, cols, rows, 1, gdal.GDT_UInt16
        )
    target_ds.SetGeoTransform(geotransform_output)
    band = target_ds.GetRasterBand(1)
    NoData_value = 0
    band.SetNoDataValue(NoData_value)
    band.FlushCache()
    gdal.RasterizeLayer(target_ds, [1],
                        source_layer, options=["ATTRIBUTE=CAT"])


def pre_process(settlment_file, landuse_file,
                crop_mask_file, output_shapefile):
    """
    Function to do the pre_processing.

    :param settlment_file: name/path of the settlment shape file
    :type settlment_file: str

    :param landuse_file: name/path of the land usage shape file
    :type landuse_file: str

    :param crop_mask_file: name/path of shapefile to crop on (can be None)
    :type crop_mask_file: str

    :param output_shapefile: name/path output shape file
    :type output_shapefile: str

    """

    settlement = shp_file()
    settlement.read(settlment_file)
    AUTORIZED_SETTELMENTS = ['City', 'Large Town', 'Major CBD',
                             'Small Town', 'Urban']
    for s in settlement.attribute:
        if s['SETTLEMENT'] not in AUTORIZED_SETTELMENTS:
            s['SETTLEMENT'] = None

    logger.info("number of element before dissolve %i" % (
                    len(settlement.attribute)))

    settlement.dissolve('SETTLEMENT')

    # Sanity check.
    for i_, g_ in enumerate(settlement.geom):
        if not g_.is_valid:
            logger.info("geometry %i isn't valid" % (i_))
            s = g_.buffer(0)
            if s.is_valid:
                logger.info("buffering worked")
                settlement.geom[i_] = s
            else:
                logger.error("buffering didn't work")

    logger.info("number of element after dissolve %i" % (
                len(settlement.attribute)))

    for i in range(len(settlement.attribute)):
        print(i, settlement.attribute[i]['SETTLEMENT'])

    land_use = shp_file()
    land_use.read(landuse_file)
    # settlement.save('intermediate/test_disolve2_crop.shp')
    if crop_mask_file != "None":
        domain = shp_file()
        domain.read(crop_mask_file)
        settlement.crop(domain.geom[0])
        land_use.crop(domain.geom[0])

    logger.info("Number of features to join %i" % (len(land_use.geom)))

    tic = time.perf_counter()
    land_use.spatial_join(settlement, "SETTLEMENT")
    toc = time.perf_counter()
    logger.info(" Done in %f seconds" % (toc - tic))

    # Mapping values:
    from collections import defaultdict

    SETTLEMENT_map = defaultdict(lambda: 0)
    SETTLEMENT_map['Major CBD'] = 1
    SETTLEMENT_map['City'] = 2
    SETTLEMENT_map['Urban'] = 3
    SETTLEMENT_map['Large Town'] = 4
    SETTLEMENT_map['Small Town'] = 5

    Local_use_map = defaultdict(lambda: 0)
    Local_use_map["Parkland"] = 1
    Local_use_map["Primary Production"] = 2
    Local_use_map["Education"] = 4
    Local_use_map["Residential"] = 5
    Local_use_map["Water"] = 6
    Local_use_map["Other"] = 7
    Local_use_map["Commercial"] = 8
    Local_use_map["Industrial"] = 9
    Local_use_map["Hospital/Medical"] = 10
    Local_use_map["Transport"] = 11

    for list_ in land_use.attribute:
        list_.update({"CAT": SETTLEMENT_map[list_['SETTLEMENT']] * 100 +
                     Local_use_map[list_['LOCAL_USE']]})

    land_use.meta['schema']['properties'].update({'SETTLEMENT': 'str:100'})
    land_use.meta['schema']['properties'].update({'CAT': 'int'})

    land_use.save(output_shapefile)


def cmd_line():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-c', '--config_file', type=str,
                        help='Configuration file name',
                        required=True)
    parser.add_argument('-v', '--verbose',
                        help='Print verbose output to stdout',
                        action='store_true')

    return parser.parse_args()


if __name__ == "__main__":
    args = cmd_line()
    # read config file.
    from utilities.config import configparser as config
    config.set_config_file(args.config_file)
    settlment_file = config.get('Preprocessing', 'settlement_data')
    landuse_file = config.get('Preprocessing', 'land_use_data')
    crop_mask_file = config.get('Preprocessing', 'crop_mask')
    output_shapefile = config.get('Preprocessing', 'output_shapefile')
    output_rasterized = config.get('Preprocessing', 'output_rasterized')
    input_topo = config.get('Preprocessing', 'input_topo')
    if input_topo == "True":
        input_topo = config.get('inputValues', 'dem_data')
        crop_topo = config.get('Preprocessing', 'topo_crop')
    elif "None":
        input_topo = None
        crop_topo = None

    # print(settlment_file, landuse_file)
    pre_process(settlment_file, landuse_file, crop_mask_file, output_shapefile)
    rasterize(output_shapefile, output_rasterized, input_topo, crop_topo)
