import os
import sys
import glob
import numpy as np
import subprocess

from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from PIL import Image, ImageChops
from datetime import datetime

radar_site = sys.argv[1] 
directory = sys.argv[2]
url = ""
most_recent = None
prev_img = None

options = webdriver.ChromeOptions()
capabilities = DesiredCapabilities.CHROME
capabilities['acceptInsecureCerts'] = True

#required for the website to know what it is me sending the request
options.add_argument('--user-agent=Radar Request User Agent 1.0, from kfknau2194@ung.edu')
driver = webdriver.Chrome()
driver.set_window_size(1920,1080)

#obtains the canvas image, converts it to png
driver.implicitly_wait(7.5)

def run_capture(driver, radar_layer, file_name):
    global most_recent, prev_img
    url = "https://weather.cod.edu/satrad/nexrad/index.php?parms="+radar_site+"-"+radar_layer+"-0-24-100-usa-rad"
    driver.get(url)

    try:
        # Purposefully false to give wait period, adding canvas causes a blank element to be saved
        element = WebDriverWait(driver, 7.5).until(EC.presence_of_element_located((By.ID, "RadarImage")))
    except TimeoutException:
        image = crop_screenshot(driver)
    else:
        image = crop_screenshot(driver, element)
    
    time_stamp =  datetime.now().strftime("%m_%d_%Y-%H_%M")
    radar_location = url.split("parms=")[1][:3]
    radar_layer_name = ""

    # check radar layer
    if(radar_layer == "N0B"):
        radar_layer_name = "baseRef"
    elif (radar_layer == "N0G"):
        radar_layer_name = "baseVel"
    elif (radar_layer == "N0C"):
        radar_layer_name = "CC"
    elif (radar_layer == "DVL"):
        radar_layer_name = "VIL"
    elif (radar_layer == "EET"):
        radar_layer_name = "TstmHeight"

    dir_day = datetime.today().strftime("%m_%d_%Y")

    if not os.path.exists(directory):
        os.makedirs(directory)

    new_date_dir = os.path.join(directory,f"{dir_day}")
    if not os.path.exists(new_date_dir):
        os.makedirs(new_date_dir)

    image.save(f"{directory}/{dir_day}/{radar_location}-{radar_layer_name}-{time_stamp}.png")
    check_identical_scan(radar_location, radar_layer_name)

def crop_screenshot(driver, element=None, x=619, y=25, width=900, height=900):
    screenshot = driver.get_screenshot_as_png()
    image = Image.open(BytesIO(screenshot))

    if element :
        location = element.location
        size = element.size
        x = location["x"]
        y = location["y"]
        width = size["width"]
        height = size["height"] 

    image = image.crop((x, y, x + width, y + height))

    return image

# Deletes identical

def check_identical_scan(loc, lay):
    global directory
    pattern = f"{directory}/*/{loc}-{lay}*"
    files = glob.glob(pattern, recursive=True)
    sorted_files = sorted(files, key=os.path.getctime, reverse=True)

    current = Image.open(sorted_files[0])
    previous = Image.open(sorted_files[1])
    cur_arr = np.array(current)
    pre_arr = np.array(previous)

    print(sorted_files[0])
    print(sorted_files[1])
    diff = np.sum(cur_arr != pre_arr)

    if diff == 0:
        os.remove(current.filename)
        print("Duplicate, deleted most recent scan")
    #else:
        #subprocess.call(["python", "storm_identification_main.py"])

rad_layers = ["N0B", "N0G", "N0C", "DVL", "EET"]

for layer in rad_layers:
    run_capture(driver, layer, "radar-image")

# Closes web driver window
driver.quit()
