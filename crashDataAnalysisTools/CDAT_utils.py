import numpy as np
import os
import pandas as pd
import sqlite3 as dbi

import matplotlib.pyplot as plt


def set_directory():
    os.chdir('../data/')

def get_annual_data(year, conn):
    '''
    This function combines four datasets to get yearly crash totals for each
    road segment. The inputs are as four csv files saved in the current
    working directory that contain road inventory data, elevation/grade data,
    crash count data, and roadway horizontal alignment (curve) data.

    The function creates a database which contains four tables, one for each
    of the aforementioned csv files. The tables are then merged via a sql
    query.

    The input of the function include four string variables denote the file
    names (including file paths if needed) with the '.csv' suffix of the four
    data tables. The output of the function will be the merged table in the
    form of a pandas dataframe.
    '''

    # read the data tables from .csv files
    set_directory()
    
    road = pd.read_csv('wa'+year+'road.csv')
    acc = pd.read_csv('wa'+year+'acc.csv')
    curv = pd.read_csv('wa'+year+'curv.csv')
    grad = pd.read_csv('wa'+year+'grad.csv')
    elev = pd.read_csv('wa_elev.csv')

    # create a connection to the crash database in the current work directory
    # the database will be created if it does not exist
    
    # create a database cursor that can execute query statements
    cu = conn.cursor()

    # drop tables in the database if needed
    cu.execute('DROP TABLE IF EXISTS road')
    cu.execute('DROP TABLE IF EXISTS acc')
    cu.execute('DROP TABLE IF EXISTS curv')
    cu.execute('DROP TABLE IF EXISTS grad')
    cu.execute('DROP TABLE IF EXISTS elev')

    # convert the pandas dataframes into database tables through the connection
    road.to_sql(name='road', con=conn)
    acc.to_sql(name='acc', con=conn)
    curv.to_sql(name='curv', con=conn)
    grad.to_sql(name='grad', con=conn)
    elev.to_sql(name='elev', con=conn)

    qry_compute_signed_grade = '''
        UPDATE grad
        SET pct_grad =
            CASE WHEN dir_grad='-' THEN -1*pct_grad
            ELSE pct_grad
        END
        '''

    cu.execute(qry_compute_signed_grade)

    # This is the sql query statement that will match elevation data with the
    # corresponding road segments through milepost information. Aggregation
    # statistics (e.g., average, maximum and minimum) about grade will be added
    # as extra columns in the roads table.

    qry_merge_elev = '''
    CREATE VIEW merge_elev AS
    SELECT road.*,
           AVG(elev.Longitude) AS longitude,
           AVG(elev.Latitude) AS latitude,
           AVG(elev.Grade) AS avg_grad,
           MAX(elev.Grade) AS max_grad,
           MIN(elev.Grade) AS min_grad
    FROM road LEFT JOIN elev
    ON road.road_inv = elev.Route_id AND
       elev.milepost BETWEEN road.begmp AND road.endmp
    GROUP BY road.road_inv, road.begmp, road.endmp
    '''

    qry_merge_grad = '''
    CREATE VIEW merge_grad AS
    SELECT lshl_typ, med_type, rshl_typ, surf_typ,
           road_inv, spd_limt, e.begmp AS begmp, endmp, lanewid, no_lanes, 
           lshldwid, rshldwid, medwid, seg_lng, aadt, longitude, latitude,
           CASE WHEN avg_grad IS NOT NULL THEN avg_grad
           ELSE AVG(pct_grad) END AS avg_grad,
           CASE WHEN max_grad IS NOT NULL THEN max_grad
           ELSE MAX(pct_grad) END AS max_grad,
           CASE WHEN min_grad IS NOT NULL THEN min_grad
           ELSE MIN(pct_grad) END AS min_grad
    FROM merge_elev AS e LEFT JOIN grad
    ON e.road_inv = grad.grad_inv AND
       grad.begmp BETWEEN e.begmp AND e.endmp
    GROUP BY e.road_inv, e.begmp, e.endmp
    '''

    qry_merge_curv = '''
    CREATE VIEW merge_curv AS
    SELECT g.*,
           COUNT(curv.dir_curv) AS curv_count,
           MAX(curv.deg_curv) AS max_deg_curv
    FROM merge_grad AS g LEFT JOIN curv
    ON curv.curv_inv = g.road_inv AND
       curv.begmp BETWEEN g.begmp AND g.endmp
    GROUP BY g.road_inv, g.begmp, g.endmp
    '''

    qry_merge_acc = '''
    SELECT c.*,
           COUNT(acc.caseno) AS acc_count
    FROM merge_curv AS c LEFT JOIN acc
    ON c.road_inv = acc.rd_inv AND
       acc.milepost BETWEEN c.begmp AND c.endmp
    GROUP BY c.road_inv, c.begmp, c.endmp
    ORDER BY c.road_inv, c.begmp, c.endmp
    '''

    cu.execute("DROP VIEW IF EXISTS merge_elev")
    cu.execute("DROP VIEW IF EXISTS merge_grad")
    cu.execute("DROP VIEW IF EXISTS merge_curv")
    
    cu.execute(qry_merge_elev)
    cu.execute(qry_merge_grad)
    cu.execute(qry_merge_curv)
    
    annual_data = pd.read_sql(qry_merge_acc, con=conn)
    
    conn.commit()
    
    return annual_data

def merge_annual_data(conn):
    
    table_list = pd.read_sql('''
                             SELECT name FROM sqlite_master
                             WHERE type = "table"
                             ''',
                             con=conn)
    
    if not any(table_list.name == 'data_06'):
        data_06 = get_annual_data('06',conn)
        data_06.to_sql(name='data_06', con=conn)

    if not any(table_list.name == 'data_07'):
        data_07 = get_annual_data('07',conn)
        data_07.to_sql(name='data_07', con=conn)
    
    if not any(table_list.name == 'data_08'):
        data_08 = get_annual_data('08',conn)
        data_08.to_sql(name='data_08', con=conn)

    if not any(table_list.name == 'data_09'):
        data_09 = get_annual_data('09',conn)
        data_09.to_sql(name='data_09', con=conn)
    
    if not any(table_list.name == 'data_10'):
        data_10 = get_annual_data('10',conn)
        data_10.to_sql(name='data_10', con=conn)
    
    if not any(table_list.name == 'data_11'):
        data_11 = get_annual_data('11',conn)
        data_11.to_sql(name='data_11', con=conn)
    
    qry_merge_data = '''
    CREATE VIEW merge_data AS
    SELECT d.*,
           data_11.aadt AS aadt_11, data_11.acc_count AS acc_ct_11
    FROM (
    
    SELECT c.*,
           data_10.aadt AS aadt_10, data_10.acc_count AS acc_ct_10
    FROM (
    
    SELECT b.*,
           data_09.aadt AS aadt_09, data_09.acc_count AS acc_ct_09
    FROM (
    
    SELECT a.*,
           data_08.aadt AS aadt_08, data_08.acc_count AS acc_ct_08
    FROM (
    
    SELECT data_06.*,
           data_06.aadt AS aadt_06, data_06.acc_count AS acc_ct_06,
           data_07.aadt AS aadt_07, data_07.acc_count AS acc_ct_07
    FROM data_06
    
    LEFT JOIN data_07
    ON data_06.road_inv = data_07.road_inv AND
       data_06.begmp = data_07.begmp AND
       data_06.endmp = data_07.endmp
    ) AS a
    
    LEFT JOIN data_08
    ON a.road_inv = data_08.road_inv AND
       a.begmp = data_08.begmp AND
       a.endmp = data_08.endmp
    ) AS b
    
    LEFT JOIN data_09
    ON b.road_inv = data_09.road_inv AND
       b.begmp = data_09.begmp AND
       b.endmp = data_09.endmp
    ) AS c
    
    LEFT JOIN data_10
    ON c.road_inv = data_10.road_inv AND
       c.begmp = data_10.begmp AND
       c.endmp = data_10.endmp
    ) AS d
    
    LEFT JOIN data_11
    ON d.road_inv = data_11.road_inv AND
       d.begmp = data_11.begmp AND
       d.endmp = data_11.endmp
    '''
    
    qry_final_data = '''
    CREATE TABLE crash_data AS
    SELECT lshl_typ, med_type, rshl_typ, surf_typ, road_inv,
           spd_limt, begmp, endmp, lanewid, no_lanes, lshldwid,
           rshldwid, medwid, seg_lng, longitude, latitude,
           avg_grad, max_grad, min_grad, curv_count, max_deg_curv,
           aadt_06, acc_ct_06, aadt_07, acc_ct_07, aadt_08, acc_ct_08,
           aadt_09, acc_ct_09, aadt_10, acc_ct_10, aadt_11, acc_ct_11,
           (aadt_06+aadt_07+aadt_08+aadt_09+aadt_10+aadt_11)/6 AS avg_aadt,
           (acc_ct_06+acc_ct_07+acc_ct_08+acc_ct_09+acc_ct_10+acc_ct_11) AS tot_acc_ct
    FROM merge_data
    ORDER BY road_inv, begmp, endmp
    '''

    cu = conn.cursor()
    
    cu.execute('DROP VIEW IF EXISTS merge_data')
    cu.execute('DROP TABLE IF EXISTS crash_data')
    
    cu.execute(qry_merge_data)
    cu.execute(qry_final_data)
    
    conn.commit()
    
def get_data():
    # set the working directory
    set_directory()
    # get the query result and store as a pandas dataframe
    conn = dbi.connect('crash_database')
    
    table_list = pd.read_sql('''
                             SELECT name FROM sqlite_master
                             WHERE type = "table"
                             ''',
                             con=conn)
    
    if not any(table_list.name=='crash_data'):
        merge_annual_data(conn)

    crash_data = pd.read_sql('SELECT * FROM crash_data', con=conn)
    
    conn.close()
    # return the merged table
    return crash_data

def plot_x_vs_y(df, colname_x, colname_y):
    """
    scatter plot of attribute x against y
    Parameters:
    @df {dataframe} datasource
    @colname_x {string} column name for attribute x
    @colname_y {string} column name for attribute y
    Return:
    @fig {matplotlib.figure} the produced figure
    """
    plt.scatter(df[colname_x], df[colname_y])
    plt.title(colname_x +' vs. '+ colname_y)
    plt.xlabel(colname_x)
    plt.ylabel(colname_y)
    plt.show()
    return plt.figure()
