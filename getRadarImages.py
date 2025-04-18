import os
from getActiveWatches import getActiveWatches
import requests
from PIL import Image, ImageDraw
from io import BytesIO
from RadarImage import radarImage
import re
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

os.chdir("C:/Users/forev/Downloads/Weather")

CACHE = "C:/Users/forev/OneDrive - Indiana University/Documents/weatherCache"

watches = None

def splitCoords(coord):
    x = float(int(coord[0:4])/100)
    y = float(int(coord[4::])/100)
    if y < 50:
        y+=100
    return [x,y]

def getWatchCoords(watch):
    coordsTemp = watch[1]
    coords = []

    for coord in coordsTemp:
        coord = splitCoords(coord)
        coords.append(coord)

    return coords

def drawWatch(watch, radarImage):
    draw = ImageDraw.Draw(radarImage.image)

    coords = getWatchCoords(watch)
    color = None
    if watch[0] == 'Tornado Watch':
        color = "#C52119"
    else:
        color = "#e0e307"
    shiftedCoords = []
    for coord in coords:
        shiftedCoords.append(radarImage.getCoordPosition(coord))

    #print(shiftedCoords)
    draw.polygon(shiftedCoords, outline=color, width=5)

#Default cache size is 90 (3 hours)
def handleImage(img, folder, cacheFolder, cacheSize = 90):
    files = [f for f in os.listdir(cacheFolder) if os.path.isfile(os.path.join(cacheFolder, f))]
    sorted_files = sorted(files, key=lambda x: int(re.search(r'\d+', x).group()))
    fileNum = len(sorted_files)
    img.image.save(cacheFolder + "/" + str(fileNum) + ".png")

    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    sorted_files = sorted(files, key=lambda x: int(re.search(r'\d+', x).group()))
    
    fileCached = len(sorted_files)
    if fileCached > cacheSize + 1:
        first_file = os.path.join(folder, sorted_files[0])
        os.remove(first_file)
    
    img.image.save(folder + "/" + str(fileNum) + ".png")

def cropImage(img):
    crop_box = (0, 23, 600, 545)
    return img.crop(crop_box)

async def getNationalRadarImage(show=False):
    image = "https://radar.weather.gov/ridge/standard/CONUS-LARGE_0.gif"
    response = requests.get(image)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content)).convert("RGBA")

    boundary = [49.75, 127.08, 21.75, 66]

    radarImg = radarImage(boundary, img, regional=False)
    try:
        watches = getActiveWatches()
    
        for watch in watches:
            drawWatch(watches[watch], radarImg)
    except:
        print("Error loading watches")

    if show:
        radarImg.image.show()
    #radarImg.image.save("annotated_image.png")

    handleImage(radarImg, "Images/national", CACHE + "/national")

    return radarImg

def createRegionalImage(name, boundary): #RETURNS REGIONAL IMAGE
    image = "https://radar.weather.gov/ridge/standard/" + name + "_0.gif"
    response = requests.get(image)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content)).convert("RGBA")
    image = cropImage(img)

    return radarImage(boundary, image, ogImage=img)

def addWatchesToRegionalImage(radarImg):
    watches = getActiveWatches()

    for watch in watches:
        drawWatch(watches[watch], radarImg)
    
    return radarImg

def createCentGrLakes(show):
    #TOP, LEFT, BOTTOM, RIGHT
    boundary = [48.5, 92, 35.5, 77]
    name = "CENTGRLAKES"
    
    radarImg = createRegionalImage(name, boundary)
    
    radarImg = addWatchesToRegionalImage(radarImg)

    if show:
        radarImg.image.show()

    radarImg.merge()
    handleImage(radarImg, "Images/centgrlakes", CACHE + "/centgrlakes")

    return radarImg

def createNorthEast(show):
    name = "NORTHEAST"
    #TOP, LEFT, BOTTOM, RIGHT
    boundary = [48.5, 81, 35.5, 66.5] #TOP MAY NEED TO BE READJUSTED FOR NORTHEAST
    
    radarImg = createRegionalImage(name, boundary)
    

    if show:
        radarImg.image.show()

    radarImg.merge()
    handleImage(radarImg, "Images/northeast", CACHE + "/northeast")

    return radarImg

def createNorthRockies(show):
    name = "NORTHROCKIES"
    #TOP, LEFT, BOTTOM, RIGHT
    boundary = [49.5, 117, 35.5, 100] 

    radarImg = createRegionalImage(name, boundary)
    radarImg = addWatchesToRegionalImage(radarImg)

    radarImg.merge()
    if show:
        radarImg.image.show()

    handleImage(radarImg, "Images/northrockies", CACHE + "/northrockies")

    return radarImg

def createPacNorthWest(show):
    name = "PACNORTHWEST"
    #TOP, LEFT, BOTTOM, RIGHT
    boundary = [49.5, 131, 35.5, 111] #MAY NEED CHANGED - UNTESTED

    radarImg = createRegionalImage(name, boundary)
    radarImg = addWatchesToRegionalImage(radarImg)

    if show:
        radarImg.image.show()

    radarImg.merge()
    handleImage(radarImg, "Images/pacnorthwest", CACHE + "/pacnorthwest")

    return radarImg

def createPacSouthWest(show):
    name = "PACSOUTHWEST"
    #TOP, LEFT, BOTTOM, RIGHT
    boundary = [42.5, 131, 28.5, 111] #MAY NEED CHANGED - UNTESTED

    radarImg = createRegionalImage(name, boundary)
    radarImg = addWatchesToRegionalImage(radarImg)

    if show:
        radarImg.image.show()

    radarImg.merge()
    handleImage(radarImg, "Images/pacsouthwest", CACHE + "/pacsouthwest")

    return radarImg

def createSouthEast(show):
    name = "SOUTHEAST"
    #TOP, LEFT, BOTTOM, RIGHT #131, 42.5
    boundary = [36.5, 91, 23.5, 75] 

    radarImg = createRegionalImage(name, boundary)
    radarImg = addWatchesToRegionalImage(radarImg)

    if show:
        radarImg.image.show()

    radarImg.merge()
    handleImage(radarImg, "Images/southeast", CACHE + "/southeast")

    return radarImg

def createSouthMissVly(show):
    name = "SOUTHMISSVLY"
    #TOP, LEFT, BOTTOM, RIGHT 
    boundary = [38.75, 98, 25.75, 82] 

    radarImg = createRegionalImage(name, boundary)
    radarImg = addWatchesToRegionalImage(radarImg)

    if show:
        radarImg.image.show()

    radarImg.merge()
    handleImage(radarImg, "Images/southmissvly", CACHE + "/southmissvly")

    return radarImg

def createSouthPlains(show):
    name = "SOUTHPLAINS"
    #TOP, LEFT, BOTTOM, RIGHT 
    boundary = [38.5, 108, 25, 92] 

    radarImg = createRegionalImage(name, boundary)
    radarImg = addWatchesToRegionalImage(radarImg)

    if show:
        radarImg.image.show()

    radarImg.merge()
    handleImage(radarImg, "Images/southplains", CACHE + "/southplains")

    return radarImg

def createSouthRockies(show):
    name = "SOUTHROCKIES"
    #TOP, LEFT, BOTTOM, RIGHT 
    boundary = [38.75, 120, 25.75, 102] #UNTESTED

    radarImg = createRegionalImage(name, boundary)
    radarImg = addWatchesToRegionalImage(radarImg)

    if show:
        radarImg.image.show()

    radarImg.merge()
    handleImage(radarImg, "Images/southrockies", CACHE + "/southrockies")

    return radarImg

def createUpperMissVly(show):
    name = "UPPERMISSVLY"
    #TOP, LEFT, BOTTOM, RIGHT 
    boundary = [49.5, 103, 35.5, 89] #UNTESTED

    radarImg = createRegionalImage(name, boundary)
    radarImg = addWatchesToRegionalImage(radarImg)

    if show:
        radarImg.image.show()

    radarImg.merge()
    handleImage(radarImg, "Images/uppermissvly", CACHE + "/uppermissvly")

    return radarImg

#Handles string and creates and returns a regional radar for given region
def createRegionalRadar(region, show):
    f = None
    if region == "centgrlakes":
        f = createCentGrLakes
    elif region == "northeast":
        f = createNorthEast
    elif region == "northrockies":
        f = createNorthRockies
    elif region == "pacnorthwest":
        f = createPacNorthWest
    elif region == "pacsouthwest":
        f = createPacSouthWest
    elif region=="southeast":
        f = createSouthEast
    elif region=="southmissvly":
        f = createSouthMissVly
    elif region=="southplains":
        f = createSouthPlains
    elif region=="southrockies":
        f = createSouthRockies
    elif region=="uppermissvly":
        f = createUpperMissVly
    else:
        return
    
    return f, show #Async reduces time to pull regional radars from 33 seconds to 7.5 seconds

async def getRegionalRadars(show=False):
    executor = ThreadPoolExecutor()
    loop = asyncio.get_running_loop()
    Regions = [
        "centgrlakes",
        "northeast",
        "northrockies",
        "pacnorthwest",
        "pacsouthwest",
        "southeast",
        "southmissvly",
        "southplains",
        "southrockies",
        "uppermissvly"
    ]

    radars = []

    f = [createRegionalRadar(region, show) for region in Regions]
    
    tasks = []

    for r in Regions:
        f = createRegionalRadar(r, show)
        tasks.append(loop.run_in_executor(executor, f[0], f[1]))
    radars = await asyncio.gather(*tasks)

    return radars

def saveRegionalRadar(code, image):

    if not os.path.exists("Images/"+code):
        os.makedirs("Images/"+code)
    if not os.path.exists(CACHE + "/" + code):
        os.makedirs(CACHE + "/" + code)
    handleImage(image, "Images/"+code, CACHE + "/" + code)

async def getImageFromLink(code, show=False):
    link = "https://radar.weather.gov/ridge/standard/" + code + "_0.gif"
    response = requests.get(link)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content)).convert("RGBA")
    
    boundary = [0,0,0,0] #Boundary aren't needed for individual radars because watches won't need to be drawn on them. 

    radarImg = radarImage(boundary, img, regional=False)

    saveRegionalRadar(code, radarImg)

    if show:
        radarImg.image.show()

    
    
    return radarImg


async def getIndividualRadars(list, show=False):

    tasks = [getImageFromLink(radar, show=show) for radar in list]
    
    radars = await asyncio.gather(*tasks)
    
    return radars

        
