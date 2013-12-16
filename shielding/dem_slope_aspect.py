# ---------------------------------------------------------------------------
# Purpose: Derive aspect (including reclassified aspect) and slope from DEM
# Input: e.g. act_dem or act_dem.img
# Output: e.g act_slope, act_aspect, and act_apect_r
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os, arcpy, time, shutil

def get_slope_aspect(input_dem, loc, root, ArcToolbox):

    import arcpy

    directory = root + "\\process\\shielding"
    arcpy.env.workspace = directory

    arcpy.env.overwriteOutput = True
    
    arcpy.CheckOutExtension("3D")
    arcpy.CheckOutExtension("spatial")

    # Load required toolboxes...
    arcpy.AddToolbox(ArcToolbox + "/Spatial Analyst Tools.tbx")
    arcpy.AddToolbox(ArcToolbox + "/3D Analyst Tools.tbx")

    dem_slope = loc + '_slope'

    dem_aspect = loc + '_aspect'

    aspect_rec = loc + '_aspect_r'

    # Derive slope...
    arcpy.Slope_3d(input_dem, dem_slope, "PERCENT_RISE", "1")

    # Dervie aspect...
    arcpy.Aspect_3d(input_dem, dem_aspect)

    # Derive reclassifed aspect...
    arcpy.gp.Reclassify_sa(dem_aspect, "Value", "-1 0 9;0 22.5 1;22.5 67.5 2;67.5 112.5 3;112.5 157.5 4;157.5 202.5 5;202.5 247.5 6;247.5 292.5 7;292.5 337.5 8;337.5 360 1", aspect_rec, "NODATA")

    g_list = arcpy.ListRasters('g_g*')
    for g_file in g_list:
        arcpy.Delete_management(g_file)

    del arcpy
    

##if __name__ == '__main__':
##
##    # start timing
##    startTime = time.time()
##
##    # set directory
##    
##    #os.chdir(r'N:\climate_change\workspaces\Tina\Multiplier\bushfire')
##
##    # setting data source, 
##    workspace = 'N:\\climate_change\\Workspaces\\Tina\\Multiplier\\validation'
##    
##    # Script arguments...
##    loc = 'act'
##    input_dem = workspace + '\\input\\' + loc + '_dem'
##
##    get_slope_aspect(input_dem, loc, workspace)
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


