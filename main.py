import os
import threading
import subprocess
import tkinter as tk
import configparser

from tkinter import *
from PIL import Image, ImageTk
from datetime import datetime, timedelta
from tkinter import filedialog

# Config and database
config = configparser.ConfigParser()
section = 'Directories'
key = 'RadarDump'

# Variables for the UI, function of the program
directory = r"E:\RadarDump"
rad_loc = "FFC- Peachtree City, GA"
local_code = rad_loc[:3]
current_city = local_code
code_list = []
last_scan_time = "--:--"
dir_path = "/RadarDump"
countdown = 330
updater = None

# Time slider variables
start_time = ""
end_time = ""

recent_base = {}
recent_velocity = {}
recent_cc = {}
recent_vil = {}

# Database management and configuratoin
if not os.path.exists('config.ini'):
    with open('config.ini', 'w') as f:
        config.write(f)

config.read('config.ini')
if not config.has_section(section):
    config.add_section(section)
directory = config.get(section, key, fallback='')

if not directory:
    directory = filedialog.askdirectory()
    if directory:
        config.set(section, key, directory)
        with open('config.ini', 'w') as f:
            config.write(f)
            
# UI and Operations
def run_scrape():
    global updater, last_scan_time, start_time,end_time,directory

    last_scan_time = datetime.now().strftime("%H:%M")
    last_scan_label.config(text=f"Last scan time: {last_scan_time}")

    end_time = (datetime.now() - timedelta(minutes=30)).strftime("%H:%M")
    start_time = (datetime.now() + timedelta(minutes=30)).strftime("%H:%M")

    if updater is not None:
        window.after_cancel(updater)

    threads = []
    for radars_to_scan in code_list:
        thread = threading.Thread(target=scan_radar, args=(radars_to_scan,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    update_timer(330)

# Individual thread call
def scan_radar(radars_to_scan):
    subprocess.call(["python", "radar_scraper.py", radars_to_scan, directory])

def update_timer(time_remaining):
    global countdown, updater
    countdown = time_remaining
    minutes = int(countdown / 60)
    seconds = int(countdown % 60)
    time_string = f"Time until next scan - {minutes:02d}:{seconds:02d}"
    time_remaining_label.config(text=time_string)
    
    if(countdown <= 0):
        run_scrape()
        countdown = 330
        updater = window.after(0, update_timer, 330)

    else:
        updater = window.after(1000, update_timer, countdown - 1)

def manual_scrape():
    run_scrape()

# Add and remove buttons as well as manually adding FFC to the list first
def add_default_loc():
    if "FFC- Peachtree City, GA" not in selected_list.get(0, END):
        selected_list.insert(END, "FFC- Peachtree City, GA")
        code_list.append("FFC")

def add_rad_loc():
    global current_city
    selected_radar = location_list.get(ACTIVE)
    if selected_radar not in selected_list.get(0,END):
        if not code_list:
            selected_list.insert(END,selected_radar)
            code_list.append(selected_radar[:3])
            current_city = code_list[0]
            current_radar_toggle.config(text=current_city)
        else:
            selected_list.insert(END,selected_radar)
            code_list.append(selected_radar[:3])

def remove_rad_loc():
    global current_city
    if len(selected_list.curselection()) != 0:
        rem_code = selected_list.get(selected_list.curselection())
        selected_radar = selected_list.curselection()
        if selected_radar:
            selected_list.delete(selected_radar)
            code_list.remove(rem_code[:3])
            if not code_list:
                current_radar_toggle.config(text="N/A")
            else:
                current_city = code_list[0]
                current_radar_toggle.config(text=current_city)

        
# Toggle cities
def next_city():
    global current_radar_toggle, current_city, code_list
    print(current_city)
    if len(code_list) > 1:
        index = code_list.index(current_city)
        index += 1
        index %= len(code_list)
        current_city = code_list[index]
        print(current_city)
        current_radar_toggle.config(text=current_city)

def last_city():
    global current_radar_toggle, current_city, code_list
    print(current_city)
    if len(code_list) > 1:
        index = code_list.index(current_city)
        index -= 1
        index %= len(code_list)
        current_city = code_list[index]
        print(current_city)
        current_radar_toggle.config(text=current_city)

# Radar Location arrays, storm arrays
location_options_full = [
    "ABR- Aberdeen, SD", "ABX- Albany, NY", "ACG- Albany, GA", "AEC- Wichita, KS", "AFC- Anchorage, AK", "AFG- Fairbanks, AK", 
    "AFW- Fort Worth, TX", "AGC- Pittsburgh, PA", "AKQ- Wakefield, VA", "AMA- Amarillo, TX", "APX- Gaylord, MI", "ARX- La Crosse, WI", 
    "ATX- Seattle, WA", "BBX- Binghamton, NY", "BGM- Binghamton, NY", "BHX- Eureka, CA", "BIS- Bismarck, ND", "BLX- Billings, MT", 
    "BMX- Birmingham, AL", "BOX- Boston, MA", "BRO- Brownsville, TX", "BUF- Buffalo, NY", "BYX- Key West, FL", "CAE- Columbia, SC", 
    "CBW- Caribou, ME", "CBX- Great Falls, MT", "CCX- State College, PA", "CLE- Cleveland, OH", "CLX- Charleston, WV", "CRI- Raleigh, NC", 
    "CRP- Corpus Christi, TX", "CXX- Fort Campbell, KY", "DDC- Dodge City, KS", "DFX- Laughlin Air Force Base, TX", "DGX- Honolulu, HI", 
    "DLH- Duluth, MN", "DMX- Des Moines, IA", "DOX- Dover Air Force Base, DE", "DTX- Detroit, MI", "DVN- Quad Cities, IA/IL", 
    "DYX- Dyess Air Force Base, TX", "EAX- Kansas City/Pleasant Hill, MO", "EMX- Elmira, NY", "ENX- Albany, NY", "EOX- Fort Rucker, AL", 
    "EPZ- El Paso, TX/Santa Teresa, NM", "EQX- Tinker Air Force Base, OK", "EVX- Evansville, IN", "EWN- Newport/Morehead City, NC", 
    "EWX- Austin/San Antonio, TX", "FCX- Blacksburg, VA", "FDR- Frederick, OK", "FDX- Grand Forks Air Force Base, ND", 
    "FFC- Peachtree City, GA", "FSD- Sioux Falls, SD", "FSX- Fort Stewart, GA", "FTG- Denver/Boulder, CO", "FWS- Dallas/Fort Worth, TX", 
    "GGW- Glasgow, MT", "GJX- Grand Junction, CO", "GLD- Goodland, KS", "GRB- Green Bay, WI", "GRK- Fort Hood, TX", "GRR- Grand Rapids, MI", 
    "GSP- Greenville/Spartanburg, SC", "GWX- Charleston Air Force Base, SC", "GYX- Gray/Portland, ME", "HDX- Grand Forks, ND", 
    "HGX- Houston/Galveston, TX", "HNX- San Joaquin Valley/Hanford, CA", "HNX- San Joaquin Valley/Hanford, CA", "HPX- Fort Campbell, KY", 
    "HTX- Houston, TX", "HWA- Honolulu, HI", "ICT- Wichita, KS", "ICX- Indianapolis, IN", "ILN- Wilmington, OH", "ILX- Central Illinois", 
    "IND- Indianapolis, IN", "INX- Northern Indiana", "IWA- Phoenix, AZ", "IWX- Northern Indiana", "JAX- Jacksonville, FL", "JGX- Robins Air Force Base, GA", 
    "JKL- Jackson, KY", "JUA- Juneau, AK", "LBB- Lubbock, TX", "LCH- Lake Charles, LA", "LIX- New Orleans/Baton Rouge, LA", "LNX - North Platte, NE", 
    "LOT - Chicago, IL", "LRX - Little Rock, AR", "LSX - St. Louis, MO", "LTX - Wilmington, NC", "LZK - Little Rock, AR", "MAF - Midland/Odessa, TX", 
    "MAX - Medford, OR", "MBX - Memphis, TN", "MHX - Newport/Morehead City, NC", "MKX - Milwaukee, WI", "MLB - Melbourne, FL", "MOB - Mobile, AL", 
    "MPX - Twin Cities/Chanhassen, MN", "MQT - Marquette, MI", "MRX - Knoxville/Tri-Cities, TN", "MSX - Missoula, MT", "MTX - Salt Lake City, UT", 
    "MUX - San Angelo, TX", "MVX - Jackson, MS", "MXX - Fort Drum, NY", "NAX - Nashville, TN", "NQA - Memphis, TN", "OHX - Nashville, TN", 
    "OKX - Upton, NY", "OTX - Spokane, WA", "PAH - Paducah, KY", "PBZ - Pittsburgh, PA", "PDT - Pendleton, OR", "PHI - Mount Holly/Philadelphia, PA", 
    "PIH - Pocatello/Idaho Falls, ID", "PIX - Phoenix, AZ", "PKD - Minot Air Force Base, ND", "PUB - Pueblo, CO", "PUX - Pueblo, CO", 
    "RAX - Roanoke, VA", "RGX - Reno, NV", "RIW - Riverton, WY", "RLX - Charleston, WV", "RTX - Portland, OR", 
    "SFX - San Francisco Bay Area/Monterey, CA", "SGF - Springfield, MO", "SHV - Shreveport, LA", "SOX - Medford, OR", "SRX - Fort Campbell, KY", 
    "TBW - Tampa Bay Area/Ruskin, FL", "TFX - Great Falls, MT", "TLH - Tallahassee, FL", "TLX - Oklahoma City, OK", "TWX - Tyndall Air Force Base, FL", 
    "TYX - Fort Drum, NY", "UDX - Rapid City, SD", "UEX - Hastings, NE", "VAX - Vero Beach, FL", "VBX - Vandenberg Air Force Base, CA", 
    "VNX - Vance Air Force Base, OK", "VTX - Burlington, VT", "VWX - Louisville, KY", "YUX - Montreal, Quebec, Canada"
    ]

location_options = [
    "ABR", "ABX", "ACX", "AEC", "AFX", "AHG", "AIH", "AKQ", "AMA", "AMX", "APX", "ARX", "ATX", "BBX", "BGM", "BHX", 
    "BLX", "BMX", "BOX", "BRO", "BUF", "BYX", "CAE", "CBW", "CBX", "CCX", "CXX", "CYS", "DAX", "DDC", "DFX", "DGX", 
    "DIX", "DLH", "DMX", "DOX", "DTX", "DVN", "DXX", "DYX", "DZX", "EAX", "EMX", "ENX", "EOX", "EPZ", "ESX", "EUX", 
    "EVX", "EYX", "FCX", "FDR", "FDX", "FFC", "FSD", "FSX", "FTG", "FWS", "GGW", "GJX", "GLD", "GRB", "GRR", "GRK", 
    "GSP", "GYX", "HDX", "HGX", "HNX", "HPX", "HTX", "HWC", "ICT", "ICX", "ILN", "ILX", "IND", "INX", "IWA", "IWX", 
    "JAX", "JGX", "JKL", "JUA", "LBB", "LCH", "LGX", "LIX", "LNX", "LOT", "LRX", "LSX", "LTX", "LWX", "AKQ", "ALY", 
    "AMA", "APX", "ARX", "LOT", "ILX", "BMX", "BOX", "FDR", "FFC", "FGF", "MPX", "ABR", "GID", "GGW", "GLD", "GRB", 
    "GRR", "GSP", "LZK", "HGX", "HNX", "ICT", "ILN", "IND", "IWX", "JAX", "LKN", "EAX", "LZK", "LBB", "LCH", "LIX", 
    "LNX", "LOT", "LRX", "LSX", "LTX", "MAF", "MAX", "MBX", "MHX", "MKX", "MLB", "MOB", "MPX", "MQT", "MRX", "MSX", 
    "MTX", "MUX", "MVX", "MXX", "NAX", "NQA", "OHX", "OKX", "OTX", "PAH", "PBZ", "PDT", "PHI", "PIH", "PIX", "PKD", 
    "PUB", "PUX", "RAX", "RGX", "RIW", "RLX", "RTX", "SFX", "SGF", "SHV", "SOX", "SRX", "TBW", "TFX", "TLH", "TLX", 
    "TWX", "TYX", "UDX", "UEX", "VAX", "VBX", "VNX", "VTX", "VWX", "YUX"
    ]

layer_options = ["Base Reflectivity","Base Velocity","Correlation Coefficient","Vertically Integrated Liquid"]
selected_radars = []
storms = []

#Main UI
window = tk.Tk()
window.title("Radar Scraper")
window.geometry("1200x800")
window.config(bg='#242424')
window.state('zoomed')


#----------------------------------- Left side -----------------------------------
left_frame = tk.Frame(window,bg="#242424")
left_frame.pack(side=LEFT, padx=10, pady=10)

#----------------------------------- Radar image -----------------------------------
loaded_radar = tk.PhotoImage(file="testimg.png")
image_label = tk.Label(left_frame, image=loaded_radar)
image_label.pack()

#----------------------------------- Below Radar Image -----------------------------------
base_frame = tk.Frame(left_frame, bg="#242424")
base_frame.pack(side=tk.BOTTOM,fill=tk.X)

last_scan_label = tk.Label(base_frame, text=f"Last scan: {last_scan_time}", fg="white", bg="#242424", font=("Arial", 16, "bold"), anchor="w")
last_scan_label.pack(fill=tk.X, side=tk.LEFT)

next_radar_button = tk.Button(base_frame, text="▶", padx=10, pady=20, anchor="w", font=("Arial", 36, "bold"), bg="#87CEF6", height=3, width=1,command=next_city)
next_radar_button.pack(padx=20, pady=20, anchor="e", side="right")

current_radar_toggle = tk.Label(base_frame, text=f"{current_city}", fg="white", bg="#242424", font=("Arial", 16, "bold"), anchor="w")
current_radar_toggle.pack(side="right")

last_radar_button = tk.Button(base_frame, text="◀", padx=10, pady=20, font=("Arial", 36, "bold"), bg="#87CEF6", height=3, width=1, command=last_city)
last_radar_button.pack(padx=20, pady=20, anchor="e", side="right")

#----------------------------------- Right side -----------------------------------
right_frame = tk.Frame(window,bg="#242424")
right_frame.pack(side=LEFT, padx=10, pady=10, fill=BOTH,expand=TRUE)

#----------------------------------- Radar list -----------------------------------
label_text = "Radar"
label = tk.Label(right_frame,text=label_text, fg="white", bg="#242424", font=("Arial", 16, "bold"),anchor="w")
label.pack(fill=X)

location_list = tk.Listbox(right_frame, height=10, width=20, bg='#E5E5E5', bd=0, highlightthickness=0)
for location in location_options_full:
    location_list.insert(tk.END, location)

location_list.selection_set(location_options_full.index(rad_loc))
location_list.see(location_options_full.index(rad_loc))

my_scrollbar = tk.Scrollbar(location_list, orient=tk.VERTICAL, command=location_list.yview)
location_list.configure(yscrollcommand=my_scrollbar.set)
my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#location_list.select_set(location_options_full.index("FFC- Peachtree City, GA"))
location_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

#----------------------------------- Selected Radar List -----------------------------------
label_text = "Selected to be scanned"
label = tk.Label(right_frame,text=label_text, fg="white", bg="#242424", font=("Arial", 16, "bold"),anchor="w")
label.pack(fill=X)

selected_list = tk.Listbox(right_frame, height=10, width=20, bg='#E5E5E5', bd=0, highlightthickness=0)
for sel in selected_radars:
    sel.insert(tk.END, location)

my_scrollbar = tk.Scrollbar(selected_list, orient=tk.VERTICAL, command=selected_list.yview)
selected_list.configure(yscrollcommand=my_scrollbar.set)
my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
selected_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

button_frame = tk.Frame(right_frame, bg="#242424")
button_frame.pack(side=tk.TOP, fill=tk.X)

remove_button = tk.Button(button_frame, text="Remove",padx=20,pady=10,anchor="w",font=("Arial", 16, "bold"),bg="#87CEF6",command=remove_rad_loc)
remove_button.pack(padx=30, pady= 20, anchor="e", side="right")

add_button = tk.Button(button_frame, text="Add",padx=20,pady=10,font=("Arial", 16, "bold"),bg="#87CEF6",command=add_rad_loc)
add_button.pack(padx=30, pady= 20, anchor="e", side= "right")


#----------------------------------- Storms -----------------------------------
label_text = "Storms"
label = tk.Label(right_frame,text=label_text, fg="white", bg="#242424", font=("Arial", 16, "bold"),anchor="w")
label.pack(fill=X)

storm_list = tk.Listbox(right_frame, height=10, width=20, bg='#E5E5E5', bd=0, highlightthickness=0)
for storm in storms:
    storm.insert(tk.END, location)

my_scrollbar = tk.Scrollbar(storm_list, orient=tk.VERTICAL, command=storm_list.yview)
storm_list.configure(yscrollcommand=my_scrollbar.set)
my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
storm_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

time_remaining_label = tk.Label(right_frame, text="Time until next scan - --:--", fg="white", bg="#242424",font=("Arial", 16, "bold"))
time_remaining_label.pack()

details_button = tk.Button(right_frame, text="Details",padx=20,pady=10,font=("Arial", 16, "bold"),bg="#87CEF6")
details_button.pack(side=RIGHT, padx=30, pady= 20)

manual_run_button = tk.Button(right_frame, text="Run", command=manual_scrape,padx=20,pady=10,font=("Arial", 16, "bold"),bg="#87CEF6")
manual_run_button.pack(side=RIGHT, padx=30, pady= 20)

time_slider = tk.Scale(right_frame,from_=-30, to=30, orient=tk.HORIZONTAL, length=600,fg="white", bg="#242424",tickinterval=6,resolution=6, label="Minutes",font=("Arial", 16, "bold"))
time_slider.pack(side=RIGHT,pady=20)

add_default_loc()
window.mainloop()