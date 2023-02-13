from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from PIL import Image
from datetime import datetime

radar_site = "FFC"
radar_layer = "N0B"
url = "https://weather.cod.edu/satrad/nexrad/index.php?parms="+radar_site+"-"+radar_layer+"-0-24-100-usa-rad"

options = webdriver.ChromeOptions()
capabilities = DesiredCapabilities.CHROME
capabilities['acceptInsecureCerts'] = True

#required for the website to know what it is me sending the request
options.add_argument('--user-agent=Radar Request User Agent 1.0, from kfknau2194@ung.edu')
driver = webdriver.Chrome()
driver.set_window_size(1920,1080)
driver.get(url)

#obtains the canvas image, converts it to png
driver.implicitly_wait(10)

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

try:
    # Purposefully false to give wait period, adding canvas causes a blank element to be saved
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "RadarImage")))
except TimeoutException:
    image = crop_screenshot(driver)
else:
    image = crop_screenshot(driver, element)
    
time_stamp =  datetime.now().strftime("%m_%d_%Y-%H_%M_%S")
radar_location = url.split("parms=")[1][:3]
radar_layer_name = ""

if(radar_layer == "N0B"):
    radar_layer_name = "baseRef"
elif (radar_layer == "N0G"):
    radar_layer_name = "baseVel"
elif (radar_layer == "N0C"):
    radar_layer_name = "CC"
elif (radar_layer == "DVL"):
    radar_layer_name = "VIL"

image.save(f"{radar_location}-{radar_layer_name}-{time_stamp}.png")

# Closes web driver window
driver.quit()
