import geopandas
import math
import matplotlib.pyplot as plt

from unidecode import unidecode
from shapely.geometry import Point
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="TwitterOpinion", timeout=10)

def generateDensityMap(df):
    df['Coordinates'] = list(zip(df.Longitude, df.Latitude))
    df['Coordinates'] = df['Coordinates'].apply(Point)
    gdf = geopandas.GeoDataFrame(df, geometry='Coordinates')
    
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

    ax = world.plot(
        color='white', edgecolor='black', figsize=(12, 12))

    gdf.plot(ax=ax, color='red')

    return plt

def getCensusTract(latitude, longitude):
    try:
        location = geolocator.reverse(str(latitude)+","+str(longitude))
        address = location.raw.get('address')
        return (unidecode(address.get('postcode')).replace("/"," "),unidecode(address.get('city') or address.get('town')).lower().replace("/"," "),unidecode(address.get('country')).lower().replace("/"," "))
    except:
        return None

def getCoordinates(location):
    return geolocator.geocode(location)

def getGeoDistance(point1, point2):
	(lat1, lon1) = point1
	(lat2, lon2) = point2
	radius = 6371
	dlat = math.radians(lat2-lat1)
	dlon = math.radians(lon2-lon1)
	lat1 = math.radians(lat1)
	lat2 = math.radians(lat2)
	a = math.sin(dlat/2) ** 2 + math.sin(dlon/2) ** 2 * math.cos(lat1) * math.cos(lat2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	return radius * c

def isLocationCloser(location, coordinates, th):
    try:
        location = getCoordinates(location)
        if not location:
            return False
    except:
        return False
    distance = getGeoDistance((location.latitude, location.longitude),coordinates)
    if distance < th:
        return True
    return False

def isLocationInArea(location, coordinates):
    try:
        location = getCoordinates(location)
        if not location:
            return False
    except:
        return False
    return isAreaMatch(location, coordinates)

def isAreaMatch(location1, location2):
	(ix,ax,iy,ay) = location1.raw['boundingbox']
	ix = float(ix)
	ax = float(ax)
	iy = float(iy)
	ay = float(ay)
	(lat, lon) = location2
	if (lat >= ix) and (lat <= ax) and (lon >= iy) and (lon <= ay):
		return True
	return False