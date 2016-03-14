import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap


def draw_road_network_map(shpurl, llon, llat, rlon, rlat):
    '''
    A function to plot a road network from shapefile
    Parameters:
    @shpurl {string} the shapefile url, without suffix,
    e.g. '../data/highway/wgs84'
    @llon {float} longitude of the top left corner
    @llat {float} latitude of the top left corner
    @rlon {float} longitude of the bottom right corner
    @rlat {float} latitude of the bottom right corner
    Return: Nothing
    '''
    # set up a map canvas
    map = Basemap(llcrnrlon=llon, llcrnrlat=llat,
                  urcrnrlon=rlon, urcrnrlat=rlat, resolution='i',
                  projection='tmerc', lat_0=(llat+rlat)/2,
                  lon_0=(llon+rlon)/2)
    # read the shapefile
    map.readshapefile(shpurl, 'highway')
    # show the map
    plt.show()


def draw_crash_map(shpurl, name, llon, llat, rlon, rlat, lons, lats, data):
    '''
    A function to plot hot spot map for crash rate and
    crash severity
    Parameters:
    @shpurl {string} the shapefile url, without suffix,
    e.g. '../data/highway/wgs84'
    @name {float} either 'rate' or 'severity'
    @llon {float} longitude of the top left corner
    @llat {float} latitude of the top left corner
    @rlon {float} longitude of the bottom right corner
    @rlat {float} latitude of the bottom right corner
    @lons {a list of float} longitudes of the crash spots
    @lats {a list of float} latitudes of the crash spots
    @data {a list of float} data for crash rates or severity
    Return: Nothing
    '''
    # set up a map canvas
    map = Basemap(llcrnrlon=llon, llcrnrlat=llat,
                  urcrnrlon=rlon, urcrnrlat=rlat, resolution='i',
                  projection='tmerc', lat_0=(llat+rlat)/2,
                  lon_0=(llon+rlon)/2)
    # read the shapefile
    map.readshapefile(shpurl, 'highway')

    # get the max value from the data to scale the size of the marker
    max = max(data)
    # plot the hot spots one by one with the marker
    # size corresponding to the data
    for index in range(len(data)):
        x, y = map(lons[index], lats[index])
        map.plot(x, y, marker='o', color='r', markersize=(data[index]*25/max))

    # show the map
    plt.show()
