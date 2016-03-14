import os
import pandas as pd
import sqlite3 as dbi

import matplotlib.pyplot as plt


def set_directory():
    os.chdir('../data/')

def merge_data():
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
    
    road = pd.read_csv('road_WA.csv')
    elev = pd.read_csv('elev_WA.csv')
    acc = pd.read_csv('acc_WA.csv')
    curv = pd.read_csv('curv_WA.csv')
    grad = pd.read_csv('grad_WA.csv')

    # create a connection to the crash database in the current work directory
    # the database will be created if it does not exist
    conn = dbi.connect('crash_database')

    # create a database cursor that can execute query statements
    cu = conn.cursor()

    # drop tables in the database if needed
    cu.execute('DROP TABLE IF EXISTS road')
    cu.execute('DROP TABLE IF EXISTS elev')
    cu.execute('DROP TABLE IF EXISTS acc')
    cu.execute('DROP TABLE IF EXISTS curv')
    cu.execute('DROP TABLE IF EXISTS grad')

    # convert the pandas dataframes into database tables through the connection
    road.to_sql(name='road', con=conn)
    elev.to_sql(name='elev', con=conn)
    acc.to_sql(name='acc', con=conn)
    curv.to_sql(name='curv', con=conn)
    grad.to_sql(name='grad', con=conn)

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
           road_inv, spd_limt, e.begmp AS begmp, endmp, lanewid,
           no_lanes, lshldwid, rshldwid, medwid, seg_lng, aadt,
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
    CREATE TABLE crash_data AS
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
    cu.execute('DROP TABLE IF EXISTS crash_data')

    cu.execute(qry_merge_elev)
    cu.execute(qry_merge_grad)
    cu.execute(qry_merge_curv)
    cu.execute(qry_merge_acc)
    
    conn.commit()
    conn.close()

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
        merge_data()

    crash_data = pd.read_sql('SELECT * FROM crash_data, con=conn)
    
    conn.close()
    # return the merged table
    return crash_data

def merge_data_by_year(dfList):
    # take a subset of the columns that we want to merge
    colList = ['road_inv','begmp','endmp','aadt','acc_count']

    # add two cols to the first df to calc the avg aadt and total acc counts
    dfList[0]['avg_aadt'] = 0
    dfList[0]['total_acc_ct'] = 0

    # loop over all data frames in the list and update total
    # counts of aadt and accidents
    for df in dfList:
        dfList[0]['avg_aadt'] = dfList[0]['avg_aadt'] + df['aadt']
        dfList[0]['total_acc_ct'] = dfList[0]['total_acc_ct'] + df['acc_count']

    # divide by the length of the list of data frames to get the average aadt
    dfList[0]['avg_aadt'] = dfList[0]['avg_aadt']/len(dfList)

    # merge data for the first two years (only keep aadt and crash
    # count from 2nd year)
    df_first_two_years = pd.merge(dfList[0], dfList[1][colList],
                                  how='left',on=colList[0:3])

    # if there are more than 2 years, merge in the data from years 3 and beyond
    for i in range (2,len(dfList)):
        dfFinal = pd.merge(df_first_two_years, dfList[i][colList], how='left',
                            on=colList[0:3])
    
     # add a column for the log of the average aadt
    dfFinal['log_avg_aadt'] = np.log(dfFinal['avg_aadt'])

    # add a column for the segment length
    dfFinal['segment_len'] = dfFinal['endmp']-dfFinal['begmp']

    # add a column for the offset (=log(segment length*number of years in analysis period))
    dfFinal['offset'] = np.log(dfFinal['segment_len']*len(dfList))

    # return the final data frame
    return dfFinal

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
