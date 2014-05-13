# ---------------------------------------------------------------------------
# Purpose: transfer the landsat classied image into shielding multplier
# Input: loc, input raster file format: loc + '_terrain_class.img', dem
# Output: loc + '_ms' in each direction
# Created on 12 08 2011 by Tina Yang
# ---------------------------------------------------------------------------



    
# Import system & process modules
import sys, string, os, arcpy, time, shutil
import terrain_class2ms_orig
import direction_filter
import dem_slope_aspect
import combine
import ConfigParser


def shield(root, loc_list, ArcToolbox):
    
    # start timing
    startTime = time.time()

    directory = root + "\\process\\shielding"    
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

    output_folder = root + "\\output\\shielding"    
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    for loc in loc_list:
        print loc

        # setting input file as the Landsat calssified image in ERDAS imagine format,
        # output as the ms_orig in ESRI Grid format,
        # it will need convoulution into different directions later by direction_filter.py

        terrain = root + '\\input\\' + loc + "_terrain_class.img"
        input_dem = root + '\\input\\' + loc + '_dem'
        #input_dem = root + '\\input\\' + loc_dem
      

        print '\nDerive slope and reclassified aspect ...   '
        dem_slope_aspect.get_slope_aspect(input_dem, loc, root, ArcToolbox)
        
        print '\nReclassfy the terrain classed into inital shielding factors ...'
        terrain_class2ms_orig.terrain_class2ms_orig(terrain, loc, root, ArcToolbox)

        print '\nMoving average for each direction ...'
        direction_filter.shielding_convo(loc, root)

        print '\nCombine the slope and aspect with each direction ...'
        combine.combine(loc, root, ArcToolbox)

    # if more than 1 tile, mosaic them into one   
    if len(loc_list) > 1:

        print '\nmerge several tiles into one ...'
        
        loc_name = loc_list[0][:-1]

        dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']
        for one_dir in dire:
            output_raster = loc_name + '_ms_' + one_dir + '.img'
            input_rasters = []
            for loc in loc_list:
                input_rasters.append(output_folder + '\\' + loc + '_ms_' + one_dir + '.img')
            arcpy.MosaicToNewRaster_management(input_rasters, output_folder, output_raster, "", "32_BIT_FLOAT","", "1", "LAST","FIRST")

    print '\nfinish successfully'

    # figure out how long the script took to run
    stopTime = time.time()
    sec = stopTime - startTime
    days = int(sec / 86400)
    sec -= 86400*days
    hrs = int(sec / 3600)
    sec -= 3600*hrs
    mins = int(sec / 60)
    sec -= 60*mins
    print 'The scipt took ', days, 'days, ', hrs, 'hours, ', mins, 'minutes ', '%.2f ' %sec, 'seconds'


##if __name__ == '__main__':
##    config = ConfigParser.RawConfigParser()
##    config.read('terr_shield.cfg')
##
##    root = config.get('input_values', 'root')
##    loc_list = config.get('input_values', 'loc_list').split()
##    shield(root, loc_list)
