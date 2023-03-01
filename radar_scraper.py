import os
import sys
import threading
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from PIL import Image
from datetime import datetime

radar_site = sys.argv[1] 
url = ""

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

    directory = r"E:\RadarDump"
    dir_day = datetime.today().strftime("%m_%d_%Y")

    if not os.path.exists(directory):
        os.makedirs(directory)

    new_date_dir = os.path.join(r"E:\RadarDump",f"{dir_day}")
    if not os.path.exists(new_date_dir):
        os.makedirs(new_date_dir)

    image.save(f"{directory}/{dir_day}/{radar_location}-{radar_layer_name}-{time_stamp}.png")


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

rad_layers = ["N0B", "N0G", "N0C", "DVL"]

for layer in rad_layers:
    run_capture(driver, layer, "radar-image")

# Closes web driver window
driver.quit()
