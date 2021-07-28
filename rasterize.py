import argparse
from os.path import splitext

from osgeo import gdal

from utilities.shapefiles import shp_file
from pre_process import rasterize

def cmdline():
    """
    Command line arguments
    """
    args = argparse.ArgumentParser(
          description="Rasterize a shapefile on geotiff \
          file with the option to crop it on anther shapefile\
          (containing only one polygone)",
                                   epilog="(c) Sebastien Allgeyer")
    args.add_argument("-i", "--input", metavar="shapefile", 
                      type=str,  help="input shapefile")
    args.add_argument("-a", "--attribute", metavar="attribute", 
                      type=str, default="CAT", help="attribute to rasterise")
    args.add_argument("-t", "--topography", metavar="topo",
                      type=str, help="topography georaster")
    args.add_argument("-c", "--crop", metavar="crop",
                       type=str, help="crop mask (optional)" )
    # args.add_argument("")
    return args.parse_args()


if __name__ == "__main__":
    arg = cmdline()
    print(arg)
    data = shp_file()
    data.read(arg.input)
    if arg.crop:
        # crop_mask = shp_file()
        # crop_mask.read(arg.crop)
        # data.crop(crop_mask.geom[0])
        root, ext = splitext(arg.topography)
        topofile = root + "_crop" + ext
        #crop topography
        write_topo = gdal.Warp(topofile,
                    arg.topography,
                    cutlineDSName=arg.crop,
                    cropToCutline=True,
                    dstNodata = 0)
        write_topo = None 
    else :
        topofile=arg.topography
    rasterize(arg.input, "test.tiff", topofile, True)
    if arg.crop:
        write_topo = gdal.Warp("test_crop.tiff",
                    "test.tiff",
                    cutlineDSName=arg.crop,
                    cropToCutline=True,
                    dstNodata = 0)
        write_topo = None