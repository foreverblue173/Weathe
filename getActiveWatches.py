import requests
from bs4 import BeautifulSoup
import time

api_url = "https://api.weather.gov/alerts/active"

params = {

    "event": ["Tornado Watch"]
}
params2 = {
    "event": ["Severe Thunderstorm Watch"]
}

headers = {
    "User-Agent": "YourAppName (your@email.com)"
}

lastChecked = None
watchCache = None
CACHETIME = 60

def remove_non_integers(s):
    return ''.join(char for char in s if char.isdigit())

def getWatchNumberFromDescription(description : str, isTornado):
    description = description.split("\n")
    description = description[0] + " " + description[1] + description[2]
    description = description.upper()
    try:
        description = description[description.index("TORNADO WATCH")::]
    except:
        try:
            description = description[description.index("SEVERE THUNDERSTORM WATCH")::]
        except:
            A = 1
    description = description.split(" ")
    num = 0
    if isTornado:
        num = description[2]
    else:
        num = description[3]

    num = remove_non_integers(num)
    num = int(num)

    return num

def getTextFromWatch(watchNum):
    url = "https://www.spc.noaa.gov/products/watch/wou0" + str(watchNum) + ".html"

    response = requests.get(url)
    response.raise_for_status()  

    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text(separator='\n', strip=True)
    
    text = text[text.index("LAT...LON")::]
    
    text = text[10::]

    text = text.split("\n")
    text = text[0]
    text = text.split(" ")
    return text

def getWatches():
    i=0
    watches = {}
    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()  
    alerts = response.json().get('features', [])

    for alert in alerts:
        properties = alert.get('properties', {})
        event = properties.get('event', 'Unknown Event')
        isTorn = True
        watch_number = getWatchNumberFromDescription(properties.get('description', {}), isTorn)
        if watch_number not in watches:
            watches[watch_number] = event

    response = requests.get(api_url, headers=headers, params=params2)
    response.raise_for_status()  
    alerts = response.json().get('features', [])

    for alert in alerts:
        properties = alert.get('properties', {})
        event = properties.get('event', 'Unknown Event')
        isTorn = False
        watch_number = getWatchNumberFromDescription(properties.get('description', {}), isTorn)
        if watch_number not in watches:
            watches[watch_number] = event
    
    return watches


def formatWatches(watches):
    for watchNum in watches:
        watches[watchNum] = [watches[watchNum], getTextFromWatch(watchNum)]
    return watches

def updateWatches():
    global watchCache
    watches = getWatches()
    watches = formatWatches(watches)
    watchCache = watches

def getActiveWatches():
    global watchCache
    global lastChecked
    global CACHETIME

    if lastChecked == None or lastChecked > CACHETIME:
        updateWatches()
        lastChecked = time.time() #Caching watches reduced time to pull data from 7.5 seconds down to 3 seconds
    
    return watchCache
