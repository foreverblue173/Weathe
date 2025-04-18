import asyncio
import requests
import aiohttp
from PIL import Image
from io import BytesIO
from CONFIG import ASSETS_FOLDER

async def getImageFromLink(link, code):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                if response.status == 200:
                    content = await response.read()
                    image = Image.open(BytesIO(content))
                    return [image, code]
    except:
        print("Error downloading image")
        return None

def convertListToDict(list):
    retDict = {}

    for i in list:
        try:
            retDict[i[1]] = i[0]
        except:
            continue
   
    return retDict

async def getImagesFromLinks(links, base = "https://www.spc.noaa.gov/", extension = ".gif"): #Wrapper to async pull multiple images from 

    tasks = [getImageFromLink(base + link + extension, link) for link in links]
    
    images = await asyncio.gather(*tasks)
    images = convertListToDict(images)

    return images
        
async def getIcon(icon) -> Image:
    icon_path = ASSETS_FOLDER + "/Images/Icons/" + icon + ".png"

    image = Image.open(icon_path)
    return image

def getBackground(background):
    background_path = ASSETS_FOLDER + "/Images/Backgrounds/" + background + ".jpg"
    image = Image.open(background_path)
    return image.copy()

async def getOutLook():
    outlooks = ["day1otlk", "day2otlk", "day3otlk"]
    images = await getImagesFromLinks(outlooks, base="https://www.spc.noaa.gov/products/outlook/")

    return images

async def getWatches():
    link = "https://www.spc.noaa.gov/products/watch/validww.png"
    code = "validww"
    l = await getImageFromLink(link, code)

    try:
        return convertListToDict([l])
    except:
        return None
        
async def getMDs():
    link = "https://www.spc.noaa.gov/products/md/validmd.png"
    code = "validmd"
    l = await getImageFromLink(link, code)

    try:
        return convertListToDict([l])
    except:
        return None
        
async def getStormReports():
    reports = ["reports/today", "reports/yesterday"]
    images = await getImagesFromLinks(reports, base="https://www.spc.noaa.gov/climo/")

    return images

async def getHazards():
    link = "https://www.weather.gov/wwamap/png/US.png"
    code = "hazards"
    l = await getImageFromLink(link, code)

    try:
        return convertListToDict([l])
    except:
        return None
        
async def getTemperatures():
    reports = ["MaxT1_conus", "MaxT1_conus"]
    images = await getImagesFromLinks(reports, base="https://graphical.weather.gov/images/conus/", extension=".png")

    return images

async def totalForecast():
    link = "http://www.wpc.ncep.noaa.gov//noaa/noaa.gif"
    code = "forecast"
    l = await getImageFromLink(link, code)

    try:
        return convertListToDict([l])
    except:
        return None
        
async def getHurricanes():
 
    hurricane_maps = ["atl/tafb_atl", "epac/tafb_epac"]
    images = await getImagesFromLinks(hurricane_maps, base="https://www.nhc.noaa.gov/overview_", extension="_graphics.png")

    return images

async def getAllImages():
    images = {}

    tasks = [getOutLook(), getWatches(), getMDs(), getStormReports(), getHazards(), getTemperatures(), totalForecast(), getHurricanes()]

    outlooks, watches, MDs, reports, hazards, temps, forecast, hurricanes = await asyncio.gather(*tasks)

    try:
        images.update(outlooks)
    except:
        a=1
    try:
        images.update(watches)
    except:
        a=1
    try:
        images.update(MDs)
    except:
        a=1
    try:
        images.update(reports)
    except:
        a=1
    try:
        images.update(hazards)
    except:
        a=1
    try:
        images.update(temps)
    except:
        a=1
    try:
        images.update(forecast)
    except:
        a=1
    try:
        images.update(hurricanes)
    except:
        a=1

    return images

async def main():
    await getAllImages()

#asyncio.run(main())