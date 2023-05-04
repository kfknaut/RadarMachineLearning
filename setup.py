import sys
from cx_Freeze import setup, Executable

build_options = {"packages": ["os"], "excludes": []}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable("main.py", base=base)
]

setup(
    name="Radar Scraper",
    version="0.1",
    description="A Radar Scraper for analyzing Radar Hazards",
    options={"build_exe": build_options},
    executables=executables,
)