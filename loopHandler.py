import os
import asyncio
from PIL import Image
import random
import cv2
import numpy as np

def sortImageFolder(image_files):
    image_files.sort()
    new_images = []

    for i in image_files:
        new_images.append(str(i) + ".png")
    
    return new_images

def extend(sorted_list):
    random_element = random.randint(0, len(sorted_list))
    return sorted_list[:random_element] + sorted_list[random_element-1:]

def pause(sorted_list):
    return sorted_list + [sorted_list[-1]]

def getGifFromFolder (folder, LOOPS_FOLDER, CURDIR, fps = 45, frames = 90, wait = 30):
    os.chdir(CURDIR)
    
    input_dir = os.path.join(CURDIR, "Images", folder)
    output_path = CURDIR + LOOPS_FOLDER + "/" + folder + ".mp4"

    image_files = [int(file.split('.')[0]) for file in os.listdir(input_dir) if file.endswith(('.png', '.jpg'))]
    image_files = sortImageFolder(image_files)

    images = []
    for idx in image_files:
        img_path = os.path.join(input_dir, idx)  # Assuming PNG; adjust if needed
        img = Image.open(img_path).convert("RGB")
        images.append(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))

    while len(images) < frames:
        images = extend(images)  # Your existing extend logic

    height, width, _ = images[0].shape

    for _ in range(wait):
        images.append(images[-1])
    
    images = images + images

    for i in images[:30]:
        images.append(i)

    #print("len images" + str(len(images)))

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for img in images:
        video.write(img)

    video.release()

    """
    image_files = []
    gif_name = CURDIR + LOOPS_FOLDER + "/" + folder + ".gif"
    for file in os.listdir(CURDIR + "/Images/" + folder):
        image_files.append(int(file[:file.index(".")]))
    image_files = sortImageFolder(image_files)

    images = []
    for image_file in image_files:
        img = Image.open(CURDIR + "/Images/" + folder + "/" + image_file)

        images.append(img)

    while len(images) < frames:
        images = extend(images)
    
    images[0].save(
        gif_name, 
        save_all=True, 
        append_images=images[1:], 
        duration=wait, 
        loop=0
    )
    """
