import os
import sys
import subprocess
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

rad_loc = "FFC"
rad_lay = "N0B"

dir_path = "/RadarDump"

def run_scrape():
    rad_loc = location_menu.get()
    rad_lay = layer_menu.get()

    if(rad_lay == "Base Reflectivity"):
        rad_lay = "N0B"
    elif(rad_lay == "Base Velocity"):
        rad_lay = "N0G"
    elif(rad_lay == "Correlation Coefficient"):
        rad_lay = "N0C"
    elif(rad_lay == "Vertically Integrated Liquid"):
        rad_lay = "DVL"

    subprocess.call(["python", "radar_scraper.py", rad_loc, rad_lay])

window = tk.Tk()

location_options = ["FFC", "BMX"]
layer_options = ["Base Reflectivity","Base Velocity","Correlation Coefficient","Vertically Integrated Liquid"]

location_menu = tk.StringVar(window)
location_menu.set(location_options[0])
location_dropdown = tk.OptionMenu(window, location_menu, *location_options)
location_dropdown.pack()

layer_menu = tk.StringVar(window)
layer_menu.set(layer_options[0])
layer_dropdown = tk.OptionMenu(window, layer_menu, *layer_options)
layer_dropdown.pack()

manual_run_buttpn = tk.Button(window, text="Run", command=run_scrape)
manual_run_buttpn.pack()

window.mainloop()