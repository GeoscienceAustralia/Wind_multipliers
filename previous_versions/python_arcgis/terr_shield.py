# ---------------------------------------------------------------------------
# Purpose: transfer the landsat classied image into shielding multplier
# Input: loc, input raster file format: loc + '_terrain_class.img', dem
# Output: loc + '_ms' in each direction
# Created on 12 08 2011 by Tina Yang
# ---------------------------------------------------------------------------


# Import system & process modules
import sys, string, os, arcpy, time, inspect
import terrain.terrain
import shielding.shielding
import ConfigParser


def main():

    # start timing
    startTime = time.time()

    
    # add subfolders into path
    cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))   
    if cmd_folder not in sys.path:
        sys.path.insert(0, cmd_folder)

    cmd_subfolder1 = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"terrain")))
    if cmd_subfolder1 not in sys.path:
        sys.path.insert(0, cmd_subfolder1)

    cmd_subfolder2 = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"shielding")))
    if cmd_subfolder2 not in sys.path:
        sys.path.insert(0, cmd_subfolder2)
  
    config = ConfigParser.RawConfigParser()
    config.read(cmd_folder + '\\terr_shield.cfg')

    root = config.get('input_values', 'root')
    loc_list = config.get('input_values', 'loc_list').split()
    cyclone_area = config.get('input_values', 'cyclone_area')
    ArcToolbox = config.get('input_values', 'ArcToolbox')

    print '\nproducing Terrain multipliers ...'
    terrain.terrain.terrain(root, loc_list, cyclone_area, ArcToolbox)

    print '\nproducing Shielding multipliers ...'
    shielding.shielding.shield(root, loc_list, ArcToolbox)
    
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


if __name__ == '__main__':
    main()
