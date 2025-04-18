from videoPlayer import VideoPlayer
from PIL import Image
import asyncio
from CONFIG import SCREEN_WIDTH, SCREEN_HEIGHT, TRACKED_CAMERAS, ERROR_MESSAGES, DEFAULT_WIDTH, DEFAULT_HEIGHT
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

url = "http://insecam.org/en/view/752899/"
#url = "http://184.167.26.199:8081/mjpg/video.mjpg"

def openUrl(driver, url):
        driver.get(url)
        time.sleep(3)

def getLinkFromInsinsecam(url):
    try:
        options = Options()
        options.page_load_strategy = 'none'
        options.add_argument("--start-minimized") 
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        driver.minimize_window()
        time.sleep(10)
        src = driver.find_element(By.ID, "image0").get_attribute("src")
        width = driver.find_element(By.ID, "image0").get_attribute("width")
        height = driver.find_element(By.ID, "image0").get_attribute("height")
        print()
        print("PAGE")
        print(src)
        driver.close()

        success = bool(src)

        return [src, success, url, width, height]
    
    except:
        if ERROR_MESSAGES:
            print("Error loading " + str(url))
        return[url, False, url, 0, 0]


class WebcamPlayer():
    def __init__(self):
        self.cache = {}
        self.download_dir = os.path.abspath("Temp")
        print(self.download_dir)
        self.images_to_delete = []
        atexit.register(self.clearImageCache)


    async def construct(self):
        tasks = []
        executor = ThreadPoolExecutor()
        loop = asyncio.get_running_loop()

        for camera in TRACKED_CAMERAS:
            tasks.append(loop.run_in_executor(executor, getLinkFromInsinsecam, camera))
        
        links = await asyncio.gather(*tasks)

        for l in links:
            if l[1]:
                self.cache[l[0]] = {"status": "closed", "driver": None, "icUrl" : l[2], "width" : l[3], "height" : int(l[4])}
    
        return self.cache
    
    def onExit(self):
        self.clearImageCache()
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
           
            options.add_argument("--enable-managed-downloads true")
            options.enable_downloads = True
            service = Service()
            
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)
            driver.minimize_window()
            icUrl = None
            width = None
            height = None
            if url in self.cache:
                icUrl = self.cache[url]["icUrl"]
                width = self.cache[url]["width"]
                height = self.cache[url]["height"]

            self.cache[url] = {"status": "open", "driver": driver, "icUrl" : icUrl, "width" : width, "height": height}
            
            return driver
        else:
            return self.cache[url]["driver"]

    def getImageSize(self, driver):
        link = self.getLinkFromDriver(driver)
        print(self.cache[link])
        width = self.cache[link]["width"]
        height = self.cache[link]["height"]
        return {"width" : width, "height" : height}

    def getImageFromDriver(self, driver : webdriver.Chrome):
    
        direct = self.download_dir + "\\" + str(random.randint(0,999999)) + ".png"

        size = self.getImageSize(driver)

        x_off = (DEFAULT_WIDTH - int(size["width"])) / 2
        y_off = (DEFAULT_HEIGHT - int(size["height"])) / 2

        bbox = (x_off - 120, y_off - 100, (int(size["width"])) + x_off + 150, int(size["height"] + 50) + y_off + 35)
        print(bbox)
        driver.get_screenshot_as_file(direct)
        
        return direct

    def getCurrentImageFromWebcam(self, url):
        driver = self.getDriverFromUrl(url)
        image = self.getImageFromDriver(driver)
        
        return image

async def main():
    vPlayer = VideoPlayer()
    wPlayer = WebcamPlayer()
    await wPlayer.construct()
    while True:
        i = wPlayer.getCurrentImageFromWebcam(wPlayer.getLinkFromIcLink(url))
        vPlayer.blit(i, (0,0), resize=True)
        vPlayer.run()
        wPlayer.images_to_delete.append(i)
        time.sleep(0.05)

asyncio.run(main())

