#TODO - make configs work
import os

CURDIR = "C:/Users/forev/Downloads/Weather"
os.chdir(CURDIR)

LOOPS_FOLDER = "/Loops" #TODO CHANGE SO IT USES FULL PATH
ASSETS_FOLDER = CURDIR + "/Assets"
IMAGE_FOLDER = CURDIR + "/Images" #TODO MAKE SO WHOLE PROGRAM USES THIS IMAGE_FOLDER
TRACKED_RADARS = ["KIND", "KMTX"]
TRACKED_LOCATIONS = [[39.6137,-86.1067]] #First city will be primary city
DEFAULT_FONT = ASSETS_FOLDER + "/Fonts/FranklinGothic.ttf"
CLEAR_CACHE_ON_START = False
LOCAL_ON_THE_8s_BUILDER = None
ERROR_MESSAGES = True

SCREEN_WIDTH = 1920 / 1.2
SCREEN_HEIGHT = 1080 / 1.2
DEFAULT_WIDTH = 1554
DEFAULT_HEIGHT = 1280

TRACKED_CAMERAS = [
    "http://insecam.org/en/view/239844/",
    "http://insecam.org/en/view/1010711/",
    "http://insecam.org/en/view/885346/",
    "http://insecam.org/en/view/885576/",
    "http://insecam.org/en/view/752899/",
    "http://insecam.org/en/view/1004220/",
    "http://insecam.org/en/view/973842/",
    "http://insecam.org/en/view/911234/",
]