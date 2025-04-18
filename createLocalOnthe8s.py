import asyncio
import os
from videoCache import VideoCache
import cv2
from forecastCache import ForecastCache
import math
import time
from concurrent.futures import ThreadPoolExecutor

CURDIR = "C:/Users/forev/Downloads/Weather"
ASSETS_FOLDER = CURDIR + "/Assets"
CACHE_FOLDER = ASSETS_FOLDER + "/Cache"
LOOPS_FOLDER = "/Loops"
IMAGE_FOLDER = CURDIR + "/Images"
TRACKED_LOCATIONS = [[39.6137, -86.1067]]

os.chdir(CURDIR)

class LocalOnThe8sBuilder:
    def __init__(self, CUR_DIR, ASSETS_FOLDER, LOOPS_FOLDER, IMAGE_FOLDER, VIDEO_CACHE : VideoCache):
        LOOPS_FOLDER = CUR_DIR + LOOPS_FOLDER #REMOVE THIS LINE WHEN LOOPS FOLDER IS CHANGED TO USE FULL PATH
        self.LOOPS_FOLDER = LOOPS_FOLDER
        self.ASSETS_FOLDER = ASSETS_FOLDER
        self.CUR_DIR = CUR_DIR
        self.IMAGE_FOLDER = IMAGE_FOLDER
        self.VIDEO_CACHE = VIDEO_CACHE
        self.FORECAST_CACHE : ForecastCache = None
        os.chdir(CUR_DIR)

        os.chdir(self.CUR_DIR)

    async def getIntro(self):
        intro = await self.VIDEO_CACHE.pickIntro()
        await self.VIDEO_CACHE.cacheImage(intro, "intro")

    async def buildFrameFromForecast(self):
        return

    async def getCurrentObservationsFrameFromForecast(self, forecast):
        f = forecast["current"]

        h = await self.FORECAST_CACHE.getForecast(f["city"])
        direction = h["hourly"][0]["windDirection"]
        windSpeedMin = h["hourly"][0]["min"]
        windSpeedMax = h["hourly"][0]["max"]
        gusts = h["hourly"][0]["windGust"]
        conditions = h["hourly"][0]["shortForecast"]

        try:
            city = f["city"]
        except:
            print("Error loading observation")
            city = None

        try:
            city = f["city"]
        except:
            print("Error loading observation")
            city = None

        try:
            temp = str(round(f["temperature"]))
        except:
            print("Error loading observation")
            temp = None

        try:  
            dewpoint = str(round(f["dewpoint"]))
        except:
            print("Error loading observation")
            dewpoint = None

        try:
            windChill = str(round(f["windChill"]))
        except:
            #print("Error loading observation")
            windChill = None

        try:
            heatIndex = str(round(f["heatIndex"]))
        except:
            #print("Error loading observation")
            heatIndex = None

        try:
            humidity = str(round(f["humidity"])) + "%"
        except:
            print("Error loading observation")
            humidity = None

        try:
            pressure = str(round(f["surfacePressure"])) + "mb"
        except:
            print("Error loading observation")
            pressure = None

        try:
            visibility = str(round(f["visibility"])) + " miles"
        except:
            print("Error loading observation")
            visibility = None

        return city, temp, dewpoint, windChill, heatIndex, humidity, pressure, visibility, conditions, direction, windSpeedMin, windSpeedMax, gusts

    async def getIconFromShortForecast(self, forecast, FORECAST_CACHE : ForecastCache):
        return await FORECAST_CACHE.getIconFromForecast(forecast)

    """
    async def getLocalForecastFrameFromForecast(self, forecast, icon):
        city = forecast["city"]
        day = forecast["name"]
        #detailedForecast = forecast["detailedForecast"]
        #icon = await self.getIconFromShortForecast(forecast, FORECAST_CACHE)
        video = await self.VIDEO_CACHE.getForecastVideo(city, day, forecast, icon)
        return video
    """
        
    async def buildLocalForecastFrames(self, FORECAST_CACHE : ForecastCache):
        self.FORECAST_CACHE = FORECAST_CACHE
        f = FORECAST_CACHE.getForecastForPrimaryCity()
        await self.getCurrentObservationsFrameFromForecast(f)
        daily_forecasgt = f["default"]
        
        s = time.time()
        print("Creating forecast videos")
        
        tasks = []
        for forecast in daily_forecasgt:
            executor = ThreadPoolExecutor()
            loop = asyncio.get_running_loop()
            icon = await self.getIconFromShortForecast(forecast, FORECAST_CACHE)
            city = forecast["city"]
            day = forecast["name"]
            tasks.append(loop.run_in_executor(executor, self.VIDEO_CACHE.getForecastVideo, city, day, forecast, icon))
            #tasks.append(self.getLocalForecastFrameFromForecast(forecast, FORECAST_CACHE))

        forecasts = await asyncio.gather(*tasks)
        e = time.time()
        print("Created forecast frames in " + str(int(e-s)) + " seconds")
        
        return forecasts
    
    async def getAllHourlyForecastsForCity(self, city, FORECAST_CACHE : ForecastCache):
        #print("Building " + city)
        tasks = [FORECAST_CACHE.getIconFromCity(city, hoursOut=hour) for hour in range(100)]
        await asyncio.gather(*tasks)

    async def testIcons(self, FORECAST_CACHE : ForecastCache):
        print("Building all forecasts")
        await FORECAST_CACHE.buildForecasts()
        print("Finished building")
        cities = FORECAST_CACHE.getCities()
        tasks = [self.getAllHourlyForecastsForCity(city, FORECAST_CACHE) for city in cities]
        await asyncio.gather(*tasks)

        return
    
    async def getLocalObservations(self, FORECAST_CACHE : ForecastCache):
        f = FORECAST_CACHE.getForecastForPrimaryCity()
        self.FORECAST_CACHE = FORECAST_CACHE
        city, temp, dewpoint, windChill, heatIndex, humidity, pressure, visibility, conditions, direction, windSpeedMin, windSpeedMax, gusts = await self.getCurrentObservationsFrameFromForecast(f)
        icon = await FORECAST_CACHE.getIconFromCity(city)
        v = self.VIDEO_CACHE.getObservationVideo(city, temp, dewpoint, windChill, heatIndex, humidity, pressure, visibility, icon, conditions, direction, windSpeedMin, windSpeedMax, gusts)
        return v

async def CreateLocalOnThe8s(VIDEO_CACHE : VideoCache, FORECAST_CACHE : ForecastCache, images):
    l8 = LocalOnThe8sBuilder(CURDIR, ASSETS_FOLDER, LOOPS_FOLDER, IMAGE_FOLDER, VIDEO_CACHE)
    await l8.getIntro()


    tasks = [
        l8.buildLocalForecastFrames(FORECAST_CACHE),
        l8.getLocalObservations(FORECAST_CACHE),
        VIDEO_CACHE.getNationalRadar(),
        VIDEO_CACHE.getRegionalRadars(),
        VIDEO_CACHE.getLocalRadars()
    ]
    
    local, obs, nat, regional, loc = await asyncio.gather(*tasks)
    obs = [obs]
    frames = obs + nat + regional + loc + local
    
    l8.VIDEO_CACHE.combineFrames(frames, ASSETS_FOLDER + "/Videos/ForecastVideos/localForecast.mp4")
    
    #await l8.testIcons(FORECAST_CACHE)

async def main():
    f = ForecastCache(TRACKED_LOCATIONS)
    await f.construct()
    await CreateLocalOnThe8s(f)

#asyncio.run(main())