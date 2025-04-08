import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import sys
from shapely.geometry import Polygon, Point
from scipy.interpolate import LinearNDInterpolator

# ========================== Step 1: Read Grid (CGRID) ==========================
def read_cgrid(input_file):
    """
    Reads the CGRID definition from the given file to extract domain parameters.

    Parameters:
        input_file (str): Path to the file containing the CGRID definition.

    Returns:
        tuple: (easting, northing, xlen, ylen, nx, ny) or raises an error if not found.
    """
    with open(input_file, 'r') as f:
        for line in f:
            if line.startswith("CGRID"):
                parts = line.split()
                try:
                    easting = float(parts[1])
                    northing = float(parts[2])
                    xlen = float(parts[4])
                    ylen = float(parts[5])
                    nx = int(parts[6]) + 1
                    ny = int(parts[7]) + 1
                    return easting, northing, xlen, ylen, nx, ny
                except (IndexError, ValueError) as e:
                    raise ValueError(f"Error parsing CGRID line: {line}\n{e}")
    
    raise ValueError("CGRID definition not found in the input file.")

# ========================== Step 2: Read Bathymetry Data ==========================
def read_bathymetry(bathy_file):
    """
    Reads bathymetry data from a file.

    Parameters:
        bathy_file (str): Path to the bathymetry file.

    Returns:
        pd.DataFrame: DataFrame containing columns ['x', 'y', 'depth'].
    """
    try:
        data = pd.read_csv(bathy_file, sep=r'\s+', header=None, names=['x', 'y', 'depth'], dtype={'x': float, 'y': float, 'depth': float})
        print("Bathymetry successfully read!")
        return data
    except Exception as e:
        raise ValueError(f"Error reading bathymetry file {bathy_file}: {e}")

# ========================== Step 3: Interpolate Bathymetry ==========================
def interpolate_bathymetry(bathy_data, mallorca_polygon, easting, northing, xlen, ylen, nx, ny):
    """
    Interpolates bathymetry while respecting land-water boundaries.

    Parameters:
        bathy_data (pd.DataFrame): Bathymetry DataFrame with ['x', 'y', 'depth'].
        mallorca_polygon (Polygon): Shapely Polygon of Mallorca's coastline.
        easting, northing (float): Grid start coordinates.
        xlen, ylen (float): Grid size in x and y directions.
        nx, ny (int): Grid resolution.

    Returns:
        grid_x, grid_y (2D arrays): Meshgrid coordinates.
        interpolated_depths (2D array): Interpolated bathymetric depths.
    """
    grid_x = np.linspace(easting, easting + xlen, nx)
    grid_y = np.linspace(northing, northing + ylen, ny)
    grid_x, grid_y = np.meshgrid(grid_x, grid_y)

    # Filter out land points from bathymetry data
    print("filterinn land-water points")
    valid_points = np.array([
        (x, y, d) for x, y, d in zip(bathy_data['x'], bathy_data['y'], bathy_data['depth'])
        if not mallorca_polygon.contains(Point(x, y))
    ])

    if len(valid_points) == 0:
        raise ValueError("No valid water points found for interpolation.")
    print("interpolatinnnnn")
    # Perform interpolation
    interpolator = LinearNDInterpolator(valid_points[:, :2], valid_points[:, 2])
    interpolated_depths = interpolator(grid_x, grid_y)

    # Mask out land points in interpolation results
    for i in range(grid_x.shape[0]):
        for j in range(grid_x.shape[1]):
            if mallorca_polygon.contains(Point(grid_x[i, j], grid_y[i, j])):
                interpolated_depths[i, j] = -1  # Assign -1 to land

    print("Interpolation done.")
    return grid_x, grid_y, interpolated_depths
# ========================== Step 4: Saving interpolation functions ==========================
def save_bathymetry(output_file, grid_x, grid_y, depths):
    with open(output_file, 'w') as f:
        for i in range(depths.shape[0]):
            for j in range(depths.shape[1]):
                f.write(f"{grid_x[i, j]:.6f} {grid_y[i, j]:.6f} {depths[i, j]:.2f}\n")

def save_bathymetry_matrix(output_file, depths, ):
    """Saves only the depth values in grid format (no coordinates)."""
    depths_flipped = np.flipud(depths) #porque la np.meshgrid gira el eje y
    np.savetxt(output_file, depths_flipped, fmt="%.2f")
    print(f"Depth matrix saved to {output_file}")


# ========================== Step 5: Load Coastline and Define Domain ==========================
#NOTE: all paths changed to automate_forecast.sh
# Load coastline data for Mallorca
coastline_file = "./DATA/coastline/mallorca_coastline_utm_HRES.dat"
coastline_data = np.loadtxt(coastline_file)  # Columns: utm_easting, utm_northing

# read mallorca polygon
gdf = gpd.read_file("./DATA/polygon/mallorca_polygon.shp")
mallorca_polygon = gdf.geometry[0]

# Use this polygon for land-water boundary checks in interpolation
print("Mallorca polygon loaded successfully!")

# Load bathymetry
bathy_file = "./DATA/bathy/BatimetriaRegenerada_mallorca.dat"
#bathy_file = "../../cases/boya/bathy/BatimetriaRegenerada_mallorca_with_HREScoastline.dat"
bathy_data = read_bathymetry(bathy_file)

# specific case
case_name = sys.argv[1] if len(sys.argv) > 1 else "default_case" # add default like: else "default_case"
swan_case_name = sys.argv[2] if len(sys.argv) > 2 else "default_swan_case"
# Load domain configuration
cgrid_file = (f"./cases/{case_name}/input_{swan_case_name}.swn")  # Change this to the actual CGRID file
easting, northing, xlen, ylen, nx, ny = read_cgrid(cgrid_file)

#load coastline in domain
#coast_easting, coast_northing = coastline_data[: 0], coastline_data[:, 1]
# Definir los límites del dominio
emin, emax = easting, easting + xlen
nmin, nmax = northing, northing + ylen

# Crear una máscara booleana para seleccionar puntos dentro del dominio
mask = (coastline_data[:, 0] >= emin) & (coastline_data[:, 0] <= emax) & \
       (coastline_data[:, 1] >= nmin) & (coastline_data[:, 1] <= nmax)

# Aplicar la máscara a los datos de la línea de costa
coast_easting = coastline_data[mask, 0]
coast_northing = coastline_data[mask, 1]

# Interpolate bathymetry
grid_x, grid_y, interpolated_depths = interpolate_bathymetry(bathy_data, mallorca_polygon, easting, northing, xlen, ylen, nx, ny)

# save interpolated bathymetry
interpolated_file=(f"./cases/{case_name}/bathy/bottom_{swan_case_name}_HRES.dat")
interpolated_file_matrix=(f"./cases/{case_name}/bathy/bottom_{swan_case_name}_HRES_matrix.dat")

save_bathymetry(interpolated_file, grid_x, grid_y, interpolated_depths)
save_bathymetry_matrix(interpolated_file_matrix, interpolated_depths)
# 
# ========================== Step 5: Plot Results ==========================
plt.figure(figsize=(10, 8))
plt.pcolormesh(grid_x, grid_y, interpolated_depths, shading='auto', cmap='Blues')
plt.colorbar(label="Depth (m)")
plt.plot(coast_easting, coast_northing, 'k-', label="Coastline")
plt.xlabel("Easting (m)")
plt.ylabel("Northing (m)")
plt.title(f"Interpolated Bathymetry around {case_name}")
plt.legend()
plt.grid()
plt.axis('equal')
plt.savefig(f"./cases/{case_name}/figures/bathy_{swan_case_name}.png")
#plt.show()

"""def save_bathymetry(output_file, grid_x, grid_y, depths):
    with open(output_file, 'w') as f:
        for i in range(depths.shape[0]):
            for j in range(depths.shape[1]):
                f.write(f"{grid_x[i, j]:.6f} {grid_y[i, j]:.6f} {depths[i, j]:.2f}\n")

def save_bathymetry_matrix(output_file, depths, ):
    #Saves only the depth values in grid format (no coordinates).
    depths_flipped = np.flipud(depths) #porque la np.meshgrid gira el eje y
    np.savetxt(output_file, depths_flipped, fmt="%.2f")
    print(f"Depth matrix saved to {output_file}")

def main(input_file, bathy_file, output_file1, output_file2):
    cgrid_params = read_cgrid(input_file)
    if cgrid_params:
        easting, northing, xlen, ylen, nx, ny = cgrid_params
        bathy_data = read_bathymetry(bathy_file)
        grid_x, grid_y, depths = interpolate_bathymetry(bathy_data, easting, northing, xlen, ylen, nx, ny)
        save_bathymetry(output_file1, grid_x, grid_y, depths)
        save_bathymetry_matrix(output_file2, depths)
        print(f"Interpolated bathymetry saved to {output_file1}")
    else:
        print("CGRID parameters not found in the input file.")

INPUT="../../cases/alcudia/input_ca00.swn"
bathy_file=("../../cases/boya/bathy/BatimetriaRegenerada_mallorca_with_HREScoastline.dat") #bathy and coatline file
interpolated_file=("../../cases/alcudia/bathy/bottom_ca00_HRES.dat")
interpolated_file_matrix=("../../cases/alcudia/bathy/bottom_ca00_HRES_matrix.dat")

# Example usage:
main(INPUT, bathy_file, interpolated_file, interpolated_file_matrix)"""

"""# check reading
easting, northing, xlen, ylen, nx, ny=read_cgrid("../../input_ca02.swn")
print(easting, northing, xlen, ylen, nx, ny)
# check read base bathymetry
data = read_bathymetry("../../bathy/BatimetriaRegenerada_mallorca.dat")
print(data.head())
# check bathymetry
grid_x, grid_y, interpolated_depths = interpolate_bathymetry(data, easting, northing, xlen, ylen, nx, ny)
print(grid_x, grid_y)
"""
