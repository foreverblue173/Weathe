from locationHandler import getForecast, getForecastHourly, getCurrentWeather, getObservationsFromCoords, getLocationFromCoords
import asyncio
import time

#CONVERSIONS
def celsius_to_fahrenheit(celsius):
    try:
        fahrenheit = (celsius * 9/5) + 32
        return fahrenheit
    except:
        return None

def kph_to_mph(kph):
    try:
        mph = kph * 0.621371
        return mph
    except:
        return None

def pa_to_mb(pa):
    try:
        mb = pa / 100
        return mb
    except:
        return None

def meters_to_miles(meters):
    try:
        miles = meters / 1609.344
        return miles
    except:
        return None

def mm_to_inches(mm):
    try:
        inches = mm / 25.4
        return inches
    except:
        return None

def getTemperatureFromData(data):
    try:
        temp = data["temperature"]
        if temp["unitCode"] == 'wmoUnit:degC':
            return celsius_to_fahrenheit(temp["value"])
        else:
            return temp["value"]
    except:
        return None

def getMinFromData(data):
    try:
        temp = data["minTemperatureLast24Hours"]
        if temp["unitCode"] == 'wmoUnit:degC':
            return celsius_to_fahrenheit(temp["value"])
        else:
            return temp["value"]
    except:
        return None
    
def getMaxFromData(data):
    try:
        temp = data["maxTemperatureLast24Hours"]
        if temp["unitCode"] == 'wmoUnit:degC':
            return celsius_to_fahrenheit(temp["value"])
        else:
            return temp["value"]
    except:
        return None

def getDewpointFromData(data):
    try:
        temp = data["dewpoint"]
        if temp["unitCode"] == 'wmoUnit:degC':
            return celsius_to_fahrenheit(temp["value"])
        else:
            return temp["value"]
    except:
        return None
    
def getWindChillFromData(data):
    try:
        temp = data["windChill"]
        if temp["unitCode"] == 'wmoUnit:degC':
            return celsius_to_fahrenheit(temp["value"])
        else:
            return temp["value"]
    except:
        return None
    
def getHeatIndexFromData(data):
    try:
        temp = data["heatIndex"]
        if temp["unitCode"] == 'wmoUnit:degC':
            return celsius_to_fahrenheit(temp["value"])
        else:
            return temp["value"]
    except:
        return None

def getWindSpeedFromData(data):
    try:
        temp = data["windSpeed"]
        if temp["unitCode"] == 'wmoUnit:km_h-1':
            return kph_to_mph(temp["value"])
        else:
            return temp["value"]
    except:
        return None

def getWindGustFromData(data):
    try:
        temp = data["windGust"]
        if temp["unitCode"] == 'wmoUnit:km_h-1':
            return kph_to_mph(temp["value"])
        else:
            return temp["value"]
    except:
        return None

def getPressureFromData(data):
    try:
        temp = data["barometricPressure"]
        if temp["unitCode"] == 'wmoUnit:Pa':
            return pa_to_mb(temp["value"])
        else:
            return temp["value"]
    except:
        return None

def getSeaLevelPressureFromData(data):
    try:
        temp = data["seaLevelPressure"]
        if temp["unitCode"] == 'wmoUnit:Pa':
            return pa_to_mb(temp["value"])
        else:
            return temp["value"]
    except:
        return None
    
def getVisibilityFromData(data):
    try:
        temp = data["visibility"]
        if temp["unitCode"] == 'wmoUnit:m':
            return meters_to_miles(temp["value"])
        else:
            return temp["value"]
    except:
        return None

def getPercipitation1(data):
    try:
        temp = data["precipitationLastHour"]
        if temp["unitCode"] == 'wmoUnit:mm':
            return mm_to_inches(temp["value"])
        else:
            return temp["value"]
    except:
        return None
    
def getPercipitation3(data):
    try:
        temp = data["precipitationLast3Hours"]
        if temp["unitCode"] == 'wmoUnit:mm':
            return mm_to_inches(temp["value"])
        else:
            return temp["value"]
    except:
        return None

def getPercipitation6(data):
    try:
        temp = data["precipitationLast6Hours"]
        if temp["unitCode"] == 'wmoUnit:mm':
            return mm_to_inches(temp["value"])
        else:
            return temp["value"]
    except:
        return None

def getHumidityFromData(data):
    temp = data["relativeHumidity"]
    return temp["value"]

def unpackData(data): #Gets latest observation from data
    return data[0]['properties']

def getConditions(coords, location): #Gets current conditions for a location
    try:
        observations = getObservationsFromCoords(coords)
    except:
        observations = None
    if observations == None:
        return observations #Aborts when error
    observations = unpackData(observations)

    conditions = location

    conditions["temperature"] = getTemperatureFromData(observations)
    conditions["min"] = getMinFromData(observations)
    conditions["max"] = getMaxFromData(observations)
    conditions["dewpoint"] = getDewpointFromData(observations)
    conditions["windChill"] = getWindChillFromData(observations)
    conditions["heatIndex"] = getHeatIndexFromData(observations)
    conditions["windSpeed"] = getWindSpeedFromData(observations)
    conditions["windGust"] = getWindGustFromData(observations)
    conditions["surfacePressure"] = getPressureFromData(observations)
    conditions["seaLevelPressure"] = getSeaLevelPressureFromData(observations)
    conditions["visibility"] = getVisibilityFromData(observations)
    conditions["oneHourPercipitation"] = getPercipitation1(observations)
    conditions["threeHourPercipitation"] = getPercipitation3(observations)
    conditions["sixHourPercipitation"] = getPercipitation6(observations)
    conditions["humidity"] = getHumidityFromData(observations)

    return conditions

def getNameFromForecast(f):
    return f["name"]

def getTemperatureFromForecast(f):
    temperatures = {}

    if f['temperatureUnit'] == "F":
        temperatures["temperature"] = f['temperature']
    else:
        temperatures["temperature"] = celsius_to_fahrenheit(f['temperatureUnit'])
    return temperatures

def getIsDayTimeFromForecast(f):
    return f['isDayTime']

def getprobOfPercipitationFromForecast(f):
    val = f['probabilityOfPrecipitation']['value']
    if val == None:
        val = 0

    return float(val/100.0)

def getWindValuesFromForecast(f):
    values = {}
    string = f['windSpeed']
    try:
        sep = string.index("to")
        v = string.split(" ")
        values["min"] = int(v[0])
        values["max"] = int(v[1])
    except:
        v = string.split(" ")
        values["min"] = int(v[0])
        values["max"] = int(v[0])

    values['windDirection'] = f['windDirection']
    return values

def getNumberFromForecast(f):
    return f["number"]

def formatForecast(forecast, location, hourly=False):
    f = location.copy()
    if not hourly:
        f["name"] = getNameFromForecast(forecast)
    else:
        f["name"] = getNumberFromForecast(forecast)
    temps = getTemperatureFromForecast(forecast)
    f["probabilityOfPrecipitation"] = getprobOfPercipitationFromForecast(forecast)
    windValues = getWindValuesFromForecast(forecast)
    f.update(temps)
    f.update(windValues)
    f["shortForecast"] = forecast["shortForecast"]
    f["detailedForecast"] = forecast["detailedForecast"]
    f["isDaytime"] = forecast["isDaytime"]
    return f

def getForecastFromCoords(points, location):
    forecast = getForecast(points)

    if forecast == None:
        return forecast #Aborts when error
    
    forecasts = []
    for f in forecast:
        forecasts.append(formatForecast(f, location))

    return forecasts

def getHourlyForecastsFromCoords(points, location):
    forecast = getForecastHourly(points)

    if forecast == None:
        return forecast #Aborts when error

    forecasts = []
    for f in forecast:
        forecasts.append(formatForecast(f, location, hourly=True))

    return forecasts
    #print(forecast)

def getForecastsForLocation(coords, location):
    forecasts = {}

    current = getConditions(coords, location)
    default = getForecastFromCoords(coords, location)
    hourly = getHourlyForecastsFromCoords(coords, location)

    forecasts["current"] = current
    forecasts["default"] = default
    forecasts["hourly"] = hourly
    
    return forecasts

"""
async def main():
    start = time.time()
    forecasts = await getForecastsForLocation([39.6137,-86.1067])
    end = time.time()

asyncio.run(main())
"""