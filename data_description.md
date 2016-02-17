# Highway Safety Information System (HSIS) Data
**All data described in the following have been verified to be available and are in the hands of the project team** 
## Crash Data (total size: 23.1 MB)
- **Files:** 
	- wa06acc.csv (size: 4.16 MB, dimension: 48967 x 16)
	- wa07acc.csv (size: 4.09 MB, dimension: 47732 x 16)
	- wa08acc.csv (size: 3.79 MB, dimension: 44252 x 16)
	- wa09acc.csv (size: 3.69 MB, dimension: 42450 x 16)
	- wa10acc.csv (size: 3.69 MB, dimension: 42460 x 16)
	- wa11acc.csv (size: 3.71 MB, dimension: 42700 x 16)
- **Columns:**
	- rd_inv (String): route number
	- milepost (float): milepost at which crash took place
	- caseno (int): police crash report number 
	- accyr (int): year in which the crash took place
	- rte_nbr: route number on which the crash took place
	- county (int): county in which the crash took place
	- func_cls (int): functional classification of the roadway on which the crash took place
	- month (int): month in which the crash took place
	- daymth (int): day on which the crash took place
	- acctype (int): type of crash (e.g., rear-end, head-on etc.)
	- severity (int): severity of crash (e.g., K-fatal, A-incapacitating inj, B-non-incapacitating inj, C-possible inj, O-proprty damage only)
	- loc_type (int): location type where the crash took place
	- rd_char1 (int): characteristics of the roadway at the time of the crash
	- rdsurf (int): type of roadway surface
	- light (int): light condition at the time of the crash
	- weather (int): weather condition at the time of the crash

## Roadway Inventory Data (total size: 17.1 MB)
- **Files:**
	- wa06road.csv (size: 2.90 MB, dimension: 37772 x 15)
	- wa07road.csv (size: 2.95 MB, dimension: 38424 x 15)
	- wa08road.csv (size: 2.99 MB, dimension: 38990 x 15)
	- wa09road.csv (size: 3.04 MB, dimension: 39455 x 15)
	- wa10road.csv (size: 2.66 MB, dimension: 38890 x 15)
	- wa11road.csv (size: 2.56 MB, dimension: 40263 x 15)
- **Columns:**
	- lhsl_typ (int): left shoulder type
	- med_type (int): median type
	- rshl_type (int): right shoulder type
	- surf_typ (int): surface type
	- road_inv (String): route number
	- spd_limt (int): speed limit
	- begmp (float): beginning milepost of segment
	- endmp (float): ending milepost of segment
	- lanewid (int): total lane width in cross-section
	- no_lanes (int): number of lanes in cross-section
	- lshldwid (int): median width in feet
	- rshldwid (int): median width in feet
	- medwid (int): median width in feet
	- seg_lng (float): segment length in miles
	- aadt (int): annual average daily traffic

## Horizontal Roadway Curvature Data (total size: 2.53 MB)
- **Files:**
	- wa06curv.csv (size: 421 KB, dimension:  15533 x 4)
	- wa07curv.csv (size: 423 KB, dimension:  15627 x 4)
	- wa08curv.csv (size: 427 KB, dimension:  15748 x 4)
	- wa09curv.csv (size: 434 KB, dimension:  15974 x 4)
	- wa10curv.csv (size: 440 KB, dimension:  16221 x 4)
	- wa11curv.csv (size: 443 KB, dimension:  16311 x 4)
- **Columns:**
	- curv_inv (String): route number
	- dir_curv (binary/boolean): direction of curve (i.e., L or R)
	- begmp (float): beginning milepost of horizontal curve
	- pct_grad (float): degree of curve on segment
	
## Roadway Grade Data (total size: 5.40 MB)
- **Files:**
	- wa06grad.csv (size: 908 KB, dimension: 33394 x 4)
	- wa07grad.csv (size: 912 KB, dimension: 33548 x 4)
	- wa08grad.csv (size: 916 KB, dimension: 33690 x 4)
	- wa09grad.csv (size: 926 KB, dimension: 34068 x 4)
	- wa10grad.csv (size: 931 KB, dimension: 34264 x 4)
	- wa11grad.csv (size: 937 KB, dimension: 34430 x 4)
- **Columns:**
	- grad_inv (String): route number
	- dir_grad (binary/boolean): direction of grade (i.e., + or -)
	- pct_grad (float): percentage grade of segment
	- begmp (float): beginning milepost of vertical curve

# Freeway Elevation Data
The dataset is created by the Smart Transportation Applications & Research Laboratory (STAR Lab) at University of Washington. It contains an individual table for freeway elevation information (at 10 ft. intervals) in each state in the US. The elevation information is extracted from Google Earth elevation database. In the class project, only Washington State elevation data was used.

## Washington State Freeway Elevation Data (total size: 67.72 MB)
- **Files:**
	- WA.csv (size: 67.72 MB, dimension: 926752 x 8)

- **Columns:**
	- State: US Postal Service abbreviated state name
	- Route_Name: Interstate name in the form of “I-” followed by a number of up to three digits. For example, Interstate 95 is coded as “I-95”
	- Route_ID: This field is inherited from the FHWA ARNOLD GIS Maps
	- Direction: Direction of the interstate, with “N”, “S”, “E”, and “W” representing North, South, East, and West, respectively. For states not having bi-directional interstate centerlines in the FHWA ARNOLD GIS Maps, “Single” is used as the direction
	- Longitude: Geographic longitude (in degrees) for each point
	- Latitude: Geographic latitude (in degrees) for each point
	- Milepost: Interstate milepost information for each point (mi.).
	- Elevation: Elevation readings are in feet. The NAD27 datum is referenced by Google Earth.

# Weather Data

## WA weather Data (total size: ~1 MB)
- **Files:** 
	- weather_06.txt (size: 0.03 MB, dimension: 365 x 23)
	- weather_07.txt (size: 0.03 MB, dimension: 365 x 23)
	- weather_08.txt (size: 0.03 MB, dimension: 365 x 23)
	- weather_09.txt (size: 0.03 MB, dimension: 365 x 23)
	- weather_10.txt (size: 0.03 MB, dimension: 365 x 23)
	- weather_11.txt (size: 0.03 MB, dimension: 365 x 23)
- **Columns:**
	- PST: date
    - Max TemperatureF
    - Mean TemperatureF
    - Min TemperatureF
    - Max Dew PointF
    - Mean Dew PointF
    - Min DewpointF
    - Max Humidity
    - Mean Humidity
    - Min Humidity
    - Max Sea Level PressureIn
    - Mean Sea Level PressureIn
    - Min Sea Level PressureIn
    - Max VisibilityMiles
    - Mean VisibilityMiles
    - Min VisibilityMiles
    - Max Wind SpeedMPH
    - Mean Wind SpeedMPH
    - Max Gust SpeedMPH
    - PrecipitationIn
    - CloudCover
    - Events: rain, fog, etc.
    - WindDirDegrees

### Question about unit tests: 
Is it possible to create a subset of the data for unit test purposes?
### Answer: 
Yes, although the combined crash data set is not that large, the data is broken down by year providing natural subsets (i.e., use one year of data instead of all six) that could be used in unit tests to test general functionality and reduce processing time.
