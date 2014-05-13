# ---------------------------------------------------------------------------
# Purpose: transfer the landsat classied image into original shielding factors
# Input: loc, input raster file format: loc + '_terrain_class.img'
# Output: loc + '_ms_orig'
# Created on 12 08 2011 by Tina Yang
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os, time, shutil
import value_lookup


def terrain_class2ms_orig(terrain, loc, root, ArcToolbox):   
    
    import arcpy
    
    arcpy.CheckOutExtension("spatial")
    arcpy.AddToolbox(ArcToolbox + "/Spatial Analyst Tools.tbx")

    directory = root + "\\process\\shielding"    
##    if os.path.exists(directory):
##        shutil.rmtree(directory)
##    os.makedirs(directory)
    
    # setting data source
    arcpy.env.workspace = directory
    arcpy.env.scratchWorkspace = arcpy.env.workspace

    ms_orig = loc + "_ms_orig"
    
    # set the initial shielding factors
    ms_init = value_lookup.ms_init

    # Reclassify the land classes into initial shielding factors
    remap = "0 100;"
    value_max = int(arcpy.GetRasterProperties_management(terrain, "MAXIMUM").getOutput(0))

    print 'Landsat classified image has ' + str(value_max) + ' classes'


    for i in range(value_max):
        remap += str(i+1) + ' ' + str(ms_init[i+1]) + ';'

    print remap

    if arcpy.Exists('temp1'):
        arcpy.Delete_management('temp1')
    arcpy.gp.Reclassify_sa(terrain, "Value", remap, 'temp1', "NODATA")
    if arcpy.Exists('temp2'):
        arcpy.Delete_management('temp2')
    arcpy.gp.Float_sa('temp1', 'temp2')
    if arcpy.Exists(ms_orig):
        arcpy.Delete_management(ms_orig)
    arcpy.gp.Divide_sa('temp2', '100', ms_orig)

    # delete intermeidiate files
    g_list = arcpy.ListRasters('g_g*')
    for g_file in g_list:
        arcpy.Delete_management(g_file)
    if arcpy.Exists('temp1'):
        arcpy.Delete_management('temp1')
    if arcpy.Exists('temp2'):
        arcpy.Delete_management('temp2')
        

    del arcpy
    del ms_init

    #print 'finish terrain_class2ms_orig'
        


##if __name__ == '__main__':
##    # start timing
##    startTime = time.time()
##
##    # set directory
##    root = 'N:\\climate_change\\Workspaces\\Tina\\Multiplier\\validation'
##                             
##    loc = 'act'
##
##    # setting input file as the Landsat calssified image in ERDAS imagine format,
##    # output as the ms_orig in ESRI Grid format,
##    # it will need convoulution into different directions later by direction_filter.py
##
##    terrain = root + '\\input\\' + loc + "_terrain_class.img"
##    
##    
##    terrain_class2ms_orig(terrain, loc, root)
##
##
##    print 'finish successfully'
##
##    # figure out how long the script took to run
##    stopTime = time.time()
##    sec = stopTime - startTime
##    days = int(sec / 86400)
##    sec -= 86400*days
##    hrs = int(sec / 3600)
##    sec -= 3600*hrs
##    mins = int(sec / 60)
##    sec -= 60*mins
##    print 'The scipt took ', days, 'days, ', hrs, 'hours, ', mins, 'minutes ', '%.2f ' %sec, 'seconds'
##
##
