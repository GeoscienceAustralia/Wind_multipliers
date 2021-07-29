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
    print("args ", input, output, input_topo, crop_topo)
    source_ds = ogr.Open(input)
    source_layer = source_ds.GetLayer()
    
    topo_ds = gdal.Open(input_topo)
    wkt = topo_ds.GetProjection()
    nrows = topo_ds.RasterYSize
    ncols = topo_ds.RasterXSize
    geoTransform = topo_ds.GetGeoTransform()
    rows = nrows
    cols = ncols
    geotransform_output = geoTransform

    logger.info("Output file: %s" %(output) )
    logger.info("Output TRANSFORM %f %f %f %f" %(geotransform_output[0], geotransform_output[3], geotransform_output[2], geotransform_output[5]) )

    target_ds = gdal.GetDriverByName('GTiff').Create(
        output, cols, rows, 1, gdal.GDT_UInt16
        )
    target_ds.SetProjection(wkt)
    target_ds.SetGeoTransform(geotransform_output)
    band = target_ds.GetRasterBand(1)
    NoData_value = 0
    band.SetNoDataValue(NoData_value)
    band.FlushCache()
    gdal.RasterizeLayer(target_ds, [1],
                        source_layer, options=["ATTRIBUTE=CAT"])


def pre_process(settlment_file, settlment_cat, landuse_file, landuse_cat,
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
    logger.info("Reading settlement shapefile %s"%(settlment_file))
    settlement = shp_file()
    settlement.read(settlment_file)
    
    logger.info("Reading landuse shapefile %s"%(landuse_file))
    land_use = shp_file()
    land_use.read(landuse_file)

    AUTORIZED_SETTELMENTS = ['City', 'Large Town', 'Major CBD',
                             'Small Town', 'Urban']
    for s in settlement.attribute:
        if s[settlment_cat] not in AUTORIZED_SETTELMENTS:
            s[settlment_cat] = None

    logger.info("number of element before dissolve %i" % (
                    len(settlement.attribute)))

    settlement.dissolve(settlment_cat)

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
        print(i, settlement.attribute[i][settlment_cat])


    # settlement.save('intermediate/test_disolve2_crop.shp')
    if crop_mask_file != "None":
        domain = shp_file()
        domain.read(crop_mask_file)
        settlement.crop(domain.geom[0])
        land_use.crop(domain.geom[0])

    logger.info("Number of features to join %i" % (len(land_use.geom)))

    tic = time.perf_counter()
    land_use.spatial_join(settlement, settlment_cat)
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
        list_.update({"CAT": SETTLEMENT_map[list_[settlment_cat]] * 100 +
                     Local_use_map[list_[landuse_cat]]})

    land_use.meta['schema']['properties'].update({settlment_cat: 'str:100'})
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
    settlment_cat = config.get('Preprocessing', 'settlement_cat')

    landuse_file = config.get('Preprocessing', 'land_use_data')
    landuse_cat = config.get('Preprocessing', 'land_use_cat')

    crop_mask_file = config.get('Preprocessing', 'crop_mask')
    output_shapefile = config.get('Preprocessing', 'output_shapefile')
    output_rasterized = config.get('Preprocessing', 'output_rasterized')
    input_topo = config.get('Preprocessing', 'input_topo')
    if input_topo == "True":
        input_topo = config.get('inputValues', 'dem_data')
    crop_topo = None

    # print(settlment_file, landuse_file)
    pre_process(settlment_file, settlment_cat, landuse_file,  landuse_cat, crop_mask_file, output_shapefile)
    rasterize(output_shapefile, output_rasterized, input_topo, crop_topo)
