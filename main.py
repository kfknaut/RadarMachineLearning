import os
import sys
import subprocess
from tkinter import *
from PIL import Image, ImageTk

rad_loc = "FFC"
rad_lay = "N0B"

dir_path = "/RadarDump"

subprocess.call(["python", "radar_scraper.py", rad_loc, rad_lay])
