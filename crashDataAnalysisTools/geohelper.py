import geopandas as gp
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


def convert_3D_2D(geometry):
'''
Takes a GeoSeries of Multi/Polygons and returns a list of Multi/Polygons
'''
import geopandas as gp
new_geo = []
for p in geometry:
    if p.has_z:
        if p.geom_type == 'Polygon':
            lines = [xy[:2] for xy in list(p.exterior.coords)]
            new_p = Polygon(lines)
            new_geo.append(new_p)
        elif p.geom_type == 'MultiPolygon':
            new_multi_p = []
            for ap in p:
                lines = [xy[:2] for xy in list(ap.exterior.coords)]
                new_p = Polygon(lines)
                new_multi_p.append(new_p)
            new_geo.append(MultiPolygon(new_multi_p))
return new_geo


def draw_road_network_map(shpurl, llon, llat, rlon, rlat)

    map = Basemap(llcrnrlon = llon, llcrnrlat = llat, urcrnrlon = rlon, urcrnrlat = rlat,
             resolution = 'i', projection = 'tmerc', lat_0 = (llat + rlat) / 2, lon_0 = (llon + rlon) / 2)
    
    map.readshapefile(shpurl, 'highway')
    
    plt.show()

def draw_crash_map(shpurl, name, llon, llat, rlon, rlat, lons, lats, crashrates)

    map = Basemap(llcrnrlon = llon, llcrnrlat = llat, urcrnrlon = rlon, urcrnrlat = rlat,
             resolution = 'i', projection = 'tmerc', lat_0 = (llat + rlat) / 2, lon_0 = (llon + rlon) / 2)

    map.readshapefile(shpurl, 'highway')

    max = max(crashrates)	
    for index in range(len(crashrates)):
        x, y = map(lons[index], lats[index])
        map.plot(x, y, marker= 'o', color = 'r', markersize = crashrates[index] * 25 / max)
	
    
    plt.show()
	
