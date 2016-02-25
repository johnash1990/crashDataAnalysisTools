import os

import pandas as pd
import sqlite3 as dbi

def get_seg_elev(road_tb, elev_tb):
    '''
    This is the function that integrate the grade information stored in the
    elevation table into the road segment table.

    Two .csv files were saved in the current working directory, with Washington
    State road segment data and elevation information stored separately.
    The function creates a database which contains these two tables together
    and executes a sql query to merge these two tables.

    The input of the function include two string variables denote the file
    names (including file paths if needed) of the two data tables. The output
    of the function will be the merged table in the form of a pandas dataframe.
    '''

    # read the data tables from .csv files
    roads = pd.read_csv(road_tb)
    elev = pd.read_csv(elev_tb)

    # create a connection to the crash database in the current work directory
    # the database will be created if it does not exist
    conn = dbi.connect('crash_database')

    # create a database cursor that can execute query statements
    cu = conn.cursor()

    # drop tables in the database if needed
    cu.execute('DROP TABLE IF EXISTS roads')
    cu.execute('DROP TABLE IF EXISTS elev')

    # convert the pandas datafromes into database tables through the connection
    roads.to_sql(name='roads', con=conn)
    elev.to_sql(name='elev', con=conn)

    # sql query statement to summarize and merge elevation data
    query_merge_elev = '''
        SELECT roads.*,
               AVG(elev.Grade) AS avg_grade,
               MAX(elev.Grade) AS max_grade,
               MIN(elev.Grade) AS min_grade
        FROM roads, elev
        WHERE roads.road_inv = elev.Route_ID AND
              elev.Milepost BETWEEN roads.begmp AND roads.endmp
        GROUP BY road_inv, begmp, endmp
        ORDER BY road_inv, begmp, endmp
        '''

    # get the query result and store as a pandas dataframe
    query_result = pd.read_sql(query_merge_elev, con=conn)

    # return the merged table
    return query_result
