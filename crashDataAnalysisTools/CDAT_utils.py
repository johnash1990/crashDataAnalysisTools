import os
import pandas as pd
import sqlite3 as dbi

import matplotlib.pyplot as plt


def merge_data(road_tb, elev_tb, acc_tb):
    '''
    This is the function that integrates the grade information stored in the
    elevation table into the road segment table.

    Two .csv files were saved in the current working directory, with Washington
    State road segment data and elevation information stored separately.
    The function creates a database which contains these two tables together
    and executes a sql query to merge these two tables.

    The input of the function include two string variables denote the file
    names (including file paths if needed) with the '.csv' suffix of the two
    data tables. The output of the function will be the merged table in the
    form of a pandas dataframe.
    '''

    # read the data tables from .csv files
    os.chdir('../data/')

    road = pd.read_csv(road_tb)
    elev = pd.read_csv(elev_tb)
    acc = pd.read_csv(acc_tb)

    # create a connection to the crash database in the current work directory
    # the database will be created if it does not exist
    conn = dbi.connect('crash_database')

    # create a database cursor that can execute query statements
    cu = conn.cursor()

    # drop tables in the database if needed
    cu.execute('DROP TABLE IF EXISTS road')
    cu.execute('DROP TABLE IF EXISTS elev')
    cu.execute('DROP TABLE IF EXISTS acc')

    # convert the pandas dataframes into database tables through the connection
    road.to_sql(name='road', con=conn)
    elev.to_sql(name='elev', con=conn)
    acc.to_sql(name='acc', con=conn)

    # This is the sql query statement that will match elevation data with the
    # corresponding road segments through milepost information. Aggregation
    # statistics (e.g., average, maximum and minimum) about grade will be added
    # as extra columns in the roads table.
    query_merge_data = '''
        SELECT road.*,
               AVG(elev.Grade) AS avg_grade,
               MAX(elev.Grade) AS max_grade,
               MIN(elev.Grade) AS min_grade,
               COUNT(acc.caseno) as crash_count
        FROM road, elev, acc
        WHERE road.road_inv = elev.Route_id AND
              elev.milepost BETWEEN road.begmp AND road.endmp AND
              road.road_inv = acc.rd_inv AND
              acc.milepost BETWEEN road.begmp AND road.endmp
        GROUP BY road_inv, begmp, endmp
        ORDER BY road_inv, begmp, endmp
        '''

    # get the query result and store as a pandas dataframe
    query_result = pd.read_sql(query_merge_data, con=conn)

    # return the merged table
    return query_result


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
