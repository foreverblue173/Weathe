import os
import time
from moviepy.video.io.VideoFileClip import VideoFileClip
from contextlib import redirect_stdout, redirect_stderr
import random
import asyncio
from datetime import datetime
from imageHandler import getBackground
import time
import cv2
import numpy as np
from CONFIG import CURDIR, ASSETS_FOLDER, DEFAULT_FONT, LOOPS_FOLDER, TRACKED_RADARS
from PIL import Image, ImageFont, ImageDraw


#CACHES
CACHESETTINGS = {
    "intros" : [10000, 10000, False] #accessDecay | int - How long until last accessed until removed - decayTime | int - how long until last updated until removed | bool - should the resources be cached on start
}

def load_videos_from_folder(folder_path, extensions=(".mp4", ".mov", ".avi", ".mkv")):
    video_clips = []
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(extensions):
            full_path = os.path.join(folder_path, filename)
            try:
                with open(os.devnull, "w") as fnull:
                    with redirect_stdout(fnull), redirect_stderr(fnull):
                        clip = VideoFileClip(full_path)
                video_clips.append(clip)
            except Exception as e:
                print(f"Failed to load {filename}: {e}")
    return video_clips

class VideoCache:
    def __init__(self, path):
        start = time.time()
        print("Creating video cache")
        self.path = path

        #Keeps track of backgrounds
        self.backgroundTime = None
        self.background = None
        self.isBackgroundLoading = False

        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v') #VIDEO WRITER

        self.caches = {
            "intros" : [None, None, None], #imageFile, lastAccessed, lastUpdated
        }

        end = time.time()
        print(f"Video cache created in {end - start:.2f} seconds")
    
    async def pickIntro(self): #EXPORT - returns a random intro
        intros = await self.getIntros()
        return random.choice(intros)

    async def getIntros(self):
        c = "intros"
        await self.refreshCache(cache=c)

        if self.checkValidityOfCache(c):
            return self.caches[c][0]
        else:
            self.download(c)
            return self.caches[c][0]
   
    async def download(self, cache):
        path = self.path + "/" + cache

        files = load_videos_from_folder(path)

        self.caches[cache] = [files, time.time(), time.time()]
    
    def clearCache(self, cache):
        self.caches[cache] = [None, None, None]

    async def cacheImage(self, file, name):
        cacheFolder = self.path + "/../Cache/"
        path = cacheFolder + name + ".mp4"
        with open(os.devnull, "w") as fnull:
            with redirect_stdout(fnull), redirect_stderr(fnull):
                file.write_videofile(path, codec='libx264', audio_codec='aac')

    def checkValidityOfCache(self, cache):
        settings = CACHESETTINGS[cache]
        cache = self.caches[cache]

        if cache[0] == None:
            return False
        
        LAT = time.time() - cache[1] #Last Accessed
        LUT = time.time() - cache[2] #Last Updated

        if (LAT > settings[0]) or (LUT > settings[1]):
            return False
        return True

    async def refreshCache(self, cache=None): #Clears cache of last used data
        tasks = []
        #Cache parameter ensures specific cache remains accesible after the cache
        for c in self.caches:
            if c == cache: #Checks if c is targeted cache
                c = self.caches[c]
                if c[0] == None: #If it does not exist, download it
                    tasks.append(self.download(cache))
                else: #Otherwise update access time
                    c[1] = time.time()

            else: #Check if c is not targeted cache
                if not self.checkValidityOfCache(c): #Checks if a cache is not valid anymore
                    self.clearCache(c) #Clears the cache if not

        await asyncio.gather(*tasks)
    
    def getTime(self):
        now = datetime.now()
        seconds_past_midnight = now.hour * 3600 + now.minute * 60 + now.second
        return seconds_past_midnight
    
    def getForecastImageForTime(self, time):
        # Dawn - 4am -> 6am -> 6
        # Sunrise - 6am -> 8am -> 11
        # Morning - 8am -> 11am -> 11
        # MIDDAY - 11am -> 3pm -> 15
        # Evening -3pm -> 6pm -> 17
        # Sunset - 6pm -> 8pm -> 17
        # Dusk - 8pm -> 10pm -> 17
        # Night - 10pm -> 4am -> 17
        # 1920 x 1080

        dawnCount = 6
        sunriseCount = 11
        morningCount = 11
        middayCount = 15
        eveningCount = 17
        sunsetCount = 17
        duskCount = 17
        nightCount = 17

        if time < 14400: #Night - 4am - SECONDS PAST MIDNIGHT
            return "Night" + str(random.randint(1,nightCount))
        elif time < 21600: #Dawn - 6am
            return "Dawn" + str(random.randint(1,dawnCount))
        elif time < 28800: #Sunrise - 8am
            return "Sunrise" + str(random.randint(1,sunriseCount))
        elif time < 39600: #Morning - 11am
            return "Morning" + str(random.randint(1,morningCount))
        elif time < 54000: #Midday - 3pm
            return "Midday" + str(random.randint(1,middayCount))
        elif time < 64800: #Evening - 6pm
            return "Evening" + str(random.randint(1,eveningCount))
        elif time < 72000: #Sunset 8pm
            return "Sunset" + str(random.randint(1,sunsetCount))
        elif time < 79200: #Dusk 10pm
            return "Dusk" + str(random.randint(1,duskCount))
        else: #Night again (10pm - midnight)
            return "Night" + str(random.randint(1,nightCount))
        

    def getForecastBackground(self):
        t = self.getTime() #Time after midnight
        if (self.background == None or ((time.time() - self.backgroundTime) > 1000)) and not (self.isBackgroundLoading):
            self.isBackgroundLoading = True
            self.backgroundTime = time.time()
            image = self.getForecastImageForTime(t)
            image = getBackground(image)
            self.background = image
            self.isBackgroundLoading = False

        while self.isBackgroundLoading:
            #print("waiting on background to load")
            time.sleep(.1)

        return self.background.copy()

    def getVideoFromImage(self, pil_image, path, video_size = (1920, 1080), fps = 30, duration_sec = 5): #Turns a video into an image
        #ALSO SAVES A VIDEO FILE
        pil_image = pil_image.resize(video_size)

        frame = np.array(pil_image)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        output = frame.copy() 
        out = cv2.VideoWriter(path, self.fourcc, fps, video_size)
        for _ in range(fps * duration_sec):
            out.write(output)
        out.release()
        return path

    def openVideo(self, video_path): 
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video file: {video_path}")
        
        return cap

    def blurFrame(self, video_path):
        cap = self.openVideo(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_b{ext}"
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            overlay = frame.copy()
            overlay = cv2.GaussianBlur(overlay, (7, 7), sigmaX=5, sigmaY=3)

            out.write(overlay)
        cap.release()
        out.release()
        return output_path
    
    #BOXES [color, alpha, rect]
    def addOverlayToImage(self, video_path, boxes):
        cap = self.openVideo(video_path)
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_o{ext}"
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            overlay = frame.copy()

            for box in boxes:
                overlay = frame.copy()
                color = box[0]
                alpha = box[1]
                rect = box[2]
                x, y, w, h = rect
                
                cv2.rectangle(overlay, (x, y), (x + w, y + h), color, thickness=-1)

                blended = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

                cv2.rectangle(blended, (x, y), (x + w, y + h), color, thickness=3) #Border
                frame = blended.copy()


            out.write(frame)
        out.release()
        cap.release()
        return output_path

    def delete_file(self, file_path):
        try:
            os.remove(file_path)
            #print(f"File '{file_path}' has been deleted.")
        except FileNotFoundError:
            print(f"The file '{file_path}' does not exist so it could not be deleted")
        except PermissionError:
            print(f"Permission denied to delete '{file_path}'.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def wrap_text(self, text, font, max_width, draw):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]

            if line_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    #BOXES[text, font_size, position, color, font = "FranklinGothic", pos = "center", maxWidth]
    def add_text_to_video(self, video_path, boxes):
        cap = self.openVideo(video_path)

        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_t{ext}"
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        fonts = []
        for box in boxes:
            font_path = ASSETS_FOLDER + "/Fonts/" + box[4] + ".ttf"
            font_size = box[1]
            fonts.append(ImageFont.truetype(font_path, font_size))
        
        #frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_frame)

            i = 0 
            for box in boxes:
                font = fonts[i]
                i += 1
                text = box[0]
                pos = box[5]
                position = box[2]
                color = box[3]
                maxWidth = box[6]

                lines = self.wrap_text(text, font, maxWidth, draw)
                line_height = draw.textbbox((0, 0), "Ay", font=font)[3]

                if pos.lower() == "center":
                    total_text_height = line_height * len(lines)
                    y_start = position[1] - total_text_height // 2
                    x = position[0]
                elif pos.lower() in ("topleft", "topLeft"):
                    y_start = position[1]
                    x = position[0]
                elif pos.lower() in ("topright", "topRight"):
                    y_start = position[1]
                    max_line_width = max(font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines)
                    x = position[0] - max_line_width

                for j, line in enumerate(lines):
                    if pos.lower() == "center":
                        line_width = draw.textbbox((0, 0), line, font=font)[2]
                        line_x = x - line_width // 2
                    else:
                        line_x = x
                    draw.text((line_x, y_start + j * line_height), line, font=font, fill=color)
                
                frame_with_text = cv2.cvtColor(np.array(pil_frame), cv2.COLOR_RGB2BGR)

            out.write(frame_with_text)
            
            """ MAY BE NEEDED IN THE FUTURE?
            frame_count += 1
            if frame_count > duration * fps:  # Stop after a specified duration
                break
            """

        cap.release()
        out.release()
        return output_path

    def add_image_to_video(self, video_path, overlay_img, position, size=None, duration=None):
        cap = self.openVideo(video_path)

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_i{ext}"
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

        if size:
            overlay_img = overlay_img.resize(size)

        max_frames = total_frames if duration is None else int(duration * fps)

        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to PIL image
            frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")

            # Paste overlay image onto frame
            if frame_count < max_frames:
                frame_pil.paste(overlay_img, position, overlay_img)

            # Convert back to OpenCV format
            frame_cv = cv2.cvtColor(np.array(frame_pil.convert("RGB")), cv2.COLOR_RGB2BGR)
            out.write(frame_cv)

            frame_count += 1

        cap.release()
        out.release()
        return output_path
    
    def getForecastVideo(self, city, day, detailedForecast, icon, lenth = 5, sound = False):
        background = self.getForecastBackground()
        path = CURDIR + "/Temp/" + str(random.randint(0,1000000)) + "TempForecast.mp4"
        path = self.getVideoFromImage(background, path)

        #BOXES [color, alpha, rect]
        #x, y, width, height
        overlayBoxes = [
            [(255,255,255), .33, [200,120,1520,70]], #TOP BOX  -> 200 - 1220 - > 1520
            [(255,255,255), .33, [200,190,912,690]], #BOTTOM LEFT BOX | width should be 60% of total width 1520 * .6 -> 912
            [(255,255,255), .33, [1112,190,608,690]], #BOTTOM RIGHT BOX -> 1112 + 304 -> 1416 -> location of image
        ]

        #BOXES[text, font_size, position, color, font = "FranklinGothic", pos = "center", MaxWidth]
        textBoxes = [
            ["Local Forecast", 90, (220, 20), (0,0,0), "FranklinGothicBold", "topLeft", 1500],
            [str(city) + " area", 70, (220, 112), (0,0,0), "FranklinGothic", "topLeft", 1500],
            [str(detailedForecast["temperature"]), 250, (1416, 700), (0,0,0), "FranklinGothicBold", "center", 1500], 
            [str(day), 65, (222, 200), (0,0,0), "FranklinGothic", "topleft", 1500],
            [str(detailedForecast["detailedForecast"]), 55, (222, 275), (0,0,0), "FranklinGothic", "topleft", 870], #MAX WIDTH -> 870
        ]

        path2 = self.addOverlayToImage(path, overlayBoxes) #TOP BOX
        self.delete_file(path)

        path3 = self.add_text_to_video(path2, textBoxes)
        self.delete_file(path2)

        path4 = self.add_image_to_video(path3, icon, (1216,200), size=(400,400))
        self.delete_file(path3)
        
        p = self.blurFrame(path4)
        self.delete_file(path4)

        return p
    
    def getRadarVideo(self, strValue):
        return CURDIR + LOOPS_FOLDER + "/" + strValue + ".mp4"

    def getRadarsFromList(self, list):
        return [self.getRadarVideo(r) for r in list]
    
    async def getRegionalRadars(self):
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
        return self.getRadarsFromList(Regions)

    async def getNationalRadar(self):
        return [self.getRadarVideo("national")]

    async def getLocalRadars(self):
        return self.getRadarsFromList(TRACKED_RADARS)

    def combineFrames(self, paths, output_path, size=(1920, 1080)):
        os.chdir(CURDIR)
        if not paths:
            raise ValueError("No video paths provided.")
        
        caps = [cv2.VideoCapture(path) for path in paths]
        # Get FPS from the first video
        fps = caps[0].get(cv2.CAP_PROP_FPS)

        # Set output video writer with the target size
        width, height = size
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        for cap in caps:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Resize frame if it doesn't match the target size
                if frame.shape[1] != width or frame.shape[0] != height:
                    frame = cv2.resize(frame, (width, height))

                out.write(frame)
            cap.release()

        out.release()

        for path in paths:
            if "/Loops/" not in path:
                self.delete_file(path)


    #BOXES[text, font_size, position, color, font = "FranklinGothic", pos = "center"]
    
    def getObservationVideo(self, city, temp, dewpoint, windChill, heatIndex, humidity, pressure, visibility, icon, conditions, direction, windSpeedMin, windSpeedMax, gusts, lenth = 5, sound = False):
        background = self.getForecastBackground()
        path = CURDIR + "/Temp/" + str(random.randint(0,1000000)) + "test.mp4"
        path = self.getVideoFromImage(background, path)

        #BOXES [color, alpha, rect]
        overlayBoxes = [ #X, y, width, height
            [(255,255,255), .33, [310,120,1240,70]], #TOP BOX
            [(255,255,255), .33, [310,190,440,690]], #BOTTOM LEFT BOX -> width -> 440 
            [(255,255,255), .33, [750,190,800,690]], #BOTTOM RIGHT BOX
        ]

        windText = str(direction) + " " + str(windSpeedMin)

        mult = 104
        offset = 230
        #BOXES[text, font_size, position, color, font = "FranklinGothic", pos = "center", textWidth]
        textBoxes = [
            [str(city), 70, (320, 108), (0,0,0), "FranklinGothic", "topLeft", 1500],
            [str(temp), 240, (530, 730), (0,0,0), "FranklinGothicBold", "center", 1500],
            [str(conditions), 85, (530, 495), (0,0,0), "FranklinGothicBold", "center", 1500],
            [str("HUMIDTY"), 65, (1125, offset + (mult * 0)), (0,0,0), "FranklinGothic", "topRight", 1500],
            [str("DEW POINT"), 65, (1125, offset + (mult * 1)), (0,0,0), "FranklinGothic", "topRight", 1500],
            [str("PRESSURE"), 65, (1125, offset + (mult * 2)), (0,0,0), "FranklinGothic", "topRight", 1500],
            [str("VISIBILITY"), 65, (1125, offset + (mult * 3)), (0,0,0), "FranklinGothic", "topRight", 1500],
            [str("WIND"), 65, (1125, offset + (mult * 4)), (0,0,0), "FranklinGothic", "topRight", 1500],
            [str("GUSTS"), 65, (1125, offset + (mult * 5)), (0,0,0), "FranklinGothic", "topRight", 1500],
            [str(humidity), 95, (1160, offset + (mult * 0)), (0,0,0), "FranklinGothicBold", "topLeft", 1500],
            [str(dewpoint), 95, (1160, offset + (mult * 1)), (0,0,0), "FranklinGothicBold", "topLeft", 1500],
            [str(pressure), 95, (1160, offset + (mult * 2)), (0,0,0), "FranklinGothicBold", "topLeft", 1500],
            [str(visibility), 95, (1160, offset + (mult * 3)), (0,0,0), "FranklinGothicBold", "topLeft", 1500],
            [str(windText), 95, (1160, offset + (mult * 4)), (0,0,0), "FranklinGothicBold", "topLeft", 1500],
            [str(gusts), 95, (1160, offset + (mult * 5)), (0,0,0), "FranklinGothicBold", "topLeft", 1500],   
        ]

        #x, y, width, height
        path2 = self.addOverlayToImage(path, overlayBoxes) #TOP BOX
        self.delete_file(path)

        path3 = self.add_text_to_video(path2, textBoxes)
        self.delete_file(path2)

        #310 + 220 = 530 -> 530-125 = 405
        path4 = self.add_image_to_video(path3, icon, (405,200), size=(250,250))
        self.delete_file(path3)
        
        p = self.blurFrame(path4)

        return p

        #background.show()
        