"""
:mod:`value_lookup` -- dictionaries relevant to terrain & shielding multipliers
"""

MULTIPLIER_TYPE = ['terrain', 'shielding']


TERRAIN_CLASS_DESC = dict([(1, 'City Buildings'),
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


# Mz initial value at 10 m
MZ_INIT = dict([(1, 750),
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


MS_INIT = dict([(1, 90),
                (2, 100),
                (3, 88),
                (4, 85),
                (5, 85),
                (6, 100),
                (7, 100),
                (8, 100),
                (9, 100),
                (10, 100),
                (11, 100),
                (12, 100),
                (13, 100),
                (14, 100),
                (15, 100)])


DIRE_ASPECT = dict([('none', 9),
                    ('n', 1),
                    ('ne', 2),
                    ('e', 3),
                    ('se', 4),
                    ('s', 5),
                    ('sw', 6),
                    ('w', 7),
                    ('nw', 8)])


ALL_NEIGHB = dict([('w', lambda i, jj, rows, cols, lag_width:
                    jj-lag_width),
                   ('e', lambda i, jj, rows, cols, lag_width:
                    cols-jj-1-lag_width),
                   ('n', lambda i, jj, rows, cols, lag_width:
                    i-lag_width),
                   ('s', lambda i, jj, rows, cols, lag_width:
                    rows-i-1-lag_width),
                   ('nw', lambda i, jj, rows, cols, lag_width:
                    min(i, jj)-lag_width),
                   ('ne', lambda i, jj, rows, cols, lag_width:
                    min(i, cols-jj-1)-lag_width),
                   ('sw', lambda i, jj, rows, cols, lag_width:
                    min(rows-i-1, jj)-lag_width),
                   ('se', lambda i, jj, rows, cols, lag_width:
                    min(rows-i-1, cols-jj-1)-lag_width),
                   ])


POINT_R = dict([('w', lambda i, m, lag_width: i),
                ('e', lambda i, m, lag_width: i),
                ('n', lambda i, m, lag_width: i-m-lag_width-1),
                ('s', lambda i, m, lag_width: i+m+lag_width+1),
                ('nw', lambda i, m, lag_width: i-m-lag_width-1),
                ('ne', lambda i, m, lag_width: i-m-lag_width-1),
                ('sw', lambda i, m, lag_width: i+m+lag_width+1),
                ('se', lambda i, m, lag_width: i+m+lag_width+1),
                ])


POINT_C = dict([('w', lambda jj, m, lag_width: jj-m-lag_width-1),
                ('e', lambda jj, m, lag_width: jj+m+lag_width+1),
                ('n', lambda jj, m, lag_width: jj),
                ('s', lambda jj, m, lag_width: jj),
                ('nw', lambda jj, m, lag_width: jj-m-lag_width-1),
                ('ne', lambda jj, m, lag_width: jj+m+lag_width+1),
                ('sw', lambda jj, m, lag_width: jj-m-lag_width-1),
                ('se', lambda jj, m, lag_width: jj+m+lag_width+1),
                ])