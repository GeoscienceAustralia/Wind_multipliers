"""
:mod:`value_lookup` -- dictionaries relevant to terrain & shielding multipliers
"""

MULTIPLIER_TYPE = ['terrain', 'shielding']


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
