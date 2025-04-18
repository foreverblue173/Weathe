import requests
from bs4 import BeautifulSoup
import time

params = {
   
}

headers = {
    "User-Agent": "YourAppName (your@email.com)"
}

def getPointsFromCoords(coords):
    api_url = "https://api.weather.gov/points/" + str(coords[0]) + "," + str(coords[1])
    response = requests.get(api_url, headers=headers, params=params)
    try:
        response.raise_for_status()
        properties = response.json().get('properties', [])  
        x = properties["gridX"]
        y = properties["gridY"]
        station = properties["gridId"]
        points = station + "/"+str(x)+","+str(y)
        return points
    except:
        print("Error loading " + api_url)
        return None
    
def getForecast(points):
    api_url = "https://api.weather.gov/gridpoints/" + points + "/forecast"
    response = requests.get(api_url, headers=headers, params=params)
    try:
        response.raise_for_status()
        properties = response.json().get('properties', [])
        periods = properties["periods"]
        return periods
    except:
        print("Error loading " + api_url)
        return None
    
def getForecastHourly(points):
    api_url = "https://api.weather.gov/gridpoints/" + points + "/forecast/hourly"
    response = requests.get(api_url, headers=headers, params=params)
    try:
        response.raise_for_status()
        properties = response.json().get('properties', [])
        periods = properties["periods"]
        return periods
    except:
        print("Error loading " + api_url)
        return None

def getCurrentWeather(points):
    api_url = "https://api.weather.gov/gridpoints/" + points
    response = requests.get(api_url, headers=headers, params=params)
    try:
        response.raise_for_status()
        properties = response.json().get('properties', [])
        return properties
    except:
        print("Error loading " + api_url)
        return None
    
def getObservationStationFromPoints(points):
    api_url = "https://api.weather.gov/gridpoints/" + points + "/stations"
    response = requests.get(api_url, headers=headers, params=params)
    try:
        response.raise_for_status()
        properties = response.json().get('features', [])
        station = properties[0]
        return station['id']
    except:
        print("Error loading " + api_url)
        return None
    
def getObservationsFromCoords(points):
    station_url = getObservationStationFromPoints(points) + "/observations"
    
    response = requests.get(station_url, headers=headers, params=params)
    try:
        response.raise_for_status()
        properties = response.json().get('features', [])
        return properties
    except:
        print("Error loading " + station_url)
        return None 

def getLocationFromCoords(coords):
    
    api_url = "https://api.weather.gov/points/" + str(coords[0]) + "," + str(coords[1])
    response = requests.get(api_url, headers=headers, params=params)
    try:
        response.raise_for_status()
        geometry = response.json().get('properties', [])  
        geometry = geometry["relativeLocation"]["properties"]
        location = {"city": geometry["city"], "state": geometry["state"]}
        return location
    except:
        print("Error loading " + api_url)
        return None