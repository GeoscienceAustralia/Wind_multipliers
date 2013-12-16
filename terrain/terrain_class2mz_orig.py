import sys, string, os, time, shutil
import value_lookup


def terrain_class2mz_orig(terrain, loc, root, cyclone_area, ArcToolbox):
    """
    Purpose: transfer the landsat classied image into original terrain multplier
    Input: loc, input raster file format: loc + '_terrain_class.img', cyclone_area -yes or -no
    Output: loc + '_mz_orig'
    """

    import arcpy
    
    directory = root + "\\process\\terrain"
    
    #if os.path.exists(directory):
    #    shutil.rmtree(directory)
    #os.makedirs(directory)
   
    
    # Create the Geoprocessor object
    arcpy.env.workspace = directory
    
    # Check out any necessary licenses
    arcpy.CheckOutExtension("spatial")

    # Load required toolboxes...
    arcpy.AddToolbox(ArcToolbox + "/Spatial Analyst Tools.tbx")

    if cyclone_area == 'no':
        mz_init = value_lookup.mz_init_non_cycl
    if cyclone_area == 'yes':
        mz_init = value_lookup.mz_init_cycl
      
    # output as the mz_orig in ESRI Grid format, it will need convoulution into different directions in ERDAS imagine
    mz_orig = loc + "_mz_orig"

    
    # Reclassify the land classes into initial shielding multipliers
    remap = "0 1000;"
    value_max = int(arcpy.GetRasterProperties_management(terrain, "MAXIMUM").getOutput(0))

    print 'Landsat classified image has ' + str(value_max) + ' classes'

    if value_max <= 15:
        for i in range(value_max):
            remap += str(i+1) + ' ' + str(mz_init[i+1]) + ';'
    #    remap += str(value_max) + ' ' + str(mz_init[value_max])
    else:
        for i in range(15):
            remap += str(i+1) + ' ' + str(mz_init[i+1]) + ';'    
        for i in range(15, value_max):
            remap += str(i+1) + ' ' + str(1000) + ';'
    #    remap += str(value_max) + ' ' + str(1000)

    print remap

    if arcpy.Exists('temp1'):
        arcpy.Delete_management('temp1')
    arcpy.gp.Reclassify_sa(terrain, "Value", remap, "temp1", "NODATA")
    if arcpy.Exists('temp2'):
        arcpy.Delete_management('temp2')
    arcpy.gp.Float_sa('temp1', 'temp2')
    if arcpy.Exists(mz_orig):
        arcpy.Delete_management(mz_orig)
    arcpy.gp.Divide_sa('temp2', '1000.0', mz_orig)

    # delete intermeidiate files
    g_list = arcpy.ListRasters('g_g*')
    for g_file in g_list:
        arcpy.Delete_management(g_file)
    if arcpy.Exists('temp1'):
        arcpy.Delete_management('temp1')
    if arcpy.Exists('temp2'):
        arcpy.Delete_management('temp2')

    del mz_init
    del arcpy

    
##if __name__ == '__main__':
##
##    startTime = time.clock()
##
##    # setting data source, 
##    root = "N:\\climate_change\\Workspaces\\Tina\\Multiplier\\validation" 
##    loc = 'act'
##    cyclone_area = 'no'
##    # setting input file as the Landsat calssified image in ERDAS imagine format,
##    terrain = root + '\\input\\' + loc + "_terrain_class.img"
##
##    terrain_class2mz_orig(terrain, loc, root, cyclone_area)    
##    
##    print 'finish successfully'
##    stopTime = time.clock()
##    sec = stopTime - startTime
##    days = int(sec / 86400)
##    sec -= 86400*days
##    hrs = int(sec / 3600)
##    sec -= 3600*hrs
##    mins = int(sec / 60)
##    sec -= 60*mins
##    print days, 'days, ', hrs, 'hours, ', mins, 'minutes ', sec, 'seconds'

