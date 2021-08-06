# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# landcoverclassification.py
# Created on: 2021-03-22 10:22:35.00000
#   (generated by ArcGIS/ModelBuilder)
# Usage: landcoverclassification <Field_Name> <Settlement_types> <Dissolve_field> <Input_mesh_block_layer> <Background_category_value> <Raster_Dataset_Name_with_Extension> <Output_folder> <Extent> <Vegetation_raster_dataset> 
# Description: 
# Using categorised mesh blocks and settlement types, create a raster layer that represents the land cover for that location. This overrides vegetation classifications, and is primarily focused on urban areas to improve the terrain types in those areas for calculating local wind multipliers.
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy

# Script arguments
Field_Name = arcpy.GetParameterAsText(0)
if Field_Name == '#' or not Field_Name:
    Field_Name = "CAT" # provide a default value if unspecified

Settlement_types = arcpy.GetParameterAsText(1)
if Settlement_types == '#' or not Settlement_types:
    Settlement_types = "SettlementTypes.shp" # provide a default value if unspecified

Dissolve_field = arcpy.GetParameterAsText(2)
if Dissolve_field == '#' or not Dissolve_field:
    Dissolve_field = "SETTLEMENT_TYPE" # provide a default value if unspecified

Input_mesh_block_layer = arcpy.GetParameterAsText(3)
if Input_mesh_block_layer == '#' or not Input_mesh_block_layer:
    Input_mesh_block_layer = "ClassifiedMeshBlocks.shp" # provide a default value if unspecified

Background_category_value = arcpy.GetParameterAsText(4)
if Background_category_value == '#' or not Background_category_value:
    Background_category_value = "27" # provide a default value if unspecified

Raster_Dataset_Name_with_Extension = arcpy.GetParameterAsText(5)
if Raster_Dataset_Name_with_Extension == '#' or not Raster_Dataset_Name_with_Extension:
    Raster_Dataset_Name_with_Extension = "bnecover" # provide a default value if unspecified

Output_folder = arcpy.GetParameterAsText(6)
if Output_folder == '#' or not Output_folder:
    Output_folder = "X:\\georisk\\HaRIA_B_Wind\\projects\\qfes_swha\\data\\derived\\landcover" # provide a default value if unspecified

Extent = arcpy.GetParameterAsText(7)
if Extent == '#' or not Extent:
    Extent = "150.246044034566 -29.0326887808719 155.30681111763 -25.2613171372321" # provide a default value if unspecified

Vegetation_raster_dataset = arcpy.GetParameterAsText(8)
if Vegetation_raster_dataset == '#' or not Vegetation_raster_dataset:
    Vegetation_raster_dataset = "X:\\georisk\\HaRIA_B_Wind\\projects\\dfes_swha\\data\\original\\landcover\\veg_types" # provide a default value if unspecified

# Local variables:
Sub_selected_settlement_types = "Selected_Settlement_Types"
Dissolved_settlement_polygons = "C:\\Users\\u12161\\Documents\\ArcGIS\\Default.gdb\\settlement_type_dissolve"
Merged_land_class_shape_file = "C:\\Users\\u12161\\Documents\\ArcGIS\\Default.gdb\\MB_LU_class"
Output_Feature_Class__3_ = Merged_land_class_shape_file
Output_Feature_Class__2_ = Output_Feature_Class__3_
Local_use_category = "LOCAL_USE_CAT"
Output_Feature_Class__4_ = Output_Feature_Class__2_
Settlement_category = "SETTLMENT_CAT"
NEXIS_INPUT_MB2016_WA_Spatia__3_ = Output_Feature_Class__4_
NEXIS_INPUT_MB2016_WA_Spatia__4_ = NEXIS_INPUT_MB2016_WA_Spatia__3_
Mesh_block_with_categorised_land_use = NEXIS_INPUT_MB2016_WA_Spatia__4_
Land_use_by_mesh_block_as_raster = "C:\\Users\\u12161\\Documents\\ArcGIS\\Default.gdb\\MB_LU_class_PolygonToRaster"
Output_raster = Land_use_by_mesh_block_as_raster
Background_raster_value = "C:\\Users\\u12161\\Documents\\ArcGIS\\Default.gdb\\CreateConsta1"

# Set Geoprocessing environments
arcpy.env.extent = Input mesh block layer

# Process: Make Feature Layer
tempEnvironment0 = arcpy.env.extent
arcpy.env.extent = Extent
arcpy.MakeFeatureLayer_management(Settlement_types, Sub_selected_settlement_types, "SETTLEMENT_TYPE = 'City' OR SETTLEMENT_TYPE = 'Large Town' OR SETTLEMENT_TYPE = 'Major CBD' OR SETTLEMENT_TYPE = 'Small Town' OR SETTLEMENT_TYPE = 'Urban'", "", "OBJECTID OBJECTID VISIBLE NONE;SHAPE SHAPE VISIBLE NONE;UCL_CODE UCL_CODE VISIBLE NONE;UCL_NAME UCL_NAME VISIBLE NONE;SETTLEMENT_TYPE SETTLEMENT_TYPE VISIBLE NONE;UCL_SRC UCL_SRC VISIBLE NONE;WIND_REGION WIND_REGION VISIBLE NONE;WIND_SRC WIND_SRC VISIBLE NONE;SITE_CLASS SITE_CLASS VISIBLE NONE;SITE_SRC SITE_SRC VISIBLE NONE;STATE STATE VISIBLE NONE;ORIG_FID ORIG_FID VISIBLE NONE;SHAPE_Length SHAPE_Length VISIBLE NONE;SHAPE_Area SHAPE_Area VISIBLE NONE")
arcpy.env.extent = tempEnvironment0

# Process: Dissolve
tempEnvironment0 = arcpy.env.extent
arcpy.env.extent = Extent
arcpy.Dissolve_management(Sub_selected_settlement_types, Dissolved_settlement_polygons, Dissolve_field, "", "SINGLE_PART", "DISSOLVE_LINES")
arcpy.env.extent = tempEnvironment0

# Process: Spatial Join
tempEnvironment0 = arcpy.env.extent
arcpy.env.extent = Extent
arcpy.SpatialJoin_analysis(Input_mesh_block_layer, Dissolved_settlement_polygons, Merged_land_class_shape_file, "JOIN_ONE_TO_ONE", "KEEP_ALL", "MB_CODE \"MB_CODE\" true true false 8 Double 0 0 ,First,#,Y:\\3_BuiltEnvData\\Buildings\\Workspace\\PreProcessing\\NEXIS_Input\\AdministrativeBoundaries\\MeshBlocks\\2018\\Workspace\\ABSMeshblocks_2016_Landuse_Classification.gdb\\NEXIS_INPUT_MB2016_QLD,MB_CODE,-1,-1;LOCAL_USE \"LOCAL_USE\" true true false 200 Text 0 0 ,First,#,Y:\\3_BuiltEnvData\\Buildings\\Workspace\\PreProcessing\\NEXIS_Input\\AdministrativeBoundaries\\MeshBlocks\\2018\\Workspace\\ABSMeshblocks_2016_Landuse_Classification.gdb\\NEXIS_INPUT_MB2016_QLD,LOCAL_USE,-1,-1;NEXIS_USE_I \"NEXIS_USE_I\" true true false 40 Text 0 0 ,First,#,Y:\\3_BuiltEnvData\\Buildings\\Workspace\\PreProcessing\\NEXIS_Input\\AdministrativeBoundaries\\MeshBlocks\\2018\\Workspace\\ABSMeshblocks_2016_Landuse_Classification.gdb\\NEXIS_INPUT_MB2016_QLD,NEXIS_USE_I,-1,-1;NEXIS_USE_II \"NEXIS_USE_II\" true true false 20 Text 0 0 ,First,#,Y:\\3_BuiltEnvData\\Buildings\\Workspace\\PreProcessing\\NEXIS_Input\\AdministrativeBoundaries\\MeshBlocks\\2018\\Workspace\\ABSMeshblocks_2016_Landuse_Classification.gdb\\NEXIS_INPUT_MB2016_QLD,NEXIS_USE_II,-1,-1;USE_SRC \"USE_SRC\" true true false 100 Text 0 0 ,First,#,Y:\\3_BuiltEnvData\\Buildings\\Workspace\\PreProcessing\\NEXIS_Input\\AdministrativeBoundaries\\MeshBlocks\\2018\\Workspace\\ABSMeshblocks_2016_Landuse_Classification.gdb\\NEXIS_INPUT_MB2016_QLD,USE_SRC,-1,-1;SETTLEMENT_TYPE \"SETTLEMENT_TYPE\" true true false 20 Text 0 0 ,First,#,C:\\Users\\u12161\\Documents\\ArcGIS\\Default.gdb\\settlement_type_dissolve,SETTLEMENT_TYPE,-1,-1", "INTERSECT", "", "")
arcpy.env.extent = tempEnvironment0

# Process: Add category field
tempEnvironment0 = arcpy.env.extent
arcpy.env.extent = Extent
arcpy.AddField_management(Merged_land_class_shape_file, Field_Name, "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.env.extent = tempEnvironment0

# Process: Add local use category
tempEnvironment0 = arcpy.env.extent
arcpy.env.extent = Extent
arcpy.AddField_management(Output_Feature_Class__3_, Local_use_category, "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.env.extent = tempEnvironment0

# Process: Add settlement category
tempEnvironment0 = arcpy.env.extent
arcpy.env.extent = Extent
arcpy.AddField_management(Output_Feature_Class__2_, Settlement_category, "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.env.extent = tempEnvironment0

# Process: Classify local use category
tempEnvironment0 = arcpy.env.extent
arcpy.env.extent = Extent
arcpy.CalculateField_management(Output_Feature_Class__4_, "LOCAL_USE_CAT", "classify_local_use( !LOCAL_USE! )", "PYTHON_9.3", "def classify_local_use(category):\\n  use_cat = {\"Parkland\": 1, \"Primary Production\":2, \"Education\":4, \"Residential\":5,\\n           \"Water\":6, \"Other\":7, \"Commercial\":8, \"Industrial\":9, \"Hospital/Medical\":10,\\n           \"Transport\":11}\\n  return use_cat[category]")
arcpy.env.extent = tempEnvironment0

# Process: Classify settlement category
tempEnvironment0 = arcpy.env.extent
arcpy.env.extent = Extent
arcpy.CalculateField_management(NEXIS_INPUT_MB2016_WA_Spatia__3_, "SETTLMENT_CAT", "classify_settlement( !SETTLEMENT_TYPE! )", "PYTHON_9.3", "def classify_settlement(settlement):\\n  settlement_cat = {'Major CBD':1, \"City\":2, \"Urban\":3, \"Large Town\":4, \"Small Town\":5 }\\n  return settlement_cat[settlement]")
arcpy.env.extent = tempEnvironment0

# Process: Calculate Field
tempEnvironment0 = arcpy.env.extent
arcpy.env.extent = Extent
arcpy.CalculateField_management(NEXIS_INPUT_MB2016_WA_Spatia__4_, "CAT", "combine_categories( !LOCAL_USE_CAT! , !SETTLMENT_CAT! )", "PYTHON_9.3", "def combine_categories(lu_cat, s_cat):\\n  usecat = \"{0:d}{1:02d}\".format(s_cat, lu_cat)\\n  return int(usecat)")
arcpy.env.extent = tempEnvironment0

# Process: Polygon to Raster
tempEnvironment0 = arcpy.env.pyramid
arcpy.env.pyramid = "NONE"
tempEnvironment1 = arcpy.env.extent
arcpy.env.extent = Extent
arcpy.PolygonToRaster_conversion(Mesh_block_with_categorised_land_use, "CAT", Land_use_by_mesh_block_as_raster, "CELL_CENTER", "NONE", "0.00027777778")
arcpy.env.pyramid = tempEnvironment0
arcpy.env.extent = tempEnvironment1

# Process: Create Constant Raster
tempEnvironment0 = arcpy.env.extent
arcpy.env.extent = "115.033287963383 -33.0245459994726 116.703669589476 -30.9853479174762"
arcpy.gp.CreateConstantRaster_sa(Background_raster_value, Background_category_value, "INTEGER", Land_use_by_mesh_block_as_raster, Extent)
arcpy.env.extent = tempEnvironment0

# Process: Mosaic To New Raster
tempEnvironment0 = arcpy.env.pyramid
arcpy.env.pyramid = "NONE"
tempEnvironment1 = arcpy.env.extent
arcpy.env.extent = Extent
tempEnvironment2 = arcpy.env.cellSize
arcpy.env.cellSize = Background raster value
arcpy.MosaicToNewRaster_management("C:\\Users\\u12161\\Documents\\ArcGIS\\Default.gdb\\MB_LU_class_PolygonToRaster;X:\\georisk\\HaRIA_B_Wind\\projects\\dfes_swha\\data\\original\\landcover\\veg_types;C:\\Users\\u12161\\Documents\\ArcGIS\\Default.gdb\\CreateConsta1", Output_folder, Raster_Dataset_Name_with_Extension, "", "32_BIT_SIGNED", "", "1", "FIRST", "FIRST")
arcpy.env.pyramid = tempEnvironment0
arcpy.env.extent = tempEnvironment1
arcpy.env.cellSize = tempEnvironment2
