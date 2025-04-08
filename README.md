# HRES operational for Wave Forecasting
This system forecasts +24h of wave conditions around the Balearic Islands. It focuses on Palma de Mallorca's bay/port, but it can be adapted to any location within Mallorca.
## Requirements
Before running the system, you need to set up a few things:

### 1. SWAN Model
You need to have SWAN (Simulating Waves Nearshore) compiled with NetCDF support. You can follow the instructions in the [Implementation Manual](https://swanmodel.sourceforge.io/download/zip/swanimp.pdf) to download and compile SWAN.

### 2. utm Python Library
This project requires the `utm` library to convert coordinates. You can get the library from the [GitHub repository](https://github.com/Turbo87/utm).

### 3. Python Virtual Environment
A Python virtual environment is recommended for managing dependencies. You can create one and install the necessary packages from the `requirements.txt` file:

```bash
python3 -m venv utm_env # you could call utm_env as you wanted and modify its source in the bash script
source utm_env/bin/activate  # linux
pip install -r requirements.txt
```
## Project Overview
Here's a tree of the project folder structure:
```
swan-ROE
│   automate_forecast_allINPUTfiles_timeGPT.sh
│
└───cases
│   │
│   └───palma
│       │   README
│       │   input_ca00.swn
│       │   input_ca01.swn
│       │   input_ca02.swn
│       │   input_ca03.swn
│       │   input_ca04.swn
│       │   swan.exe
│       │   swaninit
│       │   swanrun
│       │
|       └───bathy
│       │       │    bottom_ca00_HRES_matrix.dat 
│       │       │    ...
│
└───DATA
│   │
│   └───bathy
│       │   BatimetriaRegenerada_mallorca.dat
│   │
│   └───coastline
│       │   mallorca_coastline.dat
│       │   mallorca_coastline_utm.dat
│       │   ...
│   │
│   └───polygon
│       │   mallorca_polygon.cpg
│       │   ...
│ 
└───scripts
│   │
│   └───bathy
│       │   interpolate2.py
│   │
│   └───opendap
│       │   save_simar_point_to_TPAR.py
│  
└───timeGPT
    │   timeGPT.py
│   .gitignore
│   README.md
│   requirements.txt  

```
- **`automate_forecast_allINPUTfiles_timeGPT.sh`**: This file executes the operational system. Modify for your personal cases.
- **`/cases/`**: This directory holds the configuration files for various locations. Currently, there is a test case for Palma de Mallorca. However, you could configure new ones.
    - **`/palma/`**: The folder contains all the necessary files to run SWAN for Palma de Mallorca's bay, including:
        - **`/bathy/`**:
            - Bathymetry data (`bottom_ca00_HRES.dat`, etc.)
        - Input configuration files for SWAN (`input_caxx.swn`, etc.). The input_ca00.swn is the one configured to work operationally. Read the README to see the differences between input_caxx.swn.
        - Scripts to run SWAN (`swanrun`, etc.). When compiling swan in your computer you will need to cp the swanrun and swan.exe to each case you want to run. In this case I modifed swanrun so that it uses 28cores. You will need to get them by compiling SWAN in your computer.

- **`/DATA/`**: Stores all data related to the simulations, including coastline data, bathymetric data, and polygons.

- **`/scripts/`**: Contains Python scripts used for different tasks within the project. For example:
    - **`/bathy/`**:
        -  `interpolate2.py`:  Interpolates general bathymetry of Mallorca and creates the file needed to run SWAN in the region of interest, specified by input_caxx.swn
    - **`/opendap/`**:
        - `save_simar_point_to_TPAR.py`: Downloads simar data that will be used as BC. Taking into account what's specified in input.swn

- **`/timeGPT/`**: 
  - `timeGPT.py`: Runs timeGPT using each day swan fcst. It adjustes the model's result to what the tyde gauge in located in Palma de Mallorca could measure.
  - `.env`: I have not uploaded mine. You will need to create a nixtla account and save the nixtla key here. More info in [Nixtla repo. sec. 2b](https://nixtlaverse.nixtla.io/nixtla/docs/getting-started/setting_up_your_api_key.html).

- **`.gitignore`**: Specifies which files and folders should be ignored by git.

- **`requirements.txt`**: A list of all the Python dependencies needed to run the project. You can install the necessary packages using `pip install -r requirements.txt`.

- **`README.md`**: This file that explains the purpose and structure of the repository.
# How to use
# Create a new case


