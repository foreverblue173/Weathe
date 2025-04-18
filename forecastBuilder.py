from forecastHandler import getForecastsForLocation
from locationHandler import getLocationFromCoords
import asyncio

#IMPORTANCE LEVEL
# 1- most
# 2 - medium
# 3 - least
DEFAULT_CITIES = [
    [41.8781, -87.6298, 1], #Chicago
    [39.7691, -86.1580, 2], #Indianapolis
    [38.6270, -90.1994, 2], #St. Louis
    [38.2469, -85.7664, 3], #Louisville
    [39.1031, -84.5120, 3], #Cincinatti
    [43.0410, -87.9097, 3], #Milwaukee
    [42.3297, -83.0425, 2], #Detroit
    [41.4993, -81.6944, 2], #Cleveland
    [39.9625, -83.0032, 3], #Columbus Ohio
    [40.4387, -79.9972, 2], #Pittsburgh
    [39.2905, -76.6104, 2], #Baltimore
    [40.7128, -74.0060, 1], #New York
    [42.3555, -71.0565, 2], #Boston
    [38.9072, -77.0369, 1], #Washington DC
    [37.5407, -77.4360, 3], #Richmond VA
    [39.9526, -75.1652, 2], #Philidelphia
    [47.6061, -122.3328, 1], #Seattle
    [45.5152, -122.6784, 2], #Portland
    [43.6150, -116.2023, 3], #Boise
    [38.5781, -121.4944, 2], #Sacramento
    [39.5299, -119.8143, 3], #Reno
    [36.1716, -115.1391, 2], #Vegas
    [40.7606, -111.8881, 3], #SLC
    [37.7749, -122.4194, 1], #San Francisco
    [34.0549, -118.2426, 1], #LA
    [30.4382, -84.2806, 2], #Tallahasee
    [25.7617, -80.1918, 1], #Miami
    [28.5384, -81.3789, 2], #Orlando
    [27.9517, -82.4588, 2], #Tampa
    [33.7501, -84.3885, 1], #Atlanta
    [35.7796, -78.6382, 3], #Raleigh
    [36.1627, -86.7816, 2], #Nashville
    [33.5186, -86.8104, 3], #Birmingham
    [32.7833, -79.9320, 3], #Charleston
    [34.7445, -92.2880, 3], #Little Rock
    [29.7601, -95.3701, 1], #Houston
    [30.2672, -97.7431, 3], #Austin
    [32.7767, -96.7970, 2], #Dallas
    [35.4689, -97.5195, 3], #Oklahoma city
    [35.6894, -105.9382, 3], #Santa fe
    [31.7619, -106.4850, 3], #El paso
    [33.4482, -112.0777, 1], #Phoenix
    [44.9778, -93.2650, 2], #Minneapolis
    [39.0997, -94.5786, 2], #Kansas city
    [41.5896, -93.6164, 3], #De moines
    [46.8772, -96.7898, 3], #Fargo 
    [43.5460, -96.7313, 3], #Sioux falls
    [40.8137, -96.7026, 3], #Lincoln
    [46.5891, -112.0391, 3], #Helena
    [45.7828, -108.5046, 3], #Billings
    [39.7392, -104.9903, 1], #Denver
    [43.4799, -110.7624, 3] #Jackson
]

class ForecastBuilder:
    def __init__(self, CUSTOM_CITIES):

        self.locations = DEFAULT_CITIES + CUSTOM_CITIES
        
        if len(CUSTOM_CITIES) > 0:
            self.primary_location = CUSTOM_CITIES[0]
        else:
            self.primary_location = [39.7691, -86.1580]

        #print(self.locations)


    async def getForecastsFromCoord(self, coord):
        f = await getForecastsForLocation(coord)
        location = await getLocationFromCoords(coord)
        return location["city"], f

