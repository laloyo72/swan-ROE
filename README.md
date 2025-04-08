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
```
project
│   README.md
│   requirements.txt    
│
└───scripts
│   │
│   └───bathy
│       │   file112.txt
│       │   ...
│   │
│   └───opendap
│       │   file111.txt
│       │   file112.txt
│       │   ...
│   
└───folder2
    │   file021.txt
    │   file022.txt
```


