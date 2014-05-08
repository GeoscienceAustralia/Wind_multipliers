multiplier_type = ['terrain', 'shielding']


terrain_class_desc = dict([(1, 'City Buildings'),
                           (2, 'Dense Forest'),
                           (3, 'High Density Metro'),
                           (4, 'Centre of small towns'),
                           (5, 'suburban buildings'),
                           (6, 'Long grass with few trees'),
                           (7, 'Crops'),
                           (8, 'Uncut Grass'),
                           (9, 'Airport runways'),
                           (10, 'Cut grass'),
                           (11, 'Barren/Mining/desert(stones)'),
                           (12, 'Water'),
                           (13, 'Roads'),
                           (14, 'orched/open forest'),
                           (15, 'Mudflats/salt evaporators/sandy beaches')])


# krishna's value roughly 6.5m used before 26/09/2013
#mz_init_non_cycl = dict([(1, 750),
#                         (2, 765),
#                         (3, 778),
#                         (4, 822),
#                         (5, 830),
#                         (6, 883),
#                         (7, 910),
#                         (8, 937),
#                         (9, 937),
#                         (10, 990),
#                         (11, 1000),
#                         (12, 937),
#                         (13, 1000),
#                         (14, 830), 
#                         (15, 1037)])
                         

                         
                         
#Tina's value at 10 m used from 26/09/2013
mz_init_non_cycl = dict([(1, 750),
                         (2, 774),
                         (3, 782),
                         (4, 806),
                         (5, 830),
                         (6, 919),
                         (7, 949),
                         (8, 1000),
                         (9, 1000),
                         (10, 1048),
                         (11, 1063),
                         (12, 1000),
                         (13, 1063),
                         (14, 898),
                         (15, 1084)])


#Krishna's value used at 10 m
mz_init_cycl = dict([(1, 863),
                     (2, 873),
                     (3, 882),
                     (4, 901),
                     (5, 918),
                     (6, 945),
                     (7, 959),
                     (8, 973),
                     (9, 973),
                     (10, 995),
                     (11, 1000),
                     (12, 973),
                     (13, 1000),
                     (14, 940),
                     (15, 1014)])




mz_init_phil = dict([(1, 660),
                     (2, 680),
                     (3, 700),
                     (4, 710),
                     (5, 740),
                     (6, 770),
                     (7, 790),
                     (8, 820),
                     (9, 840),
                     (10, 890),
                     (11, 960),
                     (12, 980),
                     (13, 1020),
                     (14, 1100)])                                       
                         

#define cyclone area
cyclone = dict([((112, 25), 1),
                ((113, 27), 1),
                ((113, 26), 1),
                ((113, 25), 1),
                ((113, 24), 1),
                ((113, 23), 1),
                ((113, 22), 1),
                ((113, 21), 1),
                ((114, 21), 1),
                ((114, 22), 1),
                ((114, 23), 1),
                ((114, 24), 1),
                ((114, 25), 1),
                ((114, 26), 1),
                ((114, 27), 1),
                ((115, 22), 1),
                ((115, 21), 1),
                ((115, 20), 1),
                ((116, 22), 1),
                ((116, 21), 1),
                ((116, 20), 1),
                ((117, 21), 1),
                ((117, 20), 1),
                ((118, 21), 1),
                ((118, 20), 1),
                ((119, 21), 1),
                ((119, 20), 1),
                ((119, 19), 1),
                ((120, 20), 1),
                ((120, 19), 1),
                ((121, 20), 1),
                ((121, 19), 1),
                ((121, 18), 1),
                ((122, 19), 1),
                ((122, 18), 1),
                ((122, 17), 1),
                ((122, 16), 1),
                ((123, 17), 1),
                ((123, 16), 1),
                ((123, 15), 1),
                ((124, 17), 1),
                ((124, 16), 1),
                ((124, 15), 1),
                ((124, 14), 1),
                ((125, 16), 1),
                ((125, 15), 1),
                ((125, 14), 1),
                ((125, 13), 1),
                ((126, 15), 1),
                ((126, 14), 1),
                ((126, 13), 1),
                ((127, 15), 1),
                ((127, 14), 1),
                ((127, 13), 1),
                ((128, 15), 1),
                ((128, 14), 1),
                ((129, 15), 1),
                ((129, 14), 1),
                ((129, 13), 1),
                ((130, 15), 1),
                ((130, 14), 1),
                ((130, 13), 1),
                ((130, 12), 1),
                ((130, 11), 1),
                ((131, 13), 1),
                ((131, 12), 1),
                ((131, 11), 1),
                ((132, 12), 1),
                ((132, 11), 1),
                ((132, 10), 1),
                ((133, 12), 1),
                ((133, 11), 1),
                ((134, 12), 1),
                ((134, 11), 1),
                ((135, 15), 1),
                ((135, 14), 1),
                ((135, 13), 1),
                ((135, 12), 1),
                ((135, 11), 1),
                ((136, 16), 1),
                ((136, 15), 1),
                ((136, 14), 1),
                ((136, 13), 1),
                ((136, 12), 1),
                ((136, 11), 1),
                ((137, 16), 1),
                ((137, 15), 1),
                ((138, 17), 1),
                ((138, 16), 1),
                ((139, 18), 1),
                ((139, 17), 1),
                ((139, 16), 1),
                ((140, 18), 1),
                ((140, 17), 1),
                ((140, 16), 1),
                ((141, 17), 1),
                ((141, 16), 1),
                ((141, 15), 1),
                ((141, 14), 1),
                ((141, 13), 1),
                ((141, 12), 1),
                ((141, 11), 1),
                ((142, 15), 1),
                ((142, 13), 1),
                ((142, 12), 1),
                ((142, 11), 1),
                ((142, 10), 1),
                ((143, 14), 1),
                ((143, 13), 1),
                ((143, 12), 1),
                ((143, 11), 1),
                ((144, 16), 1),
                ((144, 15), 1),
                ((144, 14), 1),
                ((145, 18), 1),
                ((145, 17), 1),
                ((145, 16), 1),
                ((145, 15), 1),
                ((145, 14), 1),
                ((146, 19), 1),
                ((146, 18), 1),
                ((146, 17), 1),
                ((147, 20), 1),
                ((147, 19), 1),
                ((148, 21), 1),
                ((148, 20), 1),
                ((148, 19), 1),
                ((149, 22), 1),
                ((149, 21), 1),
                ((149, 20), 1),
                ((150, 24), 1),
                ((150, 23), 1),
                ((150, 22), 1),
                ((150, 21), 1),
                ((151, 24), 1),
                ((151, 23), 1),
                ((152, 25), 1),
                ((152, 24), 1)])