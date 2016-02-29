import os
import pandas as pd
import sqlite3 as dbi


def merge_crash_and_segment(crashes, roadSegments):
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
    crashFilePath = os.getcwd() + '/' + crashes + '.csv'
    roadSemgentsFilePath = os.getcwd() + '/' + roadSegments + '.csv'

    # turn the csv files into pandas data frames
    crashes = pd.read_csv(crashFilePath)
    roadSeg = pd.read_csv(roadSemgentsFilePath)

    # create a db in sqlite3, establish a connection
    db = dbi.connect('crashCountDB')

    # get a cursor for sql queries
    dbCur = db.cursor()

    # drop the tables if they already exist, assuming the function
    # has been called at least once, the tables will exist
    dbCur.execute('DROP TABLE IF EXISTS Crashes')
    dbCur.execute('DROP TABLE IF EXISTS RoadSegments')

    # convert the dataframes to sql tables
    crashes.to_sql(name='Crashes', con=db)
    roadSeg.to_sql(name='RoadSegments', con=db)

    # query to join count total number of crashes occuring on
    # each road segment based on route number and milepost
    qryGetCrashCount = '''
        SELECT RoadSegments.*,
        COUNT(Crashes.caseno) as CrashCount
        FROM Crashes, RoadSegments
        WHERE Crashes.rd_inv = RoadSegments.road_inv AND
        Crashes.milepost BETWEEN RoadSegments.begmp AND RoadSegments.endmp
        GROUP BY RoadSegments.begmp, RoadSegments.endmp, RoadSegments.road_inv
        ORDER BY RoadSegments.road_inv
        '''

    # create a data frane with the crash counts by segment
    segmentCrashCount = pd.read_sql(qryGetCrashCount, con=db)

    # merge the crash counts into the road segment data frame
    roadSegmentsAndCrashCounts = pd.merge(roadSeg,
                                          segmentCrashCount, how='left',
                                          on=['road_inv', 'begmp', 'endmp'])

    # convert the NaN's to 0's
    roadSegmentsAndCrashCounts['CrashCount'].fillna(0, inplace=True)

    # return the merged dataframe
    return roadSegmentsAndCrashCounts
