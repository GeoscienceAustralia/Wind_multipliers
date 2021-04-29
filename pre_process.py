from utilities.shapefiles import shp_file

import logging
from shapely.geometry import shape, mapping, Polygon, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
import fiona
import itertools
import time
import sys
from rtree import index
from tqdm import tqdm 


logger = logging.getLogger('shapefile converter')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('shapefile_converter.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

settlement = shp_file()
settlement.read('testing/input/SettlementTypes_20210413.shp')
AUTORIZED_SETTELMENTS = ['City', 'Large Town', 'Major CBD', 'Small Town', 'Urban']
for s in settlement.attribute:
    if s['SETTLEMENT'] not in AUTORIZED_SETTELMENTS:
        s['SETTLEMENT'] = None
        
logger.info("number of element before dissolve %i" %(len(settlement.attribute)))

settlement.dissolve('SETTLEMENT')

##Sanity check.
for i_, g_ in enumerate(settlement.geom):
	if not g_.is_valid:
		logger.info("geometry %i isn't valid"%(i_))
		s = g_.buffer(0)
		if s.is_valid:
			logger.info("buffering worked")
			settlement.geom[i_] = s 
		else:
			logger.error("buffering didn't work")

            
logger.info("number of element after dissolve %i" %(len(settlement.attribute)))

for i in range(len(settlement.attribute)):
    print(i, settlement.attribute[i]['SETTLEMENT'])
settlement.save('testing/intermediate/test_disolve2.shp')

domain = shp_file()
domain.read('testing/input/box_sub.shp')   # smaller selections. 
settlement.crop(domain.geom[0])
# settlement.save('intermediate/test_disolve2_crop.shp')

land_use = shp_file()
land_use.read('testing/input/NEXIS_INPUT_MB2016_QLD.shp')
# land_use.read('input/NEXIS_SMALL.shp')
land_use.crop(domain.geom[0])

logger.info("Number of features to join %i"%(len(land_use.geom)))

tic = time.perf_counter()
land_use.spatial_join(settlement, "SETTLEMENT")
toc = time.perf_counter()
logger.info(" Done in %f seconds"%(toc - tic ))

#Mapping values:
from collections import defaultdict

SETTLEMENT_map = defaultdict(lambda:0) # , "Small Town":1, )
SETTLEMENT_map['Major CBD']  = 1
SETTLEMENT_map['City']       = 2
SETTLEMENT_map['Urban']      = 3
SETTLEMENT_map['Large Town'] = 4
SETTLEMENT_map['Small Town'] = 5

Local_use_map = defaultdict(lambda:0) # , "Small Town":1, )
Local_use_map["Parkland"]           = 1
Local_use_map["Primary Production"] = 2
Local_use_map["Education"]          = 4
Local_use_map["Residential"]        = 5
Local_use_map["Water"]              = 6
Local_use_map["Other"]              = 7
Local_use_map["Commercial"]         = 8
Local_use_map["Industrial"]         = 9
Local_use_map["Hospital/Medical"]   = 10
Local_use_map["Transport"]          = 11

for list_ in land_use.attribute:
    list_.update({"CAT":SETTLEMENT_map[list_['SETTLEMENT']] * 100 + Local_use_map[list_['LOCAL_USE']]})

land_use.meta['schema']['properties'].update({'SETTLEMENT':'str:100'})
land_use.meta['schema']['properties'].update({'CAT':'int'})

land_use.save("testing/intermediate/output.shp")

