import os
import pandas as pd
import sqlite3 as dbi


def get_crash_count(road_tb, elev_tb):
    '''
    Inputs: - a csv file containing individual crash records for
            a given year, each of which has a milepost value and
            route number identifying where the crash took place
            - a csv file defining homogeneous road segments on
            various routes in the state, each of which is defined
            by a route number and a start and end milepost value
    Output: a data frame with the number of crashes that occurred on
    each road segment
    - Computes the sum of crashes for the segments as defined based on
    the milepost at which the individual crash occured on the specified
    route using a sql query.
    '''

    # construct the filepaths for the csv files
    road_path = os.getcwd() + '/' + road_tb + '.csv'
    elev_path = os.getcwd() + '/' + elev_tb + '.csv'

    # turn the csv files into pandas data frames
    road = pd.read_csv(road_path)
    elev = pd.read_csv(elev_path)

    # create a db in sqlite3, establish a connection
    conn = dbi.connect('crash_database')

    # get a cursor for sql queries
    cu = conn.cursor()

    # drop the tables if they already exist, assuming the function
    # has been called at least once, the tables will exist
    cu.execute('DROP TABLE IF EXISTS road')
    cu.execute('DROP TABLE IF EXISTS elev')

    # convert the dataframes to sql tables
    road.to_sql(name='road', con=conn)
    elev.to_sql(name='elev', con=conn)

    # query to join count total number of crashes occuring on
    # each road segment based on route number and milepost
    merge_elev_query = '''
        SELECT RoadSegments.begmp, RoadSegments.endmp, RoadSegments.road_inv,
        COUNT(Crashes.caseno) as CrashCount
        FROM Crashes, RoadSegments
        WHERE Crashes.rd_inv = RoadSegments.road_inv AND
        Crashes.milepost BETWEEN RoadSegments.begmp AND RoadSegments.endmp
        GROUP BY RoadSegments.begmp, RoadSegments.endmp, RoadSegments.road_inv
        ORDER BY RoadSegments.road_inv
        '''


    select_all_query = 'SELECT * FROM road'
    result_query = pd.read_sql(select_all_query, con=conn)


    # create a data frane with the crash counts by segment
    road_elev = pd.read_sql(merge_elev_query, con=conn)

    # merge the crash counts into the road segment data frame
    roadSegmentsAndCrashCounts = pd.merge(roadSeg,
                                          segmentCrashCount, how='left',
                                          on=['road_inv', 'begmp', 'endmp'])

    # convert the NaN's to 0's
    roadSegmentsAndCrashCounts['CrashCount'].fillna(0, inplace=True)

    # return the merged dataframe
    return roadSegmentsAndCrashCounts
