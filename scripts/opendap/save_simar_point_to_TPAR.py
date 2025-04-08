############################
# 14/02/2025 by @laloyo
# downloads according to day and domain specific input simar data
# NOTE: activate the virtual env (utm_env). the bash script activates it
############################
import os
import utm
import pandas as pd
import xarray as xr
import sys
from datetime import date, datetime, timezone, timedelta

def read_cgrid(input_file):
    with open(input_file, 'r') as f:
        for line in f:
            if line.startswith("CGRID"):
                parts = line.split()
                easting = float(parts[1])
                northing = float(parts[2])
                xlen = float(parts[4])
                ylen = float(parts[5])
                nx = int(parts[6]) + 1
                ny = int(parts[7]) + 1
                return easting, northing, xlen, ylen, nx, ny
    return None
def utm_to_lanlot(easting, northing, xlen, ylen):
    easting_min, easting_max = easting, easting + xlen
    northing_min, northing_max = northing, northing + ylen

    lat_min, lon_min = utm.to_latlon(easting_min, northing_min, 31, 'S')
    lat_max, lon_max = utm.to_latlon(easting_max, northing_max, 31, 'S')

    return lat_min, lat_max, lon_min, lon_max
#TODO: define lat and lon sima rpoint based on INPUT.swn file. it's difficult to think about any space in mallorca. maybe this shouldn't be automatized for any domain
def download_simar_point(case_name, lat, lon):

    base_url = "http://opendap.puertos.es/thredds/dodsC/wave_regional_bal/{year}/{month:02d}/"

    # extract day
    today = datetime.now(timezone.utc)
    #print("Today date is: ", today)

    # creating available FC names
    start_date1 = today - timedelta(days=2)
    start_date2 = today - timedelta(days=1)
    
    #generate timestamps (00 and 12 UTC)
    time_stamps = ["00", "12"]

    # saving directory
    time_dir = today.strftime("%Y%m") #we change timedir to the day of the simulation
    case_name = sys.argv[1] if len(sys.argv) > 1 else "default_case"
    save_dir = f"./cases/{case_name}/input/simar/point/{time_dir}"
    os.makedirs(save_dir, exist_ok=True)
    # Construct filenames based on observed pattern
    file_names = []
    for start_date in [start_date1, start_date2]:
        for ts in time_stamps:
            # base time
            base_str = start_date.strftime("%Y%m%d") + ts  # Base timestamp
            # start time
            start_hour = int(ts) + 1
            start_str = start_date.strftime("%Y%m%d") + f"{start_hour:02d}"
            # end time
            end_str = (start_date + timedelta(days=3)).strftime("%Y%m%d") + ts

            # url_path
            file_name = f"HW-{start_str}-{end_str}-B{base_str}-FC.nc"
            file_url = base_url.format(year=start_date.year, month=start_date.month) + file_name
            save_path = os.path.join(save_dir, f"TPAR_HW-{start_str}-{end_str}-B{base_str}-FC_point_{lat}_{lon}.txt")

            # check if file is already downloaded
            if os.path.exists(save_path):
                print(f"File already exists, skipping: {save_path}")
                continue  # Skip to the next iteration
                
            # start downloading
            print(f"Accessing: {file_url}")

            try:
                # Open dataset
                ds = xr.open_dataset(file_url)

                # Select only specific variables
                # spectral HS, wave per at spec dens max (RTpeak creo), peak wave dir
                vars = ds[["VHM0", "VTPK", "VPED"]]

                # specify point
                point_data = vars.sel(latitude=lat, longitude=lon, method="nearest")
                
                df = point_data.to_dataframe().reset_index()
                # Save only selected variables to TPAR
                df["Timestamp"] = df["time"].dt.strftime("%Y%m%d.%H%M%S")
                df["Desv_dir"] = 20. # assuming directional spread is always 20
                df = df[["Timestamp", "VHM0", "VTPK", "VPED", "Desv_dir"]]
                # save TPAR
                with open(save_path, "w") as f:
                    f.write("TPAR\n")
                    df.to_csv(f, sep=" ", index=False, header=False, float_format="%.3f")

                print(f"TPAR file saved successfully as {save_path}")

            except Exception as e:
                print(f"Error downloading dataset: {e}")

    print("Download process completed.")
# command-line arguments given in bash script
if len(sys.argv) < 4:
    print("Usage: python save_simar_point_to_TPAR.py <case_name> <latitude> <longitude>")
    sys.exit(1)

case_name = sys.argv[1]
latitude = float(sys.argv[2])
longitude = float(sys.argv[3])

#download_simar_point(lat=39.82211604, lon=3.20387967)
download_simar_point(case_name, latitude, longitude)
