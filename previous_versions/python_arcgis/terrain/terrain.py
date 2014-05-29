import sys
import string
import os
import time
import shutil
import terrain_class2mz_orig
import direction_filter
import ConfigParser
import arcpy

"""
.. module:: terrain.py
   :synopsis: Derive the terrain multplier

.. moduleauthor:: Tina Yang <Tina.Yang@ga.gov.au>

"""


def terrain(root, loc_list, cyclone_area, arctoolbox):
    """
    Derives the terrain multplier

    :param root:
    :param loc_list: loc, input raster file format: loc + '_terrain_class.img'
    :param cyclone_area: yes/no
    :param arctoolbox: path to Arc Toolbox

    :outputs: loc + '_mz_orig'
    """

    # start timing
    startTime = time.time()

    directory = root + "\\process\\terrain"
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

    output_folder = root + '\\output\\terrain'    
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

   
    for loc in loc_list:
        print loc
        # the input terrain calssified image 
        terrain = root + '\\input\\' + loc + "_terrain_class_projected.img"

        # produce the original terrain multipler from the input terrain classified image   
        print '\nReclassfy the terrain classes into initial terrain multipliers ...'
        terrain_class2mz_orig.terrain_class2mz_orig(terrain, loc, root, cyclone_area, arctoolbox)

        # convoulution of the original terrain multipler into different directions
        print '\nMoving average for each direction ...'
        direction_filter.terrain_convo(loc, root)

    # if more than 1 tile, mosaic them into one   
    if len(loc_list) > 1:
        
        print '\nmerge several tiles into one ...'
        
        loc_name = loc_list[0][:-1]

        dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']
        for one_dir in dire:
            output_raster = loc_name + '_mz_' + one_dir + '.img'
            input_rasters = []
            for loc in loc_list:
                input_rasters.append(output_folder + '\\' + loc + '_mz_' + one_dir + '.img')
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
##    cyclone_area = config.get('input_values', 'cyclone_area')
##    terrain(root, loc_list, cyclone_area)
