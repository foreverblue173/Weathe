#TODO - make configs work
import os


CURDIR =  os.path.dirname(os.path.abspath(__file__)) #Sets current directory as the directory this python file is in
os.chdir(CURDIR)

LOOPS_FOLDER = "/Loops" #TODO CHANGE SO IT USES FULL PATH
ASSETS_FOLDER = CURDIR + "/Assets"
IMAGE_FOLDER = CURDIR + "/Images" #TODO MAKE SO WHOLE PROGRAM USES THIS IMAGE_FOLDER
CACHE_FOLDER = ASSETS_FOLDER + "\\Cache" #Where files are cached

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


#WEBCAM SPECIFIC STUFF
REFRESH_TIME = 1800 #Measured in seconds
REFRESH_MODE = "fixed" #fixed - will always refresh at REFRESH_TIME interval.
                       #random - will refresh at random intervals averaged at REFRESH_TIME
TIMEOUT_PERIOD = 15 #Amount of time that the program will wait for when loading cameras
#Fullscreen doesn't really work yet aorry
MULTICAM = True #Number of cameras to show

DEFAULT_CAMERAS = [
    "http://insecam.org/en/view/239844/", #Stairs in madrid
    "http://insecam.org/en/view/1010711/", #SLC dog park
    "http://insecam.org/en/view/885346/", #Highway in texas
    "http://insecam.org/en/view/885576/", #Another outside thingy i cant see because night
    "http://insecam.org/en/view/752899/", #Montana cabin thingy? It's not really good at night!
    "http://insecam.org/en/view/1004220/", #New york lobby thingy
    "http://insecam.org/en/view/973842/", #New york camera i think it's from the video
    "http://insecam.org/en/view/911234/", #Elevator in new york. I don't think i've ever seen it move
    "http://insecam.org/en/view/692984/", #Another moving camera in japan
    "http://insecam.org/en/view/690922/", #Yet another moving cameria in japan
    "http://insecam.org/en/view/942424/", #Brasil parking garage
    "http://insecam.org/en/view/868454/", #Jaakrta road gate
    "http://insecam.org/en/view/527063/", #NC dog pet thingy
    "http://insecam.org/en/view/150987/", #Portland store
    "http://insecam.org/en/view/511755/", #Waterbury ct clocktower
    "http://insecam.org/en/view/353527/", #Weird  new york thingy
    "http://insecam.org/en/view/692030/", #Moving camera in japan
    "http://insecam.org/en/view/882498/", #Scary russian hallway
    "http://insecam.org/en/view/880541/", #Movable camera in italy
    "http://insecam.org/en/view/891134/", #schizo mexx thingy
    "http://insecam.org/en/view/811506/", #Russia highway
    "http://insecam.org/en/view/891802/", #Place in iran
    "http://insecam.org/en/view/919648/", #Casino chicago
    "http://insecam.org/en/view/373083/", #Rooftop pool in miami
    "http://insecam.org/en/view/400553/", #Office in vietnam
    "http://insecam.org/en/view/442745/",#Marina view camera in spain
    "http://insecam.org/en/view/241072/", #Thinky in russia
    "http://insecam.org/en/view/229/", #Streets in tokyo
    "http://insecam.org/en/view/995986/", #Food place in tokyo
    "http://insecam.org/en/view/628599/", #Bus deopt in chile, good night lighting
    "http://insecam.org/en/view/371870/", #Chicken coop in switzerland
    "http://insecam.org/en/view/1008795/", #Soccer stadium in chile
    "http://insecam.org/en/view/934534/", #Street camera in brazil good night lighting
    "http://insecam.org/en/view/983159/", #Store? in turkey
    "http://insecam.org/en/view/826157/", #Bridge cam of sydney
    "http://insecam.org/en/view/914326/", #Storage closet in iran i think
    "http://insecam.org/en/view/888584/", #Truck bay in brasil
    "http://insecam.org/en/view/857881/", #Solar panels in turkey
    "http://insecam.org/en/view/858482/", #Store in taiwan
    "http://insecam.org/en/view/911230/", #appartment cam in new york
    "http://insecam.org/en/view/241070/", #Chicago play place
    "http://insecam.org/en/view/504141/", #River thing in pennsylvania 
    "http://insecam.org/en/view/237638/", #Pool bar in paris
    "http://insecam.org/en/view/451528/", #Auckland bay
    "http://insecam.org/en/view/258713/", #Lousville religous building. also has funny description
    "http://insecam.org/en/view/970532/", #Bullet trainyard in japan
    "http://insecam.org/en/view/871354/", #Casino in pennsylvania
    "http://insecam.org/en/view/722313/", #Woodworking place in japan
    "http://insecam.org/en/view/402722/", #Place in italy
    "http://insecam.org/en/view/692030/", #Yet another factory in japan
    "http://insecam.org/en/view/689864/", #Another factory in japan
    "http://insecam.org/en/view/748057/", #Spain beach
    "http://insecam.org/en/view/1010777/", #Cool solar panels in japan
    "http://insecam.org/en/view/1010735/", #More cool solar panels in japan
    "http://insecam.org/en/view/1010634/", #Solar panels
    "http://insecam.org/en/view/1004889/", #Car place in italy
    "http://insecam.org/en/view/813979/", #Church in indianapolis
    "http://insecam.org/en/view/391312/", #Parking lot in minneapolis
    "http://insecam.org/en/view/798093/", #Lake in norway
    "http://insecam.org/en/view/423527/", #stairwell thingy in mankato
    "http://insecam.org/en/view/849718/", #Camera at college in mankato
    "http://insecam.org/en/view/1010690/", #Evansville bridge
    "http://insecam.org/en/view/817622/", #Stoplight in tennesee
    "http://insecam.org/en/view/768708/", #Bridge in alabama
    "http://insecam.org/en/view/744797/", #Gazebo in ohio
    "http://insecam.org/en/view/738706/", #Street in greenwich
    "http://insecam.org/en/view/723208/", #Moving camera in baltimore
    "http://insecam.org/en/view/571014/", #Hallway in NY
    "http://insecam.org/en/view/571017/", #Hallway in NY
    "http://insecam.org/en/view/856159/", #Greenwood village in denver intersection 
]

TRACKED_CAMERAS = [
    "", #Add links here
]

TRACKED_CAMERAS = TRACKED_CAMERAS + DEFAULT_CAMERAS #COMMENT OUT THIS LINE TO ONLY USE CUSTOM CAMERAS