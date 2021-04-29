import ogr
import gdal

source_ds = ogr.Open("output/res_full_c2.shp")
source_layer = source_ds.GetLayer()
pixelWidth = pixelHeight = 1/3600.0 
x_min, x_max, y_min, y_max = source_layer.GetExtent()
cols = int((x_max - x_min) / pixelHeight)
rows = int((y_max - y_min) / pixelWidth)
target_ds = gdal.GetDriverByName('GTiff').Create('temp.tif', cols, rows, 1, gdal.GDT_UInt16) 
target_ds.SetGeoTransform((x_min, pixelWidth, 0, y_min, 0, pixelHeight))
band = target_ds.GetRasterBand(1)
NoData_value = 0
band.SetNoDataValue(NoData_value)
band.FlushCache()
gdal.RasterizeLayer(target_ds, [1], source_layer, options = ["ATTRIBUTE=CAT"])
# target_ds = None #this is the line that makes the difference
# gdal.Open('temp.tif').ReadAsArray()