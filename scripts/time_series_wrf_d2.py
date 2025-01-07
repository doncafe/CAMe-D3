import xarray as xr
import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime

def extract_swdown_timeseries(wrf_dir, point_lat=None, point_lon=None):
    """
    Extract SWDOWN time series from daily WRF output files for a month.
    
    Parameters:
    wrf_dir (str): Directory containing WRF output files
    point_lat (float, optional): Latitude of point of interest
    point_lon (float, optional): Longitude of point of interest
    
    Returns:
    pandas.DataFrame: DataFrame containing SWDOWN time series
    """
    # Get list of WRF output files
    wrf_files = sorted(glob.glob(os.path.join(wrf_dir, "wrfout_d02_*.nc")))
    print(f"Found {len(wrf_files)} WRF output files")
    
    all_data = []
    
    for file in wrf_files:
        try:
            print(f"Processing file: {os.path.basename(file)}")
            # Open dataset
            ds = xr.open_dataset(file)
            
            if point_lat is not None and point_lon is not None:
                # For a specific point - find nearest grid point
                lat = ds.XLAT.isel(Time=0)
                lon = ds.XLONG.isel(Time=0)
                
                # Find indices of nearest grid point
                dist = abs(lat - point_lat) + abs(lon - point_lon)
                y_idx, x_idx = np.unravel_index(dist.argmin(), dist.shape)
                
                # Extract SWDOWN for this point
                swdown = ds.SWDOWN.isel(south_north=y_idx, west_east=x_idx)
                
            else:
                # Calculate domain average if no specific point is given
                swdown = ds.SWDOWN.mean(dim=['south_north', 'west_east'])
            
            # Extract times from filename if Times variable is not accessible
            file_time_str = os.path.basename(file).split('_')[2:4]
            file_time_str = '_'.join(file_time_str).replace('.nc', '')
            start_time = datetime.strptime(file_time_str, '%Y-%m-%d_%H')
            
            # Create time range based on SWDOWN shape
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
            print("Full error details:", e)
            continue
    
    # Combine all data
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df = final_df.sort_values('timestamp')
        
        # Add additional time information
        final_df['date'] = final_df['timestamp'].dt.date
        final_df['hour'] = final_df['timestamp'].dt.hour
        final_df['day'] = final_df['timestamp'].dt.day
        
        # Calculate daily statistics
        daily_stats = final_df.groupby('date').agg({
            'SWDOWN': ['mean', 'max', 'min', 'std']
        }).round(2)
        
        return final_df, daily_stats
    
    return None, None

def plot_swdown_timeseries(df, daily_stats):
    """
    Create plots of SWDOWN time series using matplotlib.
    """
    import matplotlib.pyplot as plt
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot hourly values
    ax1.plot(df['timestamp'], df['SWDOWN'], 'b-', label='Hourly SWDOWN')
    ax1.set_title('Hourly SWDOWN Values')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('SWDOWN (W/m²)')
    ax1.grid(True)
    ax1.legend()
    
    # Plot daily statistics
    daily_stats['SWDOWN']['mean'].plot(ax=ax2, label='Daily Mean')
    daily_stats['SWDOWN']['max'].plot(ax=ax2, label='Daily Max')
    daily_stats['SWDOWN']['min'].plot(ax=ax2, label='Daily Min')
    ax2.set_title('Daily SWDOWN Statistics')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('SWDOWN (W/m²)')
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('swdown_d2_timeseries.png')
    plt.close()

# Example usage
if __name__ == "__main__":
    # Directory containing WRF output files
    wrf_dir = "/LUSTRE/ID/hidromet/WRF/Salidas_WRF_mayo_2022"
    
    # Extract time series
    print("Starting time series extraction...")
    df, daily_stats = extract_swdown_timeseries(wrf_dir)
    
    if df is not None:
        # Save to CSV
        print("Saving results to CSV files...")
        df.to_csv("swdown_hourly_d2_timeseries.csv", index=False)
        daily_stats.to_csv("swdown_daily_d2_statistics.csv")
        
        # Create plots
        print("Creating plots...")
        plot_swdown_timeseries(df, daily_stats)
        
        # Print summary statistics
        print("\nSWDOWN Daily Statistics Summary:")
        print("=" * 50)
        print(daily_stats)
    else:
        print("No data was processed successfully.")
