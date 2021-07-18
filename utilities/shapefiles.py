import logging
from shapely.geometry import shape, mapping, Polygon, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
import fiona
import itertools
import time
import sys
from rtree import index
import numpy as np

logger = logging.getLogger()


class shp_file:

    def __init__(self):
        self.meta = None
        self.geom = []
        self.attribute = [] #None

    def read(self, fname):
        with fiona.open(fname) as input:
            self.meta = input.meta
            for i, poly in enumerate(input):
                if poly['geometry'] is None:
                    logger.info("geometry %i is empty of %s"%(i, fname))
                else:
                    self.geom.append(shape(poly['geometry']))
                    self.attribute.append(poly['properties'])

    def save(self, fname):
        with fiona.open(fname, 'w', **self.meta) as output:
            for i in range(len(self.attribute)):
                output.write({'geometry': mapping(self.geom[i]), 'properties': self.attribute[i]})

    def dissolve(self, attribute_name):
        list_z = zip(self.attribute, self.geom)
        e = sorted(list_z, key=lambda k: k[0][attribute_name] or "None")
        tmp_geom        = []
        tmp_attribute   = []
        for key, group in itertools.groupby(e, key=lambda x: x[0][attribute_name] or "None"):
            properties, geom = zip(*[(feature[0], feature[1]) for feature in group])
            tmp_geom.append(unary_union(geom))
            tmp_attribute.append( properties[0] )
        self.geom = tmp_geom
        self.attribute = tmp_attribute


    def crop(self, polygon):
        clip_geom = []
        clip_attribute = []
        bounds = polygon.bounds 
        p1 = Point(bounds[0], bounds[1])
        p2 = Point(bounds[0], bounds[3])
        p3 = Point(bounds[2], bounds[3])
        p4 = Point(bounds[2], bounds[1])
        pointList = [p1, p2, p3, p4, p1]
        polybox = Polygon([[p.x, p.y] for p in pointList])
        for idx, poly in enumerate(self.geom):
            result = polybox.intersection(poly)
            if result.area:
                clip_geom.append(result)
                clip_attribute.append(self.attribute[idx])
        self.geom = clip_geom
        self.attribute = clip_attribute

    def spatial_join(self, other, var):
        # create the index. 
        index_by_id = dict((id(pt), i) for i, pt in enumerate(other.geom))
        # create the spatial tree
        idx_other = STRtree(other.geom)
        # start the merge:
        def process( i ):
            poly = self.geom[i]
        #for i, poly in enumerate(self.geom):
            fids = [index_by_id[id(pt)] for pt in idx_other.query(poly) if poly.intersects(pt)]
            if len(fids) == 0 :
                return None
                #self.attribute[i].update({var:None})
            elif len(fids) == 1 :
                return fids[0]
                #self.attribute[i].update({var:other.attribute[fids[0]][var]})
            else :
                results = np.zeros(len(fids))
                for ii, id_ in enumerate(fids):
                    result = poly.intersection(other.geom[id_])
                    results[ii] = result.area / poly.area
                argmax = np.argmax(results)
                return fids[argmax]
                #self.attribute[i].update({var:other.attribute[fids[argmax]][var]})
        #multi process
        from concurrent.futures import ThreadPoolExecutor
        
        with ThreadPoolExecutor() as executor:
            res = list(executor.map(process, range(len(self.geom))))

        for i in range(len(self.geom)):
            if res[i] is not None:
                self.attribute[i].update({var:other.attribute[ res[i] ][var]})
            else:
                self.attribute[i].update({var:None})
