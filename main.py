import asyncio
import time
from getRadarImages import getNationalRadarImage, getRegionalRadars, getIndividualRadars
from loopHandler import getGifFromFolder
from createLocalOnthe8s import LocalOnThe8sBuilder, CreateLocalOnThe8s
from Queue import queue
import random
import os
from forecastBuilder import ForecastBuilder
from imageHandler import getAllImages
from videoCache import VideoCache
from forecastCache import ForecastCache
from concurrent.futures import ThreadPoolExecutor

CURDIR = "C:/Users/forev/Downloads/Weather"
os.chdir(CURDIR)

##TODO ADD 1 second pause at end of loop
##TODO Make loading forecasts a lot faster

LOOPS_FOLDER = "/Loops" #TODO CHANGE SO IT USES FULL PATH
ASSETS_FOLDER = CURDIR + "/Assets"
IMAGE_FOLDER = CURDIR + "/Images" #TODO MAKE SO WHOLE PROGRAM USES THIS IMAGE_FOLDER
TRACKED_RADARS = ["KIND", "KMTX"]
TRACKED_LOCATIONS = [[39.6137,-86.1067], [40.7606, -111.8881]] #First city will be primary city
CLEAR_CACHE_ON_START = False
LOCAL_ON_THE_8s_BUILDER = None
FORECAST_CACHE = ForecastCache(TRACKED_LOCATIONS) #Builds the forecast cache

VIDEO_CACHE = None
async def load_video_cache(): #Loads video cache in a function called in main #ALSO CREATES LOCAL ON THE 8s BUILDER
    vc = VideoCache(ASSETS_FOLDER + "/Videos")
    l8 = LocalOnThe8sBuilder(CURDIR, ASSETS_FOLDER, LOOPS_FOLDER, IMAGE_FOLDER, vc)
    return vc, l8

gifs_updated = 0
imageQueue = queue()
image_last_update = None
image_cache = None

async def updateAllRadarImages():
    global imageQueue
    await imageQueue.enqueue()
    print(f"Retrieving radar images")
    start = time.time()

    result_national, result_regional, individual_radars = await asyncio.gather(
        getNationalRadarImage(),
        getRegionalRadars(),
        getIndividualRadars(TRACKED_RADARS)
    )
    end = time.time()
    print(f"Radar images retrieved in {end - start:.2f} seconds")
    await imageQueue.dequeue()
    return [result_national, result_regional, individual_radars]
    
async def createGifs(): #Wrapper function to asyncronously create gifs from folders
    global gifs_updated
    global imageQueue

    executor = ThreadPoolExecutor()
    loop = asyncio.get_running_loop()

    await imageQueue.enqueue()
    gifs_updated = 0
    print(f"Creating Gifs")
    start = time.time()
    folders = [folder for folder in os.listdir(CURDIR + "/Images") if os.path.isdir(os.path.join(CURDIR + "/Images", folder))]
    tasks = [loop.run_in_executor(executor, getGifFromFolder, folder, LOOPS_FOLDER, CURDIR) for folder in folders]
    await asyncio.gather(*tasks)
    end = time.time()
    await imageQueue.dequeue()
    print(f"Gifs created in {end - start:.2f} seconds")

async def updateForecasts(): #Wrapper to update forecasts
    t = time.time()
    print("Updating forecasts")
    await FORECAST_CACHE.refreshForecasts()
    end = time.time()
    print(f"Forecasts refreshed in {end - t:.2f} seconds")

async def updateAllImages(): #Wrapper to update all images
    global image_cache
    global image_last_update

    t = time.time()
    print("Updating all images")
    image_cache = await getAllImages()
    image_last_update = time.time()

    end = time.time()
    print(f"Images updated in {end - t:.2f} seconds")
    return image_cache

async def softUpdateImages():
    global image_cache
    global image_last_update

    if image_last_update - time.time() > 750:
        await updateAllImages()

    return image_cache

async def softUpdateForecasts():

    t = time.time()
    await FORECAST_CACHE.refreshForecasts()

async def softCreateGifs():
    global gifs_updated
    await asyncio.sleep(0)
    if gifs_updated > 2:
        await asyncio.to_thread(createGifs)

async def UpdateRadarImages(interval = 120):
    global gifs_updated
    while True:
        try:
            asyncio.create_task(updateAllRadarImages())
            gifs_updated += 1
        except:
            a = 1
        await asyncio.sleep(interval)

async def UpdateGifs(interval = 300):
    while True:
        try:
            asyncio.create_task(createGifs())
        except:
            a=1 #Continue
        await asyncio.sleep(interval)

async def UpdateForecasts(interval = 240):
    while True:
        try:
            asyncio.create_task(updateForecasts())
        except:
            a=1 #Continue
        await asyncio.sleep(interval)

async def updateImages(interval = 450):
    while True:
        try:
            asyncio.create_task(updateAllImages())
        except:
            a=1 #Continue
        await asyncio.sleep(interval)
        
async def createLocalOnThe8sTask():
    await asyncio.sleep(0)
    await softCreateGifs()
    await softUpdateForecasts()
    await softUpdateImages()
    await CreateLocalOnThe8s(VIDEO_CACHE, FORECAST_CACHE, image_cache)


async def createLocalOnThe8s(interval = 1800):
    while True:
        try:
            asyncio.create_task(createLocalOnThe8sTask())
        except:
            a=1 #Continue
        await asyncio.sleep(interval)
    
    a = 1

async def main():
    global VIDEO_CACHE, LOCAL_ON_THE_8s_BUILDER

    await FORECAST_CACHE.construct()
    VIDEO_CACHE, LOCAL_ON_THE_8s_BUILDER = await load_video_cache()

    tasks = [
        
    ]
    await asyncio.sleep(.5)
    asyncio.create_task(updateImages())
    await asyncio.sleep(.5)
    asyncio.create_task(UpdateRadarImages())
    await asyncio.sleep(.5)
    asyncio.create_task(UpdateGifs())
    await asyncio.sleep(.5)
    asyncio.create_task(UpdateForecasts())
    await asyncio.sleep(.5)
    asyncio.create_task(createLocalOnThe8s())
    #await createLocalOnThe8s()
    #MAIN LOOP
    i = 0
    while True:
        i += 1
        if i % 600 == 0:
            print("Main function is running normally..." + str(i/20))
        await asyncio.sleep(0.05)


asyncio.run(main())

