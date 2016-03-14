import os
import pandas as pd
import sqlite3 as dbi

import matplotlib.pyplot as plt

from ipywidgets import interact

import seaborn
seaborn.set()


def set_directory():
    # set the current work directory to the data folder
    os.chdir('../data/')


def get_annual_data(year, conn):
    '''
    Parameters:
    @year {string} the year for which to combine different data tables
    @conn {sqlite3 Connection} connection to the studied database
    Return:
    @annual_data {pd dataframe} the combined annual dataframe
    Combine five data tables (road segments, elevation, grade, curvature,
    accidents) to get detailed information as well as crash count for each road
    segment in a specific year. Six years (from 06 to 11) of data are available
    for the analysis. Given a specific year, the function reads the
    corresponding .csv files and converts them into database tables. Attributes
    from different tables are merged into a combined table through SQL codes.
    '''

    # set the current working directory to the data folder
    set_directory()

    # read the .csv files for the specific year
    road = pd.read_csv('wa'+year+'road.csv')
    acc = pd.read_csv('wa'+year+'acc.csv')
    curv = pd.read_csv('wa'+year+'curv.csv')
    grad = pd.read_csv('wa'+year+'grad.csv')

    # the roadway elevation infomration does not change over years, the same
    # file is used for all six years
    elev = pd.read_csv('wa_elev.csv')

    # create a database cursor that can execute query statements
    cu = conn.cursor()

    # before converting dataframes into the database, drop existing tables with
    # conflicting names
    cu.execute('DROP TABLE IF EXISTS road')
    cu.execute('DROP TABLE IF EXISTS acc')
    cu.execute('DROP TABLE IF EXISTS curv')
    cu.execute('DROP TABLE IF EXISTS grad')
    cu.execute('DROP TABLE IF EXISTS elev')

    # convert the pandas dataframes into database tables
    road.to_sql(name='road', con=conn)
    acc.to_sql(name='acc', con=conn)
    curv.to_sql(name='curv', con=conn)
    grad.to_sql(name='grad', con=conn)
    elev.to_sql(name='elev', con=conn)

    # SQL query for updating the negative grade values in the grade table
    # (in the original table, signs and absolute values of grade are stored
    # in separate columns)
    qry_compute_signed_grade = '''
    UPDATE grad
    SET pct_grad =
        CASE WHEN dir_grad='-' THEN -1*pct_grad
        ELSE pct_grad
    END
    '''

    # execute the query statement
    cu.execute(qry_compute_signed_grade)

    # SQL query for merging elevation information into the road segment table
    # Two sources of roadway grade information is provided: the elevation
    # dataset contains detailed elevation and grade information for freeways;
    # HSIS grade information covers more roads, but in much lower resolution.
    # In the data merging, HSIS grade is only applied when the elevation
    # information is not available.
    qry_merge_elev = '''
    CREATE VIEW merge_elev AS
    SELECT road.*,
           AVG(elev.Longitude) AS longitude,
           AVG(elev.Latitude) AS latitude,
           AVG(elev.Grade)*100 AS avg_grad,
           MAX(elev.Grade)*100 AS max_grad,
           MIN(elev.Grade)*100 AS min_grad
    FROM road LEFT JOIN elev
    ON road.road_inv = elev.Route_id AND
       elev.milepost BETWEEN road.begmp AND road.endmp
    GROUP BY road.road_inv, road.begmp, road.endmp
    '''

    # SQL query for merging grade informatino when elevation information is not
    # obtainable
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

    # SQL query for merging curvature information
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

    # SQL query for calculating and merging accident counts
    qry_merge_acc = '''
    SELECT c.*,
           COUNT(acc.caseno) AS acc_count
    FROM merge_curv AS c LEFT JOIN acc
    ON c.road_inv = acc.rd_inv AND
       acc.milepost BETWEEN c.begmp AND c.endmp
    GROUP BY c.road_inv, c.begmp, c.endmp
    ORDER BY c.road_inv, c.begmp, c.endmp
    '''

    # drop views if there exists name conflits
    cu.execute("DROP VIEW IF EXISTS merge_elev")
    cu.execute("DROP VIEW IF EXISTS merge_grad")
    cu.execute("DROP VIEW IF EXISTS merge_curv")

    # execute the merging query statements
    cu.execute(qry_merge_elev)
    cu.execute(qry_merge_grad)
    cu.execute(qry_merge_curv)

    # output the last step of data merging as a pandas dataframe
    annual_data = pd.read_sql(qry_merge_acc, con=conn)

    # commit the changes to the database
    conn.commit()

    # return the combined table
    return annual_data


def merge_annual_data(conn):
    '''
    Parameters:
    @conn {sqlite3 Connection} connection to the studied database
    Merge all annual crash tables for six different years. Here we assume the
    road geometry does not change over the six years, while the annual average
    daily traffic (aadt) and crash counts for different years are merged based
    on the road inventory number (road_inv) and the milepost data of each
    segment. The function has no return value and the final table will be saved
    in the database for further use.
    '''

    # get a list of tables in the database
    table_list = pd.read_sql('''
                             SELECT name FROM sqlite_master
                             WHERE type = "table"
                             ''',
                             con=conn)

    # check if the annual data table already exist in the dataframe
    # if not, call the get_annual_data() function to create the annual data
    if not any(table_list.name == 'data_06'):
        data_06 = get_annual_data('06', conn)
        data_06.to_sql(name='data_06', con=conn)

    if not any(table_list.name == 'data_07'):
        data_07 = get_annual_data('07', conn)
        data_07.to_sql(name='data_07', con=conn)

    if not any(table_list.name == 'data_08'):
        data_08 = get_annual_data('08', conn)
        data_08.to_sql(name='data_08', con=conn)

    if not any(table_list.name == 'data_09'):
        data_09 = get_annual_data('09', conn)
        data_09.to_sql(name='data_09', con=conn)

    if not any(table_list.name == 'data_10'):
        data_10 = get_annual_data('10', conn)
        data_10.to_sql(name='data_10', con=conn)

    if not any(table_list.name == 'data_11'):
        data_11 = get_annual_data('11', conn)
        data_11.to_sql(name='data_11', con=conn)

    # SQL query to merge data from all six years
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

    # SQL query to select columns needed for data modeling
    # and calculate the average aadt and total accident count
    qry_final_data = '''
    CREATE TABLE crash_data AS
    SELECT lshl_typ, med_type, rshl_typ, surf_typ, road_inv,
           spd_limt, begmp, endmp, lanewid, no_lanes, lshldwid,
           rshldwid, medwid, seg_lng, longitude, latitude,
           avg_grad, max_grad, min_grad, curv_count, max_deg_curv,
           aadt_06, acc_ct_06, aadt_07, acc_ct_07, aadt_08, acc_ct_08,
           aadt_09, acc_ct_09, aadt_10, acc_ct_10, aadt_11, acc_ct_11,
           (aadt_06+aadt_07+aadt_08+aadt_09+aadt_10+aadt_11)/6 AS avg_aadt,
           (acc_ct_06+acc_ct_07+acc_ct_08+acc_ct_09+acc_ct_10+acc_ct_11)
           AS tot_acc_ct
    FROM merge_data
    ORDER BY road_inv, begmp, endmp
    '''

    # create a database cursor that can execute query statements
    cu = conn.cursor()

    # drop view and table if exists name conflicts
    cu.execute('DROP VIEW IF EXISTS merge_data')
    cu.execute('DROP TABLE IF EXISTS crash_data')

    # execute query statments to merge data
    cu.execute(qry_merge_data)
    cu.execute(qry_final_data)

    # commit changes to the database
    conn.commit()


def get_data():
    '''
    Return:
    @crash_data {pd dataframe} the crash dataset for modeling and analysis
    This function return the processed crash dataset in the form of a pandas
    dataframe for the further data modeling work. The functions for get annual
    data and merge data from different years are called if necessary.
    '''

    # set the current working directory to the data folder
    set_directory()

    # create a connection to the crash database
    # the database will be created if it does not exist
    conn = dbi.connect('crash_database')

    # get a list of tables in the database
    table_list = pd.read_sql('''
                             SELECT name FROM sqlite_master
                             WHERE type = "table"
                             ''',
                             con=conn)

    # if the crash data table does not exist in the database, call the
    # merge_annual_data() function to create the crash dataset
    if not any(table_list.name == 'crash_data'):
        merge_annual_data(conn)

    # read the crash dataset as a pandas dataframe from the database
    crash_data = pd.read_sql('SELECT * FROM crash_data', con=conn)

    # close the database connection
    conn.close()

    # return the crash data table
    return crash_data


def plot_scatter(x='avg_aadt', y='tot_acc_ct'):
    """
    Parameters:
    @x {string} column name for attribute x
    @y {string} column name for attribute y
    Draw the scatter plot of two columns in the crash dataset.
    """

    # get the dataset table as a pandas dataframe
    crash_data = get_data()

    # draw the scatter plot
    plt.clf()
    plt.scatter(crash_data[x], crash_data[y])
    plt.xlabel(x)
    plt.ylabel(y)


def plot_x_vs_y():
    '''
    This functions enables the interactive scatter selections of the columns of
    the scatter plot. Two drop-down interactive widgets are created for users
    to select the two columns shown in the scatter plot.
    '''

    # define two lists of column names from which users can define the data
    # shown on x/y axis of the scatter plot
    x_columns = ['spd_limt', 'lanewid', 'no_lanes', 'lshldwid', 'rshldwid',
                 'medwid', 'seg_lng', 'avg_grad', 'max_grad', 'min_grad',
                 'curv_count', 'max_deg_curv', 'aadt_06', 'aadt_07',
                 'aadt_08', 'aadt_09', 'aadt_10', 'aadt_11', 'avg_aadt']

    y_columns = ['acc_ct_06', 'acc_ct_07', 'acc_ct_08', 'acc_ct_09',
                 'acc_ct_10', 'acc_ct_11', 'tot_acc_ct']

    # interactive scatter plot function
    interact(plot_scatter, x=x_columns, y=y_columns)
