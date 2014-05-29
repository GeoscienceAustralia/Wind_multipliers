import sys, string, os, arcpy, time, shutil
import value_lookup


def combine(loc, root, ArcToolbox):
    """
    To Generate Shielding Multiplier. This tool will be used for each direction to
    derive the shielding multipliers after moving averaging the shielding multiplier using direction_filter.py
    It also will remove the conservatism. 
    input: slope, reclassified aspect, shield origin in one direction
    output: shielding multiplier in the dirction
    """

    import arcpy

    arcpy.env.overwriteOutput = True

    # Check out any necessary licenses
    arcpy.CheckOutExtension("spatial")

    # Load required toolboxes...
    arcpy.AddToolbox(ArcToolbox + "/Spatial Analyst Tools.tbx")
   
    arcpy.env.workspace = root + '\\process\\shielding'
    arcpy.env.scratchWorkspace = arcpy.env.workspace

    output_folder = root + "\\output\\shielding"
    
    slope = loc + '_slope'
    aspect = loc + '_aspect_r'

    dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']

    #dire = ['e', 'ne']

    for one_dir in dire:

        print one_dir
        shield_orig = loc + '_shield_' + one_dir + '.img'
        ms = output_folder + '\\' + loc + '_ms_' + one_dir + '.img'
                             
        combine_each(slope, aspect, shield_orig, ms, one_dir)

        g_list = arcpy.ListRasters('g_g*')
        for g_file in g_list:
            arcpy.Delete_management(g_file)

    arcpy.BuildPyramidsandStatistics_management(output_folder, "#", "BUILD_PYRAMIDS", "CALCULATE_STATISTICS")
    
    del arcpy

    

def combine_each(slope, aspect, shield_orig, ms, one_dir):

    dire_aspect = value_lookup.dire_aspect
    aspect_value = dire_aspect[one_dir]
    
    yes_dire = "Value = " + str(aspect_value)
    not_dire = "Value <> " + str(aspect_value)

    Input_raster_or_constant_value_2 = "0.9"

    # Local variables...
    
    temp = "C:\\temp\\"
    
    if not os.path.exists(temp):
        os.makedirs(temp)   
   
    xasp_n = temp + "xasp_n"
    xslope_n = temp + "xslope_n"
    xslope_n1 = temp + "xslope_n1"
    xshield_n1 = temp + "xshield_n1"
    xslope_n3 = temp + "xslope_n3"
    xshield_n31 = temp + "xshield_n31"
    xslope_temp = temp + "xslope_temp"
    xslope_n2 = temp + "xslope_n2"
    xslope_adjust = temp + "xslope_adjust"
    xasp_o = temp + "xasp_o"
    xshield_o = temp + "xshield_o"
    xshield_merge = temp + "xshield_merge"
    xshield_con1 = temp + "xshield_con1"
    xshield_con2 = temp + "xshield_con2"
    xshield_1 = temp + "xshield_1"
    xshield_2 = temp + "xshield_2"

##    import pdb
##    pdb.set_trace()
    
    # Deal with aspect that is the same as the wind direction
    arcpy.gp.ExtractByAttributes_sa(aspect, yes_dire, xasp_n)    
    arcpy.gp.Con_sa(xasp_n, slope, xslope_n, "", "")

    # select pixel with slope value > 1.8
    arcpy.gp.ExtractByAttributes_sa(xslope_n, "value > 1.8", xslope_n3)    
    arcpy.gp.Reclassify_sa(xslope_n3, "Value", "1 1000 1", xshield_n31, "DATA")

    # select pixel with slope value <= 5.71
    arcpy.gp.ExtractByAttributes_sa(xslope_n, "value <= 5.71", xslope_n1)
    arcpy.gp.Con_sa(xslope_n1, shield_orig, xshield_n1, "", "")

    # select pixel with slope value > 5.71 and value <= 21.8
    arcpy.gp.ExtractByAttributes_sa(xslope_n, "value > 5.71", xslope_temp)
    arcpy.gp.ExtractByAttributes_sa(xslope_temp, "value <= 21.8", xslope_n2)
    # interpolation 
    expr = "((1 - " + shield_orig + ") * (" + xslope_n2 + " - 5.71) / (21.8 - 5.71)) + " + shield_orig
    arcpy.gp.SingleOutputMapAlgebra_sa(expr, xslope_adjust)

    # Deal with aspect that is not the same as the wind direction
    arcpy.gp.ExtractByAttributes_sa(aspect, not_dire, xasp_o)
    arcpy.gp.Con_sa(xasp_o, shield_orig, xshield_o, "", "")
    
    # merge above outputs to get a merged shield
    expr2 = "merge(" + xshield_o + "," + xshield_n1 + "," + xslope_adjust + "," + xshield_n31 + ")"
    arcpy.gp.SingleOutputMapAlgebra_sa(expr2, xshield_merge)

    # Remove convertism, if value >= 0.9, times itself, if value < 0.9, times 0.9
    arcpy.gp.ExtractByAttributes_sa(xshield_merge, "value >= 0.9", xshield_con1)
    arcpy.gp.Square_sa(xshield_con1, xshield_1)
    arcpy.gp.ExtractByAttributes_sa(xshield_merge, "value < 0.9", xshield_con2)
    arcpy.gp.Times_sa(xshield_con2, Input_raster_or_constant_value_2, xshield_2)

    # merge the two into one
    expr3 = "merge(" + xshield_1 + "," + xshield_2 + ")"
    if arcpy.Exists(ms):
        arcpy.Delete_management(ms)        
    arcpy.gp.SingleOutputMapAlgebra_sa(expr3, ms)


                            

##if __name__ == '__main__':
##    # start timing
##    startTime = time.time()
##
##    # set directory
##    workspace = r'N:\climate_change\Workspaces\Tina\Multiplier\validation'
##                             
##    loc = 'act'
##   
##                             
##    combine(loc, workspace)
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

