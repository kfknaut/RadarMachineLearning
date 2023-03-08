import os
import threading
import subprocess
import tkinter as tk
import configparser
import glob

from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk, ImageChops
from datetime import datetime, timedelta
from tkinter import filedialog

config = configparser.ConfigParser()
section = 'Directories'
key = 'RadarDump'

# Config and database
directory = r"E:\RadarDump"
if not os.path.exists(directory):
    # Database management and configuration
    print("Entering path setup...")
    if not os.path.exists('config.ini'):
        print("Config does not exist, creating one")
        with open('config.ini', 'w') as f:
            config.write(f)

    config.read('config.ini')
    if not config.has_section(section):
        print("Config section does not exist, creating one")
        config.add_section(section)
    directory = config.get(section, key, fallback='')
    if not os.path.exists(directory):
        print("Directory does not exist, asking for one")
        select_file_location()

subirectories = os.listdir(directory)

# Variables for the UI, function of the program
rad_loc = "FFC- Peachtree City, GA"
local_code = rad_loc[:3]
current_city = local_code
code_list = []
last_scan_time = "--:--"
dir_path = "/RadarDump"
delay = 300
countdown = delay + 30
updater = None

layer_options = ["Base Reflectivity","Base Velocity","Correlation Coefficient","Vertically Integrated Liquid"]
layer_options_short = ["baseRef","baseVel","CC","VIL"]
current_layer = layer_options[0]

# Time slider variables
start_time = ""
end_time = ""
            
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

    update_timer(delay + 30)

def select_file_location():
    global directory, config, key,section
    directory = filedialog.askdirectory()
    if directory:
        config.set(section, key, directory)
        with open('config.ini', 'w') as f:
            config.write(f)

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
        countdown = delay + 30
        updater = window.after(0, update_timer, delay + 30)

    else:
        updater = window.after(1000, update_timer, countdown - 1)

def manual_scrape():
    run_scrape()

# Add and remove buttons as well as manually adding FFC to the list first
def add_default_loc():
    if "FFC- Peachtree City, GA" not in selected_list.get(0, END):
        selected_list.insert(END, "FFC- Peachtree City, GA")
        code_list.append("FFC")
    if "Test" not in storm_list.get(0, END):
        storm_list.insert(END, "Test")

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
    if len(code_list) > 1:
        index = code_list.index(current_city)
        index += 1
        index %= len(code_list)
        current_city = code_list[index]
        current_radar_toggle.config(text=current_city)
        update_rad(time_slider.get())
    update_rad(0)
    

def last_city():
    global current_radar_toggle, current_city, code_list
    if len(code_list) > 1:
        index = code_list.index(current_city)
        index -= 1
        index %= len(code_list)
        current_city = code_list[index]
        current_radar_toggle.config(text=current_city)
        update_rad(time_slider.get())

# Toggle layers
def next_layer():
    global current_layer_toggle, current_layer, layer_options
    index = layer_options.index(current_layer)
    index += 1
    index %= len(layer_options)
    current_layer = layer_options[index]
    current_layer_toggle.config(text=current_layer)
    update_rad(time_slider.get())

def last_layer():
    global current_layer_toggle, current_layer, layer_options
    index = layer_options.index(current_layer)
    index += 1
    index %= len(layer_options)
    current_layer = layer_options[index]
    current_layer_toggle.config(text=current_layer)
    update_rad(time_slider.get())

# Storm details button
def storm_details():
    global last_scan_time, loaded_radar,current_city,current_layer,directory, storm_list
    selected_storm = storm_list.curselection()
    if selected_storm:
        detail_window = tk.Toplevel()
        detail_window.title("Storm Details")
        detail_window.geometry("1200x800")
        detail_window.config(bg='#242424')
        detail_window.state('zoomed')

        # Obtain latest radar image
        dt_pattern = f"{directory}/*/{current_city}-{layer_options_short[0]}*"
        dt_files = glob.glob(dt_pattern, recursive=True)
        dt_sorted_files = sorted(dt_files, key=os.path.getctime, reverse=True)
        rad = dt_sorted_files[0]
        dt_photo = ImageTk.PhotoImage(file=rad)

        #----------------------------------- Left side -----------------------------------
        detail_left_frame = tk.Frame(detail_window,bg="#242424")
        detail_left_frame.pack(side=LEFT, padx=10, pady=10)

        #----------------------------------- Radar image -----------------------------------
        detail_image_label = tk.Label(detail_left_frame, image=dt_photo)
        detail_image_label.pack()
        detail_image_label.config(image=dt_photo)
        detail_image_label.image = dt_photo
        #----------------------------------- Below Radar Image -----------------------------------
        detail_base_frame = tk.Frame(detail_left_frame, bg="#242424")
        detail_base_frame.pack(side=tk.BOTTOM,fill=tk.X)

        last_scan_label = tk.Label(detail_base_frame, text=f"Last scan: {last_scan_time}", fg="white", bg="#242424", font=("Arial", 16, "bold"), anchor="w")
        last_scan_label.pack(fill=tk.X, side=tk.LEFT)

        #----------------------------------- Right side -----------------------------------
        detail_right_frame = tk.Frame(detail_window,bg="#242424")
        detail_right_frame.pack(side=LEFT, padx=10, pady=30, fill=BOTH,expand=TRUE)

        dt_direction = tk.Label(detail_right_frame, text="Direction: ",font=("Arial", 16, "bold"),bg='#242424', fg='white',anchor='w')
        dt_direction.pack(fill=X, pady=10)

        dt_speed = tk.Label(detail_right_frame, text="Speed: ",font=("Arial", 16, "bold"),bg='#242424', fg='white',anchor='w')
        dt_speed.pack(fill=X, pady=10)

        dt_life = tk.Label(detail_right_frame, text="Known Storm Lifetime: ",font=("Arial", 16, "bold"),bg='#242424', fg='white',anchor='w')
        dt_life.pack(fill=X, pady=10)

        dt_max_p = tk.Label(detail_right_frame, text="Max precip: ",font=("Arial", 16, "bold"),bg='#242424', fg='white',anchor='w')
        dt_max_p.pack(fill=X, pady=10)

        dt_hazards = tk.Label(detail_right_frame, text="Hazards: ",font=("Arial", 16, "bold"),bg='#242424', fg='white',anchor='w')
        dt_hazards.pack(fill=X, pady=10)

        def back_button():
            detail_window.destroy()
            window.deiconify()

        back_button = tk.Button(detail_window, text='Back', font=("Arial", 16, "bold"), bg="#87CEF6", command=back_button,padx=30,pady=10)
        back_button.pack(pady=40, padx=40, side=BOTTOM)


# Radar image management
def get_layer_imagery(city, layer, offset):
    global directory, loaded_radar, most_recent, prev_img

    pattern = f"{directory}/*/{city}-{layer}*"
    files = glob.glob(pattern, recursive=True)
    sorted_files = sorted(files, key=os.path.getctime, reverse=False)

    if offset <= 0:
        try:
            loaded_radar = sorted_files[offset - 1]
            photo = ImageTk.PhotoImage(file=loaded_radar)
            image_label.config(image=photo)
            image_label.image = photo
            if offset == 0:
                most_recent = image_label.image = photo
            elif offset == 1:
                prev_img = image_label.image = photo
            print(loaded_radar)
        except:
            print("Image not found")

def update_rad(time):
    global current_city, current_layer, layer_options_short, layer_options
    lay_list = layer_options
    index = lay_list.index(current_layer)
    lay = layer_options_short[index]
    time = int(time)
    offset = int (time)
    get_layer_imagery(current_city, lay, offset)

# Radar Location arrays, storm arrays
location_options_full = [
    "ABC- Bethel, AK", "ABR- Aberdeen, SD", "ABX- Albuquerque, NM", "ACG- Biorka Island, AK", "AEC- Nome, AK",
    "AHG- Kenai, AK", "AIH- Middleton Island, AK", "AMX - Miami, FL", "AKC- King Salmon, AK", "AKQ- Wakefield, VA", "AMA- Amarillo, TX", 
    "APD- Fairbanks, AK", "APX- Gaylord, MI", "ARX- La Crosse, WI", 
    "ATX- Seattle, WA", "BBX- Beale AFB, CA","BGM- Binghamton, NY", "BHX- Eureka, CA", "BIS- Bismarck, ND", "BLX- Billings, MT", 
    "BMX- Birmingham, AL", "BOX- Boston, MA", "BRO- Brownsville, TX", "BUF- Buffalo, NY", "BYX- Key West, FL", "CAE- Columbia, SC", 
    "CBW- Caribou, ME", "CBX- Boise, ID", "CCX- State College, PA", "CLE- Cleveland, OH", "CLX- Charleston Air Force Base, SC", "CRI-", 
    "CRP- Corpus Christi, TX", "CXX - Burlington, VT", "CYS- Cheyenne, WY", "DAX- Sacramento, CA","DDC- Dodge City, KS", "DFX- Laughlin Air Force Base, TX", 
    "DGX- Jackson, MS", "DIX - Philadelphia, PA",
    "DLH- Duluth, MN", "DMX- Des Moines, IA", "DOX- Dover Air Force Base, DE", "DTX- Detroit, MI", "DVN- Quad Cities, IA/IL", 
    "DYX- Dyess Air Force Base, TX", "EAX- Kansas City/Pleasant Hill, MO", "EMX- Tuscon, AZ", "ENX- Albany, NY", "EOX- Fort Rucker, AL", 
    "EPZ- El Paso, TX/Santa Teresa, NM", "ESX- Las Vegas, NV", "EVX- Valparaiso/Eglin AFB, FL", 
    "EWX- Austin/San Antonio, TX", "Edwards AFB, CA", "FCX- Blacksburg, VA", "FDR- Frederick, OK", "FDX- Cannon AFB, NM", 
    "FFC- Peachtree City, GA", "FSD- Sioux Falls, SD", "FSX- Flagstaff, AZ", "FTG- Denver/Boulder, CO", "FWS- Dallas/Fort Worth, TX", 
    "GGW- Glasgow, MT", "GJX- Grand Junction, CO", "GLD- Goodland, KS", "GRB- Green Bay, WI", "GRK- Fort Hood, TX", "GRR- Grand Rapids, MI", 
    "GSP- Greenville/Spartanburg, SC", "GWX- Columbus AFB, MS", "GYX- Gray/Portland, ME", "HDX- Holloman AFB, NM", 
    "HGX- Houston/Galveston, TX", "HKI- Honolulu, HI", "HKM- Waimea, HI", "HMO- Maunaloa, HI", "HNX- San Joaquin Valley/Hanford, CA", "HPX- Fort Campbell, KY", 
    "HTX- Huntsville, AL", "HWA- Naalehu, HI", "ICT- Wichita, KS", "ICX- Cedar City, UT", "ILN- Cincinnati/Wilmington, OH", "ILX- Lincoln, IL", 
    "IND- Indianapolis, IN", "INX- Tulsa, OK", "IWA- Phoenix, AZ", "IWX- North Webster, IN", "JAX- Jacksonville, FL", "JGX- Robins Air Force Base, GA", 
    "JKL- Jackson, KY", "LBB- Lubbock, TX", "LCH- Lake Charles, LA", "LGX - Langley Hill, WA", "LIX- New Orleans/Baton Rouge, LA", "LNX - North Platte, NE", 
    "LOT- Chicago, IL", "LRX- ELko, NV", "LSX - St. Louis, MO", "LTX - Wilmington, NC", "LVX - Louisville, KY", "LWX - Sterling, VA", "LZK - Little Rock, AR", 
    "MAF - Midland/Odessa, TX", 
    "MAX- Medford, OR", "MBX - Minot AFB, ND", "MHX - Newport/Morehead City, NC", "MKX - Milwaukee, WI", "MLB - Melbourne, FL", "MOB - Mobile, AL", 
    "MPX- Twin Cities/Chanhassen, MN", "MQT - Marquette, MI", "MRX - Knoxville/Tri-Cities, TN", "MSX - Missoula, MT", "MTX - Salt Lake City, UT", 
    "MUX-  San Francisco, CA", "MVX- Grand Forks, ND", "MXX - Maxwell AFB, AL", "NKX- San Diego, CA", "NQA - Memphis, TN", 
    "OAX- Omaha, NE", "OHX - Nashville, TN", "OKX- Upton, NY", "OTX - Spokane, WA", "PAH - Paducah, KY", "PBZ - Pittsburgh, PA", "PDT - Pendleton, OR", 
    "POE- Fort Polk, LA", "PUX - Pueblo, CO", 
    "RAX- Raleigh, NC", "RGX - Reno, NV", "RIW - Riverton, WY", "RLX - Charleston, WV", "RTX - Portland, OR", 
    "SFX- Pocatello, ID", "SGF- Springfield, MO", "SHV- Shreveport, LA", "SJT- San Angelo, TX", "SOX - Santa Ana Mountains, CA", "SRX- Fort Smith, AR", 
    "TBW- Tampa Bay Area/Ruskin, FL", "TFX- Great Falls, MT", "TLH- Tallahassee, FL", "TLX- Oklahoma City, OK", "TWX- Topeka, KS", 
    "TYX- Fort Drum, NY", "UDX- Rapid City, SD", "UEX- Hastings, NE", "VAX- Moody AFB, GA", "VBX- Vandenberg Air Force Base, CA", 
    "VNX- Vance Air Force Base, OK", "VTX- Los Angeles, CA", "VWX- Evansville, IN", "YUX- Yuma, AZ"
    ]

selected_radars = []
storms = []

#Main UI
window = tk.Tk()
window.title("Radar Scraper")
window.geometry("1200x800")
window.config(bg='#242424')
window.state('zoomed')
window.iconphoto(True,ImageTk.PhotoImage(Image.open('radar.png')))

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

# Toggle city
next_radar_button = tk.Button(base_frame, text="▶", padx=10, pady=20, anchor="w", font=("Arial", 36, "bold"), bg="#87CEF6", height=3, width=1,command=next_city)
next_radar_button.pack(padx=20, pady=20, anchor="e", side="right")

current_radar_toggle = tk.Label(base_frame, text=f"{current_city}", fg="white", bg="#242424", font=("Arial", 16, "bold"), anchor="w")
current_radar_toggle.pack(side="right")

last_radar_button = tk.Button(base_frame, text="◀", padx=10, pady=20, font=("Arial", 36, "bold"), bg="#87CEF6", height=3, width=1, command=last_city)
last_radar_button.pack(padx=20, pady=20, anchor="e", side="right")

# Toggle layer
next_layer_button = tk.Button(base_frame, text="▶", padx=10, pady=20, anchor="w", font=("Arial", 36, "bold"), bg="#87CEF6", height=3, width=1,command=next_layer)
next_layer_button.pack(padx=20, pady=20, anchor="e", side="right")

current_layer_toggle = tk.Label(base_frame, text=f"{current_layer}", fg="white", bg="#242424", font=("Arial", 16, "bold"), anchor="w")
current_layer_toggle.pack(side="right")

last_layer_button = tk.Button(base_frame, text="◀", padx=10, pady=20, font=("Arial", 36, "bold"), bg="#87CEF6", height=3, width=1, command=last_layer)
last_layer_button.pack(padx=20, pady=20, anchor="e", side="right")

#----------------------------------- Right side -----------------------------------
right_frame = tk.Frame(window,bg="#242424")
right_frame.pack(side=LEFT, padx=10, pady=10, fill=BOTH,expand=TRUE)

#----------------------------------- Radar list -----------------------------------
label_text = "Radar"
label = tk.Label(right_frame,text=label_text, fg="white", bg="#242424", font=("Arial", 16, "bold"),anchor="w")
label.pack(fill=X)

r_border = tk.Frame(right_frame, relief="sunken", bg='#E5E5E5')
r_border.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
location_list = tk.Listbox(r_border, height=7, width=20, bg='#E5E5E5', bd=0, highlightthickness=0,font=("Arial", 12))
for location in location_options_full:
    location_list.insert(tk.END, location)

location_list.selection_set(location_options_full.index(rad_loc))
location_list.see(location_options_full.index(rad_loc))

my_scrollbar = tk.Scrollbar(r_border, orient=tk.VERTICAL, command=location_list.yview)
location_list.configure(yscrollcommand=my_scrollbar.set)
my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#location_list.select_set(location_options_full.index("FFC- Peachtree City, GA"))
location_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

#----------------------------------- Selected Radar List -----------------------------------
label_text = "Selected to be scanned"
label = tk.Label(right_frame,text=label_text, fg="white", bg="#242424", font=("Arial", 16, "bold"),anchor="w")
label.pack(fill=X)

sr_border = tk.Frame(right_frame, relief="sunken", bg='#E5E5E5')
sr_border.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
selected_list = tk.Listbox(sr_border, height=7, width=20, bg='#E5E5E5', bd=0, highlightthickness=0,font=("Arial", 12))
for sel in selected_radars:
    sel.insert(tk.END, location)

my_scrollbar = tk.Scrollbar(sr_border, orient=tk.VERTICAL, command=selected_list.yview)
selected_list.configure(yscrollcommand=my_scrollbar.set)
my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
selected_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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

sl_border = tk.Frame(right_frame, relief="sunken", bg='#E5E5E5')
sl_border.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
storm_list = tk.Listbox(sl_border, height=6, width=20, bg='#E5E5E5', bd=0, highlightthickness=0,font=("Arial", 12))
for storm in storms:
    storm.insert(tk.END, location)

my_scrollbar = tk.Scrollbar(sl_border, orient=tk.VERTICAL, command=storm_list.yview)
storm_list.configure(yscrollcommand=my_scrollbar.set)
my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
storm_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Below listboxes
delay_label = tk.Label(right_frame, text="Delay", fg="white", bg="#242424",font=("Arial", 16, "bold"), anchor="w")
delay_label.pack(anchor='w')
delay_options = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
selected_option = tk.StringVar(value=delay_options[4])

def update_delay(*args):
    global delay
    delay = (int(selected_option.get()) * 60) - 60
    print(delay)
selected_option.trace("w", update_delay)

dropdown = ttk.Combobox(right_frame, textvariable=selected_option, values=delay_options,state="readonly",width=5,background="#242424",font=("Arial", 12, "bold"))
dropdown.pack(anchor='w', padx=20)

time_remaining_label = tk.Label(right_frame, text="Time until next scan - --:--", fg="white", bg="#242424",font=("Arial", 16, "bold"))
time_remaining_label.pack()

details_button = tk.Button(right_frame, text="Details",padx=20,pady=10,font=("Arial", 16, "bold"),bg="#87CEF6",command=storm_details)
details_button.pack(side=RIGHT, padx=20, pady= 20)

manual_run_button = tk.Button(right_frame, text="Run", command=manual_scrape,padx=20,pady=10,font=("Arial", 16, "bold"),bg="#87CEF6")
manual_run_button.pack(side=RIGHT, padx=20, pady= 20)

file_select_button = tk.Button(right_frame, text="📁",padx=10,pady=10,font=("Arial", 16, "bold"),bg="#E5E5E5", command=select_file_location)
file_select_button.pack(side=RIGHT, padx=20, pady= 20)

time_slider = tk.Scale(right_frame,from_=-30, to=30, orient=tk.HORIZONTAL, length=600,fg="white", bg="#242424",tickinterval=5,resolution=1, label="Frames",font=("Arial", 12, "bold"),showvalue=False)
time_slider.pack(side=RIGHT,pady=20)
time_slider.config(command=update_rad)

update_rad(time_slider.get())
add_default_loc()
window.mainloop()