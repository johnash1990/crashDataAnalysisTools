import unittest
from data_prep import *


class DataPrepTest(unittest.TestCase):
    '''
    A series of test functions have been created to test the effectiveness of
    the data pre-processing functions in the data_prep.py file.
    '''
    # test set_directory() function
    def test_set_directory(self):

        # call the set_directory() function
        set_directory()

        # check if the working directory is set to the data folder
        self.assertTrue('\data' in os.getcwd())

    # test get_tables() function
    def test_get_tables(self):

        # set the working directory to the data folder
        set_directory()

        # set up a connection to the database
        conn = dbi.connect('crash_database')

        # call the test function to get the table name list from the database
        tables = get_tables(conn)

        # close the database connection
        conn.close()

        # check if a list of database table names has been included in the
        # returned dataframe
        self.assertTrue('name' in tables.columns.values)

    # test get_annual_data() function
    def test_get_annual_data(self):
        '''
        The tested function creates an annual data table based on the original
        datasets. In order to test the funtion, an annual table has been
        removed and regenerated. The year of 2008 is chosen as an example.
        First we remove the 2008 data table in the database and then call the
        function to create the table. Finally we check if the new 2008 data
        table has been created.
        '''

        # set the working directory to the data folder
        set_directory()

        # set up a connection to the database
        conn = dbi.connect('crash_database')

        # create a database cursor that can execute query statements
        cu = conn.cursor()

        # drop the 2008 data table if it exists in the database
        cu.execute('DROP TABLE IF EXISTS data_08')

        # call the function to create the 2008 data and upload to the database
        data_08 = get_annual_data('08', conn)
        data_08.to_sql(name='data_08', con=conn)

        # get the database table name list
        tables = get_tables(conn)

        # commit the changes to the database and close the connection
        conn.commit()
        conn.close()

        # check if a new 2008 table has been created in the database
        self.assertTrue('data_08' in tables.name.tolist())

    # test merge_annual_data() function
    def test_merge_annual_data(self):
        '''
        Similar to the unit test for get_annual_data(). The test function for
        merge_annual_data() first remove the final dataset (crash_data) in the
        database and then recreate the table.
        '''

        # set the working directory to the data folder
        set_directory()

        # set up a connection to the database
        conn = dbi.connect('crash_database')

        # create a database cursor that can execute query statements
        cu = conn.cursor()

        # drop the crash_data table if it exists in the database
        cu.execute('DROP TABLE IF EXISTS crash_data')

        # call the function to generate the final dataset
        merge_annual_data(conn)

        # get the database table name list
        tables = get_tables(conn)

        # close the database connection
        conn.close()

        # check if a new crash_data table has been created in the database
        self.assertTrue('crash_data' in tables.name.tolist())

    # test get_data() function
    def test_get_data(self):

        # call the function to get the data
        crash_data = get_data()

        # check if the returned dataframe is not empty
        self.assertFalse(crash_data.empty)


if __name__ == '__main__':
    unittest.main()
