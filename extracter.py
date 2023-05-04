import re

html = '<option value="ABR">[ABR] Aberdeen</option>                    <option value="ALY">[ALY] Albany</option>                    <option value="ABQ">[ABQ] Albuquerque</option>                    <option value="AMA">[AMA] Amarillo</option>                    <option value="PAFC">[PAFC] Anchorage</option>                    <option value="EWX">[EWX] Austin/San Antonio</option>                    <option value="LWX">[LWX] Baltimore Md/ Washington Dc</option>                    <option value="BYZ">[BYZ] Billings</option>                    <option value="BGM">[BGM] Binghamton</option>                    <option value="BMX">[BMX] Birmingham</option>                    <option value="BIS">[BIS] Bismarck</option>                    <option value="RNK">[RNK] Blacksburg</option>                    <option value="BOI">[BOI] Boise</option>                    <option value="BOX">[BOX] Boston / Norton</option>                    <option value="BRO">[BRO] Brownsville</option>                    <option value="BUF">[BUF] Buffalo</option>                    <option value="BTV">[BTV] Burlington</option>                    <option value="CAR">[CAR] Caribou</option>                    <option value="CHS">[CHS] Charleston</option>                    <option value="RLX">[RLX] Charleston</option>                    <option value="CYS">[CYS] Cheyenne</option>                    <option value="LOT">[LOT] Chicago</option>                    <option value="CLE">[CLE] Cleveland</option>                    <option value="CAE">[CAE] Columbia</option>                    <option value="CRP">[CRP] Corpus Christi</option>                    <option value="FWD">[FWD] Dallas/Fort Worth</option>                    <option value="BOU">[BOU] Denver</option>                    <option value="DMX" SELECTED>[DMX] Des Moines</option>                    <option value="DTX">[DTX] Detroit</option>                    <option value="DDC">[DDC] Dodge City</option>                    <option value="DLH">[DLH] Duluth</option>                    <option value="LKN">[LKN] Elko</option>                    <option value="EPZ">[EPZ] El Paso</option>                    <option value="EKA">[EKA] Eureka</option>                    <option value="PAFG">[PAFG] Fairbanks</option>                    <option value="FGZ">[FGZ] Flagstaff</option>                    <option value="APX">[APX] Gaylord</option>                    <option value="GGW">[GGW] Glasgow</option>                    <option value="GLD">[GLD] Goodland</option>                    <option value="FGF">[FGF] Grand Forks</option>                    <option value="GJT">[GJT] Grand Junction</option>                    <option value="GRR">[GRR] Grand Rapids</option>                    <option value="GYX">[GYX] Gray</option>                    <option value="TFX">[TFX] Great Falls</option>                    <option value="GRB">[GRB] Green Bay</option>                    <option value="GSP">[GSP] Greenville/Spartanburg</option>                    <option value="PGUM">[PGUM] Guam</option>                    <option value="GUM">[GUM] Guam</option>                    <option value="GID">[GID] Hastings</option>                    <option value="PHFO">[PHFO] Honolulu</option>                    <option value="HGX">[HGX] Houston/Galveston</option>                    <option value="HUN">[HUN] Huntsville</option>                    <option value="IND">[IND] Indianapolis</option>                    <option value="JAN">[JAN] Jackson</option>                    <option value="JKL">[JKL] Jackson</option>                    <option value="JAX">[JAX] Jacksonville</option>                    <option value="PAJK">[PAJK] Juneau</option>                    <option value="EAX">[EAX] Kansas City/Pleasant Hill</option>                    <option value="KEY">[KEY] Key West</option>                    <option value="ARX">[ARX] La Crosse</option>                    <option value="LCH">[LCH] Lake Charles</option>                    <option value="VEF">[VEF] Las Vegas</option>                    <option value="ILX">[ILX] Lincoln</option>                    <option value="LZK">[LZK] Little Rock</option>                    <option value="LOX">[LOX] Los Angeles/Oxnard</option>                    <option value="LMK">[LMK] Louisville</option>                    <option value="LUB">[LUB] Lubbock</option>                    <option value="MQT">[MQT] Marquette</option>                    <option value="MFR">[MFR] Medford</option>                    <option value="MLB">[MLB] Melbourne</option>                    <option value="MEG">[MEG] Memphis</option>                    <option value="MFL">[MFL] Miami</option>                    <option value="MAF">[MAF] Midland/Odessa</option>                    <option value="MKX">[MKX] Milwaukee/Sullivan</option>                    <option value="MSO">[MSO] Missoula</option>                    <option value="MOB">[MOB] Mobile</option>                    <option value="MRX">[MRX] Morristown</option>                    <option value="PHI">[PHI] Mount Holly</option>                    <option value="OHX">[OHX] Nashville</option>                    <option value="LIX">[LIX] New Orleans</option>                    <option value="MHX">[MHX] Newport/Morehead City</option>                    <option value="OKX">[OKX] New York</option>                    <option value="OUN">[OUN] Norman</option>                    <option value="IWX">[IWX] Northern Indiana</option>                    <option value="LBF">[LBF] North Platte</option>                    <option value="OAX">[OAX] Omaha / Valley</option>                    <option value="PAH">[PAH] Paducah</option>                    <option value="FFC">[FFC] Peachtree City</option>                    <option value="PDT">[PDT] Pendleton</option>                    <option value="PSR">[PSR] Phoenix</option>                    <option value="PBZ">[PBZ] Pittsburgh</option>                    <option value="PIH">[PIH] Pocatello/Idaho Falls</option>                    <option value="PQR">[PQR] Portland</option>                    <option value="PUB">[PUB] Pueblo</option>                    <option value="DVN">[DVN] Quad Cities Ia</option>                    <option value="RAH">[RAH] Raleigh</option>                    <option value="UNR">[UNR] Rapid City</option>                    <option value="REV">[REV] Reno</option>                    <option value="RIW">[RIW] Riverton</option>                    <option value="STO">[STO] Sacramento</option>                    <option value="SLC">[SLC] Salt Lake City</option>                    <option value="SJT">[SJT] San Angelo</option>                    <option value="SGX">[SGX] San Diego</option>                    <option value="MTR">[MTR] San Francisco</option>                    <option value="HNX">[HNX] San Joaquin Valley/Hanford</option>                    <option value="TJSJ">[TJSJ] San Juan</option>                    <option value="JSJ">[JSJ] San Juan</option>                    <option value="SJU">[SJU] San Juan</option>                    <option value="SEW">[SEW] Seattle</option>                    <option value="SHV">[SHV] Shreveport</option>                    <option value="FSD">[FSD] Sioux Falls</option>                    <option value="OTX">[OTX] Spokane</option>                    <option value="SGF">[SGF] Springfield</option>                    <option value="CTP">[CTP] State College</option>                    <option value="LSX">[LSX] St Louis</option>                    <option value="TAE">[TAE] Tallahassee</option>                    <option value="TBW">[TBW] Tampa Bay Area / Ruskin</option>                    <option value="TOP">[TOP] Topeka</option>                    <option value="TWC">[TWC] Tucson</option>                    <option value="TSA">[TSA] Tulsa</option>                    <option value="MPX">[MPX] Twin Cities/Chanhassen</option>                    <option value="AKQ">[AKQ] Wakefield</option>                    <option value="ICT">[ICT] Wichita</option>                    <option value="ILM">[ILM] Wilmington</option>                    <option value="ILN">[ILN] Wilmington</option>'

# Extract the value using regular expression
airport_codes = re.findall(r"\b[A-Z]{3}\b", html)
print(airport_codes)