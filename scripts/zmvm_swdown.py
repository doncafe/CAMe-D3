import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

def create_area_map(lat_bounds, lon_bounds, output_file='area_came.png'):
    """
    Create a map showing the area of interest with context.
    
    Parameters:
    lat_bounds (tuple): (min_lat, max_lat) in decimal degrees
    lon_bounds (tuple): (min_lon, max_lon) in decimal degrees
    output_file (str): Name of the output file
    """
    # Add some padding around the area for context
    pad = 0.5  # degrees
    
    # Create figure and axes with Mercator projection
    plt.figure(figsize=(12, 8))
    ax = plt.axes(projection=ccrs.Mercator())
    
    # Set map bounds (with padding)
    ax.set_extent([
        lon_bounds[0] - pad,
        lon_bounds[1] + pad,
        lat_bounds[0] - pad,
        lat_bounds[1] + pad
    ])
    
    # Add map features
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, linestyle=':')
    
    # Add gridlines
    gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False
    
    # Create rectangle for area of interest
    import matplotlib.patches as mpatches
    rect = mpatches.Rectangle(
        (lon_bounds[0], lat_bounds[0]),
        lon_bounds[1] - lon_bounds[0],
        lat_bounds[1] - lat_bounds[0],
        facecolor='none',
        edgecolor='none',
        linewidth=2,
        transform=ccrs.PlateCarree()
    )
    ax.add_patch(rect)
    
    # Add title and labels
    plt.title('Area a considerar (CAMe)\n' +
             f'Latitud: {lat_bounds[0]}°N to {lat_bounds[1]}°N\n' +
             f'Longitud: {lon_bounds[0]}°W to {lon_bounds[1]}°W')
    
    # Add some major cities for reference
    cities = {
        'CDMX': (-99.133333, 19.433333),
        'Cuernavaca': (-99.25, 18.9167),
        'Toluca': (-99.6667, 19.2833),
        'Puebla': (-98.2063, 19.0414)
    }
    
    for city, coords in cities.items():
        ax.plot(coords[0], coords[1], 'ko', markersize=5,
                transform=ccrs.PlateCarree())
        ax.text(coords[0] + 0.1, coords[1] - 0.1, city,
                transform=ccrs.PlateCarree())
    
    # Save the map
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    # Define the area bounds in DMS
    lat_bounds = (19.18, 19.45)  # (min_lat, max_lat)
    lon_bounds = (-99.15, -98.52)  # (min_lon, max_lon)
    
    print("Creating map of the area of interest...")
    create_area_map(lat_bounds, lon_bounds)
    print("Map has been saved as 'area_map.png'")
