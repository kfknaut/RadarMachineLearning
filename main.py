import os
import sys
import subprocess
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

rad_loc = "FFC"
rad_lay = "N0B"
dir_path = "/RadarDump"
countdown = 340
updater = None

def run_scrape(rad_loc):
    global updater
    if updater is not None:
        print("CANCEL")
        window.after_cancel(updater)
    subprocess.call(["python", "radar_scraper.py", rad_loc])
    update_timer(340)

def update_timer(time_remaining):
    global countdown, updater
    countdown = time_remaining
    minutes = int(countdown / 60)
    seconds = int(countdown % 60)
    time_string = f"Time until next scan - {minutes:02d}:{seconds:02d}"
    time_remaining_label.config(text=time_string)
    print(time_remaining)
    
    if(countdown <= 0):
        rad_loc = location_list.get(location_list.curselection())
        run_scrape(rad_loc)
        countdown = 340
        updater = window.after(0, update_timer, 340)

    else:
        updater = window.after(1000, update_timer, countdown - 1)

def manual_scrape():
    rad_loc = location_list.get(location_list.curselection())
    run_scrape(rad_loc)
    
# Radar Location arrays, storm arrays

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
    "TWX", "TYX", "UDX", "UEX", "VAX", "VBX", "VNX", "VTX", "VWX", "YUX"]

layer_options = ["Base Reflectivity","Base Velocity","Correlation Coefficient","Vertically Integrated Liquid"]
selected_radars = []
storms =[]

#Main UI
window = tk.Tk()
window.title("Title")
window.geometry("1200x800")
window.config(bg='#242424')
window.state('zoomed')


#Left side
left_frame = tk.Frame(window)
left_frame.pack(side=LEFT, padx=10, pady=10)

#Radar image
loaded_radar = tk.PhotoImage(file="testimg.png")
image_label = tk.Label(left_frame, image=loaded_radar)
image_label.pack()

last_scan = tk.Label(left_frame,text="Last scan: --:--", fg="white", bg="#242424", font=("Arial", 12, "bold"),anchor="w")
last_scan.pack(fill=X)

#Right side
right_frame = tk.Frame(window,bg="#242424")
right_frame.pack(side=LEFT, padx=10, pady=10)

#Radar list
label_text = "Radar"
label = tk.Label(right_frame,text=label_text, fg="white", bg="#242424", font=("Arial", 12, "bold"),anchor="w")
label.pack(fill=X)

location_list = tk.Listbox(right_frame, height=10, width=20, bg='#E5E5E5', bd=0, highlightthickness=0)
for location in location_options:
    location_list.insert(tk.END, location)

location_list.selection_set(location_options.index(rad_loc))
location_list.see(location_options.index(rad_loc))

my_scrollbar = tk.Scrollbar(location_list, orient=tk.VERTICAL, command=location_list.yview)
location_list.configure(yscrollcommand=my_scrollbar.set)
my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
location_list.select_set(location_options.index("FFC"))
location_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

#Selected Radar List
label_text = "Selected to be scanned"
label = tk.Label(right_frame,text=label_text, fg="white", bg="#242424", font=("Arial", 12, "bold"),anchor="w")
label.pack(fill=X)

location_list = tk.Listbox(right_frame, height=10, width=20, bg='#E5E5E5', bd=0, highlightthickness=0)
for location in selected_radars:
    location_list.insert(tk.END, location)

location_list.selection_set(location_options.index(rad_loc))
location_list.see(location_options.index(rad_loc))

my_scrollbar = tk.Scrollbar(location_list, orient=tk.VERTICAL, command=location_list.yview)
location_list.configure(yscrollcommand=my_scrollbar.set)
my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
location_list.select_set(location_options.index("FFC"))
location_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

remove_button = tk.Button(right_frame, text="Remove", command=manual_scrape,padx=20,pady=10)
remove_button.pack(side=RIGHT, padx=30, pady= 20)

#Storms
label_text = "Storms"
label = tk.Label(right_frame,text=label_text, fg="white", bg="#242424", font=("Arial", 12, "bold"),anchor="w")
label.pack(fill=X)

location_list = tk.Listbox(right_frame, height=10, width=20, bg='#E5E5E5', bd=0, highlightthickness=0)
for storm in storms:
    location_list.insert(tk.END, location)

location_list.selection_set(location_options.index(rad_loc))
location_list.see(location_options.index(rad_loc))

my_scrollbar = tk.Scrollbar(location_list, orient=tk.VERTICAL, command=location_list.yview)
location_list.configure(yscrollcommand=my_scrollbar.set)
my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
location_list.select_set(location_options.index("FFC"))
location_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

time_remaining_label = tk.Label(right_frame, text="Time until next scan - --:--", fg="white", bg="#242424",font=("Arial", 12, "bold"))
time_remaining_label.pack()

details_button = tk.Button(right_frame, text="Details", command=manual_scrape,padx=20,pady=10)
details_button.pack(side=RIGHT, padx=30, pady= 20)
manual_run_button = tk.Button(right_frame, text="Run", command=manual_scrape,padx=20,pady=10)
manual_run_button.pack(side=RIGHT, padx=30, pady= 20)


window.mainloop()