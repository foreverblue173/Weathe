from videoPlayer import VideoPlayer
from PIL import Image
import asyncio
from CONFIG import SCREEN_WIDTH, SCREEN_HEIGHT, TRACKED_CAMERAS, ERROR_MESSAGES, DEFAULT_WIDTH, DEFAULT_HEIGHT, REFRESH_TIME, REFRESH_MODE, TIMEOUT_PERIOD, MULTICAM, CACHE_FOLDER
import pygame
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
import os
import random
import atexit
import keyboard
import pickle

#url = "http://insecam.org/en/view/752899/"
#url = "http://184.167.26.199:8081/mjpg/video.mjpg"

def openUrl(driver, url):
        driver.get(url)
        time.sleep(3)

def getDictFromLinkAndCache(url, cache):
    for l in cache:
        if cache[l]["icUrl"] == url:
            cache[l]["directUrl"] = l
            return cache[l]
    
    return None

def isUrlCached(url, cache):
    return bool(getDictFromLinkAndCache(url, cache))

def getDataFromUrlAndCache(url, cache):
    d = getDictFromLinkAndCache(url, cache)
    if d == None:
        return None
    src = d["directUrl"]
    width = d["width"]
    height = d["height"]
    try:
        isActive = d["isActive"]
    except:
        isActive = True

    return [src, True, url, width, height, isActive]

def getLinkFromInsinsecam(url, cache):
    if not isUrlCached(url, cache):
        try:
            options = Options()
            options.page_load_strategy = 'none'
            options.add_argument("--start-minimized") 
            service = Service()
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)
            driver.minimize_window()
            time.sleep(TIMEOUT_PERIOD)
            src = driver.find_element(By.ID, "image0").get_attribute("src")
            width = driver.find_element(By.ID, "image0").get_attribute("width")
            height = driver.find_element(By.ID, "image0").get_attribute("height")
            #print("PAGE")
            #print(src)
            driver.close()

            success = bool(src)

            return [src, success, url, width, height, True]
        
        except:
            if ERROR_MESSAGES:
                print("Error loading " + str(url))
            return[url, False, url, 0, 0, False]
    else:
        return getDataFromUrlAndCache(url, cache)

def loadCache():
    filename = CACHE_FOLDER + "/linkCache.pkl"

    if os.path.exists(filename):
        with open(filename, "rb") as f:
            data = pickle.load(f)
    else:
        return {} 

    return data

class WebcamPlayer():
    def __init__(self, videoPlayer):
        self.cache = {}
        self.download_dir = os.path.abspath("Temp")
        self.images_to_delete = []

        self.current_image = None
        self.cooldown = REFRESH_TIME

        self.current_image2 = None
        self.cooldown2 = REFRESH_TIME

        self.current_image3 = None
        self.cooldown3 = REFRESH_TIME

        self.current_image4 = None
        self.cooldown4 = REFRESH_TIME

        self.videoPlayer = videoPlayer

        self.mostRecentlyDisplayedImage = None
        self.mostRecentlyDisplayedImage2 = None
        self.mostRecentlyDisplayedImage3 = None
        self.mostRecentlyDisplayedImage4 = None

        self.imageLoadTime = None


    async def construct(self):
        tasks = []
        executor = ThreadPoolExecutor()
        loop = asyncio.get_running_loop()
        asyncio.create_task(self.clearCacheLoop())

        loadedCache = loadCache()

        for camera in TRACKED_CAMERAS:
            tasks.append(loop.run_in_executor(executor, getLinkFromInsinsecam, camera, loadedCache))
        
        links = await asyncio.gather(*tasks)

        newCache = {}

        for l in links:
            if l[1]:
                newCache[l[0]] = {"status": "closed", "driver": None, "icUrl" : l[2], "width" : l[3], "height" : int(l[4]), "isActive" : l[5]}

        loadedCache.update(newCache)
        self.cache = loadedCache

        self.chooseNewCamera()
        atexit.register(self.onExit)
        return self.cache
    
    async def clearCacheLoop(self):
        while True:
            await asyncio.sleep(60)
            self.clearImageCache()

    def saveCache(self): #Saves self.cache so it can be loaded later
        for c in self.cache:
            self.closeCamera(c)
        with open(CACHE_FOLDER + "\\linkCache.pkl", "wb") as f:
            pickle.dump(self.cache, f)

    def onExit(self):
        #Cleans images up
        if self.mostRecentlyDisplayedImage != None:
            self.images_to_delete.append(self.mostRecentlyDisplayedImage)

        if self.mostRecentlyDisplayedImage2 != None:
            self.images_to_delete.append(self.mostRecentlyDisplayedImage2)

        if self.mostRecentlyDisplayedImage3 != None:
            self.images_to_delete.append(self.mostRecentlyDisplayedImage3)

        if self.mostRecentlyDisplayedImage4 != None:
            self.images_to_delete.append(self.mostRecentlyDisplayedImage4)

        self.clearImageCache()
        self.saveCache()

        return

    def clearImageCache(self):
        for i in self.images_to_delete:
            if os.path.exists(i):
                os.remove(i)
        
        self.images_to_delete = []

    def onPageClose(self, url):
        self.cache[url]["status"] = "closed"

    def testPages(self):
        for p in self.cache: #p is url
            if self.cache[p]["status"] == "closed":
                continue

            driver = self.cache[p]["driver"]
            to = 0.1
            toMax = 3
            driver.set_script_timeout = to

            try:
                driver.execute_script("return 1")
                #driver.title
            except:
                self.onPageClose(p)
                
            driver.set_script_timeout = toMax
    
    def findDriverFromIcLink(self, icUrl):

        for i in self.cache:
            if self.cache[i]["icUrl"] == icUrl:
                return self.cache[i]["driver"]
        return None
    
    def getLinkFromIcLink(self, icUrl):
        for i in self.cache:
            if self.cache[i]["icUrl"] == icUrl:
                return i
        return None
    
    def getLinkFromDriver(self, driver):
        for i in self.cache:
            if self.cache[i]["driver"] == driver:
                return i
        return None

    def getDriverFromUrl(self, url):
        if url not in self.cache or self.cache[url]["status"] == "closed":       
            options = webdriver.ChromeOptions()
            options.page_load_strategy = 'none'
            #options.add_argument("--enable-managed-downloads true")
            #options.enable_downloads = True
            service = Service()
            
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)
            driver.set_window_position(-20000, 0)
            icUrl = None
            width = None
            height = None
            isActive = False
            if url in self.cache:
                icUrl = self.cache[url]["icUrl"]
                width = self.cache[url]["width"]
                height = self.cache[url]["height"]
                isActive = self.cache[url]["isActive"]


            self.cache[url] = {"status": "open", "driver": driver, "icUrl" : icUrl, "width" : width, "height": height, "isActive" : isActive}
            driver.minimize_window()
            return driver
        else:
            return self.cache[url]["driver"]

    def getImageSize(self, driver):
        link = self.getLinkFromDriver(driver)
        width = self.cache[link]["width"]
        height = self.cache[link]["height"]
        return {"width" : width, "height" : height}

    def getImageFromDriver(self, driver : webdriver.Chrome):
        #driver.minimize_window()
        direct = self.download_dir + "\\" + str(random.randint(0,999999)) + ".png"

        size = self.getImageSize(driver)

        x_off = (DEFAULT_WIDTH - int(size["width"])) / 2
        y_off = (DEFAULT_HEIGHT - int(size["height"])) / 2

        bbox = (x_off - 120, y_off - 100, (int(size["width"])) + x_off + 150, int(size["height"] + 50) + y_off + 35)
        driver.get_screenshot_as_file(direct)
        
        return direct

    def getCurrentImageFromWebcam(self, url):
        driver = self.getDriverFromUrl(url)
        image = self.getImageFromDriver(driver)
        
        return image
    
    def closeCamera(self, camera):
        driver = self.cache[camera]["driver"]
        if driver != None:
            driver.close()
        self.cache[camera]["driver"] = None
        self.cache[camera]["status"] = "closed"
    
    def pickRandomCamera(self):
        #print(self.cache)
        return random.choice(list(self.cache))

    def chooseNewCamera(self, camera = 1):
        if camera == 1:
            if self.current_image != None:
                self.closeCamera(self.current_image)

            while True: #Functions as a do-while loop
                self.current_image = self.pickRandomCamera()
                if self.current_image not in [self.current_image3, self.current_image2, self.current_image4]:
                    break

            if REFRESH_MODE == "random":
                sigma = 1
                mu = -0.5 * sigma**2  #Ensures mean of ~1

                x = random.lognormvariate(mu, sigma) * REFRESH_TIME
                self.cooldown = time.time() + x
            else:
                self.cooldown = time.time() + REFRESH_TIME

        elif camera == 2:
            if self.current_image2 != None:
                self.closeCamera(self.current_image2)

            while True: #Functions as a do-while loop
                self.current_image2 = self.pickRandomCamera()
                if self.current_image2 not in [self.current_image, self.current_image3, self.current_image4]:
                    break

            if REFRESH_MODE == "random":
                sigma = 1
                mu = -0.5 * sigma**2  #Ensures mean of ~1

                x = random.lognormvariate(mu, sigma) * REFRESH_TIME
                self.cooldown2 = time.time() + x
            else:
                self.cooldown2 = time.time() + REFRESH_TIME

        elif camera == 3:
            if self.current_image3 != None:
                self.closeCamera(self.current_image3)

            while True: #Functions as a do-while loop
                self.current_image3 = self.pickRandomCamera()
                if self.current_image3 not in [self.current_image, self.current_image2, self.current_image4]:
                    break

            if REFRESH_MODE == "random":
                sigma = 1
                mu = -0.5 * sigma**2  #Ensures mean of ~1

                x = random.lognormvariate(mu, sigma) * REFRESH_TIME
                self.cooldown3 = time.time() + x
            else:
                self.cooldown3 = time.time() + REFRESH_TIME

        elif camera == 4:
            if self.current_image4 != None:
                self.closeCamera(self.current_image4)

            while True: #Functions as a do-while loop
                self.current_image4 = self.pickRandomCamera()
                if self.current_image4 not in [self.current_image, self.current_image2, self.current_image3]:
                    break

            if REFRESH_MODE == "random":
                sigma = 1
                mu = -0.5 * sigma**2  #Ensures mean of ~1

                x = random.lognormvariate(mu, sigma) * REFRESH_TIME
                self.cooldown4 = time.time() + x
            else:
                self.cooldown4 = time.time() + REFRESH_TIME

    def displayCurrentCamera(self):
        i = self.getCurrentImageFromWebcam(self.current_image)
        self.videoPlayer.blit(i, (0,0), resize="One")
        if self.mostRecentlyDisplayedImage != None:
            self.images_to_delete.append(self.mostRecentlyDisplayedImage)
        self.mostRecentlyDisplayedImage = i

    async def displayCurrentCameras(self): #Displays all 4 cameras
        if self.current_image == None or time.time() > self.cooldown:
            self.chooseNewCamera(1)

        if self.current_image2 == None or time.time() > self.cooldown2:
            self.chooseNewCamera(2)

        if self.current_image3 == None or time.time() > self.cooldown3:
            self.chooseNewCamera(3)

        if self.current_image4 == None or time.time() > self.cooldown4:
            self.chooseNewCamera(4)
        
        executor = ThreadPoolExecutor()
        loop = asyncio.get_running_loop()
        tasks = []

        tasks.append(loop.run_in_executor(executor, self.getCurrentImageFromWebcam, self.current_image))
        tasks.append(loop.run_in_executor(executor, self.getCurrentImageFromWebcam, self.current_image2))
        tasks.append(loop.run_in_executor(executor, self.getCurrentImageFromWebcam, self.current_image3))
        tasks.append(loop.run_in_executor(executor, self.getCurrentImageFromWebcam, self.current_image4))

        images = await asyncio.gather(*tasks)

        #Camera 1
        i = images[0]
        self.videoPlayer.blit(i, loc="topLeft", resize="Four")
        if self.mostRecentlyDisplayedImage != None:
            self.images_to_delete.append(self.mostRecentlyDisplayedImage)
        self.mostRecentlyDisplayedImage = i

        #Camera 2
        i = images[1]
        self.videoPlayer.blit(i, loc="topRight", resize="Four")
        if self.mostRecentlyDisplayedImage2 != None:
            self.images_to_delete.append(self.mostRecentlyDisplayedImage2)
        self.mostRecentlyDisplayedImage2 = i

        #Camera3
        i = images[2]
        self.videoPlayer.blit(i, loc="bottomLeft", resize="Four")
        if self.mostRecentlyDisplayedImage3 != None:
            self.images_to_delete.append(self.mostRecentlyDisplayedImage3)
        self.mostRecentlyDisplayedImage3 = i

        #Camera4
        i = images[3]
        self.videoPlayer.blit(i, loc="bottomRight", resize="Four")
        if self.mostRecentlyDisplayedImage4 != None:
            self.images_to_delete.append(self.mostRecentlyDisplayedImage4)
        self.mostRecentlyDisplayedImage4 = i

    async def run(self):
        if self.current_image == None or time.time() > self.cooldown:
            self.chooseNewCamera()
        if not MULTICAM:
            self.displayCurrentCamera()
        else:
            await self.displayCurrentCameras()
        
        self.videoPlayer.run()

async def main():
    vPlayer = VideoPlayer()
    wPlayer = WebcamPlayer(vPlayer)
    await wPlayer.construct()
    Running = True
    while Running:
        await wPlayer.run()
        if keyboard.is_pressed('esc'):
            print("Escape key pressed. Exiting...")
            Running = False

asyncio.run(main())
