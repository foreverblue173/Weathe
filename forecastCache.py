from forecastBuilder import DEFAULT_CITIES, ForecastBuilder
import time
from locationHandler import getLocationFromCoords, getPointsFromCoords
import asyncio
from forecastHandler import getForecastsForLocation
from imageHandler import getIcon
import random
from concurrent.futures import ThreadPoolExecutor

#{KEY: {lastUpdate, lastAccess, observation, forecast, forecastHourly, isPrimary, isUserTracked, importanceLevel, coords, city, state, gridPoints}}

class ForecastCache:
    def __init__(self, TRACKED_LOCATIONS, MAX_DELAY = 3600, REFRESH_MAX = 15): #MAX_DELAY is the maximum amount of time a radar can go before being updated (DEFAULT 1 HOUR)
        self.FORECAST_BUILDER = ForecastBuilder(TRACKED_LOCATIONS)
        self.TRACKED_LOCATIONS = TRACKED_LOCATIONS
        self.ALL_LOCATIONS = DEFAULT_CITIES + TRACKED_LOCATIONS[0]
        self.empty_forecasts = 0
        self.forecasts = 0
        self.empty_percentage = 0
        self.MAX_DELAY = MAX_DELAY
        self.REFRESH_MAX = REFRESH_MAX
        self.CACHE = {}

    async def construct(self): #Calls after initialization
        print("Constructing forecasts")
        t = time.time()
        list = await self.initializeForecasts()

        self.ALL_LOCATIONS = {}
        for item in list:
            self.addEmptyForecast()
            self.ALL_LOCATIONS[item['city']] = item
            
        end = time.time()
        print(f"Forecasts constructed in {end - t:.2f} seconds")
            
    def updatePercent(self):
        self.empty_percentage = float(self.empty_forecasts)/self.forecasts
        return self.empty_percentage

    def getPercent(self):
        return self.updatePercent()

    def fillForecast(self):
        self.empty_forecasts -= 1
        self.updatePercent()
        return self.empty_forecasts

    def addEmptyForecast(self): #Accessor
        self.forecasts += 1
        self.empty_forecasts +=1

    def addFullForecast(self):
        self.addEmptyForecast()
        self.fillForecast()

    def convertItem(self, loc, isPrimary, isCustom): #Converts singular item
        dict = {"isPrimary" : isPrimary, "isUserTracked" : isCustom, "lastAccess" : None, "lastUpdate" : None, "current" : None, "default" : None, "hourly" : None}
        location = getLocationFromCoords(loc)
        
        if isCustom:
            dict["importanceLevel"] = 1
        else:
            dict["importanceLevel"] = loc[2]

        dict["gridPoints"] = getPointsFromCoords(loc)

        dict["coords"] = loc

        dict.update(location)

        return dict

    async def convertList(self, list, isCustom): #Converts a list of coordinates to a forecast
        tasks = []
        executor = ThreadPoolExecutor()
        loop = asyncio.get_running_loop()
        isPrimary = True and isCustom #ONLY TRUE if the list is custom and for first item of the list
        for loc in list:
            tasks.append(loop.run_in_executor(executor, self.convertItem, loc, isPrimary, isCustom))
            isPrimary = False

        locations = await asyncio.gather(*tasks)
        return locations

    def printStatus(self, hide=True):
        
        forecasts = 0
        empty = 0
        cur = 0
        daily = 0
        hourly = 0
        cities = []
        for item in self.ALL_LOCATIONS:
            cities.append(item)
            forecasts += 1

            r = 0
            if self.ALL_LOCATIONS[item]["default"] == None:
                r += 1
            else:
                daily += 1

            if self.ALL_LOCATIONS[item]["current"] == None:
                r += 1
            else:
                cur += 1
                
            if self.ALL_LOCATIONS[item]["hourly"] == None:
                r += 1
            else:
                hourly += 1

            if r == 3:
                empty += 1
        self.cities = cities
        if hide==True:
            return
        print()
        print(cities)
        print()
        print("cities " + str(forecasts))
        print("Current Forecasts " + str(cur))
        print("daily forecasts " + str(daily))
        print("hourly forecasts " + str(hourly))
        print("empty forecasts " + str(empty))

    async def initializeForecasts(self): #ASYNC COMBINING LISTS
        tasks = [self.convertList(self.TRACKED_LOCATIONS, True), self.convertList(DEFAULT_CITIES, False)]
        locations, locations2 = await asyncio.gather(*tasks)
        return locations2 + locations

    def updateSingleForecastFromDict(self, dict):
        points = dict["gridPoints"]
        location = {"city": dict["city"], "state" :dict["state"]}
        city = dict["city"]
        f = getForecastsForLocation(points, location)
        t = time.time()
        invalid = False #If any forecast cannot be loaded correctly
        for forecast in f:
            if f[forecast] == None:
                invalid = True
                print(city + " " + forecast + " invalid")
                continue
            self.ALL_LOCATIONS[city][forecast] = f[forecast]
        if not invalid:
            self.ALL_LOCATIONS[city]["lastUpdate"] = t 
            self.ALL_LOCATIONS[city]["lastAccess"] = t
        return self.ALL_LOCATIONS[city]
    
    def getDictFromPoints(self, points):
        for loc in self.ALL_LOCATIONS:
            if self.ALL_LOCATIONS[loc]["gridPoints"] == points:
                return self.ALL_LOCATIONS[loc]

    def updateSingleForecast(self, points):
        dict = self.getDictFromPoints(points)
        return self.updateSingleForecastFromDict(dict)

    def getCustomForecasts(self):
        forecasts = []

        for f in self.ALL_LOCATIONS:
            if self.ALL_LOCATIONS[f]['isUserTracked'] == True:
                forecasts.append(self.ALL_LOCATIONS[f])
        
        return forecasts

    def getMajorCities(self):
        forecasts = []

        for f in self.ALL_LOCATIONS:
            if self.ALL_LOCATIONS[f]['importanceLevel'] == 1:
                forecasts.append(self.ALL_LOCATIONS[f])
        
        return forecasts    
    
    def getMediumCities(self):
        forecasts = []

        for f in self.ALL_LOCATIONS:
            if self.ALL_LOCATIONS[f]['importanceLevel'] == 2:
                forecasts.append(self.ALL_LOCATIONS[f])
        
        return forecasts   
    
    def getSmallCities(self):
        forecasts = []

        for f in self.ALL_LOCATIONS:
            if self.ALL_LOCATIONS[f]['importanceLevel'] == 3:
                forecasts.append(self.ALL_LOCATIONS[f])
        
        return forecasts   

    async def buildForecastsFromList(self, list):
        executor = ThreadPoolExecutor()
        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(executor, self.updateSingleForecastFromDict, f) for f in list]
        return await asyncio.gather(*tasks)
    
    async def buildCustomForecasts(self):
        return await self.buildForecastsFromList(self.getCustomForecasts())

    async def buildMajorForecasts(self):
        return await self.buildForecastsFromList(self.getMajorCities())
    
    async def buildMediumForecasts(self):
        return await self.buildForecastsFromList(self.getMediumCities())
    
    async def buildSmallForecasts(self):
        return await self.buildForecastsFromList(self.getSmallCities())
    
    def isForecastEmpty(self, forecast):
        return bool(not forecast["lastUpdate"])

    async def getOutdatedForecasts(self):
        t = time.time()
        forecasts = []

        for l in self.ALL_LOCATIONS:
            if self.ALL_LOCATIONS[l]["lastUpdate"] == None:
                continue

            if t - self.ALL_LOCATIONS[l]["lastUpdate"] > self.MAX_DELAY:
                forecasts.append(self.ALL_LOCATIONS[l])

        return forecasts
    
    async def getStaleForecasts(self):
        t = time.time()
        forecasts = []

        for l in self.ALL_LOCATIONS:
            if self.ALL_LOCATIONS[l]["lastUpdate"] == None:
                continue

            if t - self.ALL_LOCATIONS[l]["lastUpdate"] > self.MAX_DELAY / 2:
                forecasts.append(self.ALL_LOCATIONS[l])
        
        return forecasts

    async def mergeAndTrim(self, lists, trim): #Merges and trims a list to fit a certain size
        list = lists[0] + lists[1]

        while len(list) >= trim:
            list = list[:-1]
        return list
    
    def shouldRefreshForecast(self, forecast): #RANDOMLY DETERMINES IF A FORECAST SHOULD BE REFRESHED
        if forecast["lastUpdate"] == None:
            return False
        baseChance = float(self.REFRESH_MAX)/self.forecasts
        importanceLevel = forecast['importanceLevel'] / 4 + .5 
        #Base CHANCE = MAX / 6
        timeDecay = (time.time() - forecast["lastUpdate"]) / (self.MAX_DELAY/6)

        chance = baseChance * importanceLevel * timeDecay #0.xx

        num = chance * 100 * 10000 
        rand_num = random.randint(0,10000) #If random number is less than generated num, forecast should be refreshed

        return (num < rand_num)

    async def refreshOlderForecasts(self): #feReturns the forecasts in most need of being refreshed
        max = self.REFRESH_MAX
        tasks = [
            self.getOutdatedForecasts(), self.getStaleForecasts()
        ]
        lists = await asyncio.gather(*tasks)
        lists = await self.mergeAndTrim(lists, max)
        return lists

    def fetchEmptyLocations(self, amount):
        Locs = []

        for f in self.ALL_LOCATIONS:
            if self.isForecastEmpty(self.ALL_LOCATIONS[f]):
                Locs.append(self.ALL_LOCATIONS[f])
                if len(Locs) == amount:
                    break

        return Locs

    async def refreshForecasts(self): #Soft updates forecasts
        refreshed = []
        #FILL EMPTY FORECASTS FIRST
        if self.getPercent() == 0: #ALL FORECASTS are filled 
            refreshed = await self.refreshOlderForecasts()
            for f in self.ALL_LOCATIONS:
                if len(refreshed) == self.REFRESH_MAX:
                    break

                if not f in refreshed and self.shouldRefreshForecast(self.ALL_LOCATIONS[f]):
                    refreshed.append(self.ALL_LOCATIONS[f])

        else: #ALL FORECASTS ARE NOT FILLed
            refreshed = self.fetchEmptyLocations(self.REFRESH_MAX)
            for f in self.ALL_LOCATIONS:
                if len(refreshed) == self.REFRESH_MAX:
                    break

                if not f in refreshed and self.shouldRefreshForecast(self.ALL_LOCATIONS[f]):
                    refreshed.append(self.ALL_LOCATIONS[f])

        return await self.buildForecastsFromList(refreshed), len(refreshed)
    
    async def buildForecasts(self): #BUILDS ALL FORECASTS
        tasks = [
            self.buildSmallForecasts(), self.buildMediumForecasts(), self.buildMajorForecasts(),
        ]

        return await asyncio.gather(*tasks)
            
    def getCities(self):
        self.printStatus(hide=True)
        #print(self.cities)
        return self.cities
    
    def getPrimaryCity(self):
        for loc in self.ALL_LOCATIONS:
            if self.ALL_LOCATIONS[loc]["isPrimary"]:
                return self.ALL_LOCATIONS[loc]
        return 1
    
    def getForecastForPrimaryCity(self):
        return self.getForecastFromDict(self.getPrimaryCity())
    
    def getForecastFromDict(self, dict): 
        if dict["lastUpdate"] == None or (time.time() - dict["lastUpdate"]) > self.MAX_DELAY:
            dict = self.updateSingleForecastFromDict(dict)
        return dict

    async def isDayForLocation(self, location):
        dict = await self.getForecast(location)
        print(dict["hourly"][0])

    async def getForecast(self, city): #Gets Forecast for a city - WRAPPER FUNCTION
        return self.getForecastFromDict(self.ALL_LOCATIONS[city])
    
    async def getForecastsFromListCity(self, list):
        tasks = [self.getForecast(f) for f in list]
        return await asyncio.gather(*tasks)
    
    async def getForecastsFromListDict(self, list):
        tasks = [self.getForecastFromDict(f) for f in list]
        return await asyncio.gather(*tasks)
    
    async def getCustomForecasts(self):
        return await self.getForecastsFromListDict(self.getCustomForecasts())

    async def getMajorForecasts(self):
        return await self.getForecastsFromListDict(self.getMajorCities())
    
    async def getMediumForecasts(self):
        return await self.getForecastsFromListDict(self.getMediumCities())
    
    async def getSmallForecasts(self):
        return await self.getForecastsFromListDict(self.getSmallCities())

    async def getIconFromCity(self, city, hoursOut=0):
        dict = await self.getForecast(city)
        #print(dict["hourly"][hoursOut])
        if dict["hourly"]:
            return await self.getIconFromForecast(dict["hourly"][hoursOut])
        else:
            return None
    
    def matchForecastWithIcon(self, shortForecast : str, isDay):
        #MATCHING FORECASTS
        try: #REMOVE ANYTHING AFTER THEN
            shortForecast = shortForecast[:shortForecast.index("then")]
        except: #Continue if the word then is not present
            a = 1

        try: #REMOVING ANYTHING AFTER LIKELY
                shortForecast = shortForecast[:shortForecast.index("Likely")]
        except:
            a=1 #CONTINUE

        shortForecast = shortForecast.lower()
        shortForecast = shortForecast.strip()

        lightlyRainy = ["light rain", "chance rain showers", "slight chance rain showers", "rain showers", "chance light rain", "isolated rain showers", "slight chance drizzle", "very light rain"]
        rain = ["rain"]
        scatteredRain = ["scattered rain showers"]
        cloudy = ["cloudy"]
        lightlySnowy = ["chance snow showers", "light snow", "slight chance snow showers", "slight chance light snow", "isolated snow showers", "chance light snow"]
        lightSleet = ["chance sleet"]
        snowy = ["snow showers"]
        scatteredSnow = ["scattered snow showers",]
        partlyCovered = ["partly cloudy", "partly sunny"]
        mostlyUncovered = []
        mostlyCovered = ["mostly cloudy"]
        clear = ["sunny", "clear", "mostly clear", "mostly sunny"]
        lightStorms = ["slight chance t-storms", "chance showers and thunderstorms", "slight chance showers and thunderstorms", "isolated showers and thunderstorms"]
        storms = ["showers and thunderstorms", "scattered showers and thunderstorms"]
        smoke = ['areas of smoke']
        frost = ["widespread frost", "areas of frost", "patchy frost"]
        patchyFog = ["patchy fog"]
        fog = ["areas of fog"]
        rainAndSnow = ["chance rain and snow showers", "slight chance rain and snow showers", "rain and snow", "chance rain and snow", "rain and snow showers", "slight chance rain and snow", "scattered rain and snow showers", "isolated rain and snow showers"]
        freezingRain = ["freezing rain"]
    
        if (shortForecast in frost):
            return "Blizzard-BlowingSnow"
        elif (shortForecast == "slight chance light rain"):
            if isDay:
                return "FewShowers"
            else:
                return "FewShowersWorded"
        elif (shortForecast in lightlyRainy):
            return "Drizzle"
        elif (shortForecast in rain):
            return "Rain"
        elif (shortForecast in freezingRain):
            return "FreezingRain"
        elif(shortForecast in scatteredRain):
            if isDay:
                return "ScatteredRainDay"
            else:
                return "ScatteredRainNight"
        elif (shortForecast in cloudy):
            return "Cloudy"
        elif(shortForecast in partlyCovered):
            if isDay:
                return "PartlyCloudyDay"
            else:
                return "PartlyCloudyNight"
        elif(shortForecast in mostlyUncovered):
            if isDay:
                return "FairDay"
            else:
                return "FairNight"
        elif (shortForecast in clear):
            if isDay:
                return "Sunny"
            else:
                return "Clear"
        elif (shortForecast in mostlyCovered):
            if isDay:
                return "MostlyCloudyDay"
            else:
                return "MostlyCloudyNight" 
        elif (shortForecast in lightStorms):
            if isDay:
                return "IsolatedThunderstormsDay"
            else:
                return "IsolatedThunderstormsNight"
        elif (shortForecast in storms):
            if isDay:
                return "ScatteredThunderstormsDay"
            else:
                return "ScatteredThunderstormsNight"  
        elif (shortForecast in rainAndSnow):
            return "RainSnow"
        elif (shortForecast in lightSleet):
            return "Sleet"
        elif (shortForecast in lightlySnowy):
            return "SnowFlurries"
        elif (shortForecast in snowy):
            if isDay:
                return "SnowDay"
            else:
                return "Snow"
        elif (shortForecast in scatteredSnow):
            if isDay:
                return "ScatteredSnowDay"
            else:
                return "ScatteredSnowNight"
        elif (shortForecast in smoke):
            if isDay:
                return "Smoke"
            else:
                return "SmokeNight"  
        elif (shortForecast in patchyFog):
            if isDay:
                return "AMFogPMClouds"
            else:
                return "FoggyConditions"
        elif (shortForecast in fog):
            if isDay:
                return "FoggyConditions"
            else:
                return "FoggyConditions"
        else:
            print("Cannot find icon for " + shortForecast)
            return "NotAvailable"

    async def getIconFromForecast(self, forecast):
        f = forecast["shortForecast"]
        isDay = forecast["isDaytime"]
        icon_token = self.matchForecastWithIcon(f, isDay)
        icon = await getIcon(icon_token)
        return icon

    async def getALLForecasts(self): #Gets all forecasts
        tasks = [
            self.getSmallForecasts(), self.getMediumForecasts(), self.getMajorForecasts(),
        ]

        dict = {}
        a, b, c = await asyncio.gather(*tasks)
        forecasts = a + b + c

        for f in forecasts:
            dict[f["city"]] = f
        return dict
    



"""
async def main():
    TRACKED_LOCATIONS = [[39.6137,-86.1067]]
    cache = ForecastCache(TRACKED_LOCATIONS)
    s = time.time()
    print("Constructing cache")
    await cache.construct()
    e = time.time()
    print("Finished in secondes : " + str(e-s))

    s = time.time()
    print("Refreshing Forecasts")
    await cache.refreshForecasts()
    e = time.time()
    print(" Forecasts refreshed in secondes : " + str(e-s))
    
    cache.printStatus()

    s = time.time()
    print("Refreshing Forecasts")
    await cache.refreshForecasts()
    e = time.time()
    print(" Forecasts refreshed in secondes : " + str(e-s))

    s = time.time()
    print("Refreshing Forecasts")
    await cache.refreshForecasts()
    e = time.time()
    print(" Forecasts refreshed in secondes : " + str(e-s))
    
    s = time.time()
    print("Getting all Forecasts")
    await cache.getALLForecasts()
    e = time.time()
    print("All Forecasts refreshed in secondes : " + str(e-s))

    
    
    return 0


asyncio.run(main())
"""