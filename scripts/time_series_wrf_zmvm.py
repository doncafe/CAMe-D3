import xarray as xr
import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime

def extract_swdown_area(wrf_dir, lat_bounds, lon_bounds):
    """
    Extract SWDOWN time series from daily WRF output files 
    
    Parameters:
    wrf_dir (str): Directory containing WRF output files
    lat_bounds (tuple): (min_lat, max_lat) in decimal degrees
    lon_bounds (tuple): (min_lon, max_lon) in decimal degrees
    
    Returns:
    tuple: (DataFrame with hourly data, DataFrame with daily statistics)
    """
    wrf_files = sorted(glob.glob(os.path.join(wrf_dir, "wrfout_d02_*.nc")))
    print(f"Found {len(wrf_files)} WRF output files")
    
    all_data = []
    
    for file in wrf_files:
        try:
            print(f"Processing file: {os.path.basename(file)}")
            ds = xr.open_dataset(file)
            
            # Get the grid coordinates
            lat = ds.XLAT.isel(Time=0)
            lon = ds.XLONG.isel(Time=0)
            
            # Create mask for the area of interest
            mask = (
                (lat >= lat_bounds[0]) & 
                (lat <= lat_bounds[1]) & 
                (lon >= lon_bounds[0]) & 
                (lon <= lon_bounds[1])
            )
            
            # Calculate average SWDOWN for the masked area
            swdown = ds.SWDOWN.where(mask).mean(dim=['south_north', 'west_east'])
            
            # Extract times from filename
            file_time_str = os.path.basename(file).split('_')[2:4]
            file_time_str = '_'.join(file_time_str).replace('.nc', '')
            start_time = datetime.strptime(file_time_str, '%Y-%m-%d_%H')
            
            # Create time range
            n_times = len(swdown)
            times = pd.date_range(start=start_time, periods=n_times, freq='H')
            
            # Create DataFrame for this file
            df = pd.DataFrame({
                'timestamp': times,
                'SWDOWN': swdown.values
            })
            
            all_data.append(df)
            ds.close()
            
        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")
            continue
    
    if not all_data:
        return None, None
        
    # Combine and process all data
    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.sort_values('timestamp')
    
    # Add time information
    final_df['date'] = final_df['timestamp'].dt.date
    final_df['hour'] = final_df['timestamp'].dt.hour
    final_df['day'] = final_df['timestamp'].dt.day
    
    # Calculate daily statistics
    daily_stats = final_df.groupby('date').agg({
        'SWDOWN': ['mean', 'max', 'min', 'std']
    }).round(2)
    
    return final_df, daily_stats

def plot_swdown_timeseries(df, daily_stats, output_prefix='zmvm'):
    """
    Create plots of SWDOWN time series for the area.
    """
    import matplotlib.pyplot as plt
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot hourly values
    ax1.plot(df['timestamp'], df['SWDOWN'], 'b-', label='Hourly SWDOWN')
    ax1.set_title('Valores horarios de radiacion de onda corta que llega a la superficie (SWDOWN) (Area CAMe Promedio)')
    ax1.set_xlabel('t (h)')
    ax1.set_ylabel('SWDOWN (W/m²)')
    ax1.grid(True)
    ax1.legend()
    
    # Plot daily statistics
    daily_stats['SWDOWN']['mean'].plot(ax=ax2, label='Diario Promedio')
    daily_stats['SWDOWN']['max'].plot(ax=ax2, label='Diario Max')
    # daily_stats['SWDOWN']['min'].plot(ax=ax2, label='Diario Min')
    ax2.set_title('Valores diarios de SWDOWN estadisticos (Area CAMe Promedio)')
    ax2.set_xlabel('Dia')
    ax2.set_ylabel('SWDOWN (W/m²)')
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(f'swdown_{output_prefix}_timeseries.png')
    plt.close()

# Example usage
if __name__ == "__main__":
    # Directory containing WRF output files
    wrf_dir = "/LUSTRE/ID/hidromet/WRF/Salidas_WRF_mayo_2022"
    
    # Define area bounds (DMS)
    lat_bounds = (19.18, 19.45)  # (min_lat, max_lat)
    lon_bounds = (-99.15, -98.52)  # (min_lon, max_lon)
    
    print("Starting area analysis...")
    df, daily_stats = extract_swdown_area(wrf_dir, lat_bounds, lon_bounds)
    
    if df is not None:
        print("Saving results to CSV files...")
        df.to_csv("swdown_hourly_area_timeseries.csv", index=False)
        daily_stats.to_csv("swdown_daily_area_statistics.csv")
        
        print("Creating plots...")
        plot_swdown_timeseries(df, daily_stats)
        
        print("\nSWDOWN Daily Statistics Summary:")
        print("=" * 50)
        print(daily_stats)
    else:
        print("No data was processed successfully.")
