import xarray as xr
import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime

def extract_swdown_timeseries(wrf_dir, lon_bounds=[-99.26, -98.88], lat_bounds=[19.3, 19.75]):
    """
    Extrae la serie de tiempo de SWDOWN de los archivos de salida diarios de WRF para una área específica (Dominio CAME).
    
    Parametros:
    wrf_dir (str): Directorio con las salidas del modelo WRF
    lon_bounds (list): [min_lon, max_lon] area de interes
    lat_bounds (list): [min_lat, max_lat] area de interes
    
    Regresa:
    tuple: (DataFrame with hourly data, DataFrame with daily maximum values)
    """
    wrf_files = sorted(glob.glob(os.path.join(wrf_dir, "wrfout_d02_*.nc")))
    print(f"Found {len(wrf_files)} WRF output files")
    
    all_data = []
    
    for file in wrf_files:
        try:
            print(f"Processing file: {os.path.basename(file)}")
            ds = xr.open_dataset(file)
            
            # lat/lon coord
            if 'XLAT' in ds and 'XLONG' in ds:
                lats = ds.XLAT.values[0]  # Obtener coord
                lons = ds.XLONG.values[0]
                
                # mascara del area de interes
                lat_mask = (lats >= lat_bounds[0]) & (lats <= lat_bounds[1])
                lon_mask = (lons >= lon_bounds[0]) & (lons <= lon_bounds[1])
                combined_mask = lat_mask & lon_mask
                
                # Calcula el promedio de SWDOWN en la mascara
                swdown = ds.SWDOWN.where(combined_mask).mean(dim=['south_north', 'west_east'])
            else:
                print(f"Warning: XLAT/XLONG not found in {file}, skipping spatial subsetting")
                continue
            
            # Extrae las horas desde el nombre del archivo
            file_time_str = os.path.basename(file).split('_')[2:4]
            file_time_str = '_'.join(file_time_str).replace('.nc', '')
            start_time = datetime.strptime(file_time_str, '%Y-%m-%d_%H')
            
            # Crea un rango de tiempos basado en la longitud de swdown
            n_times = len(swdown)
            times = pd.date_range(start=start_time, periods=n_times, freq='h')
            
            # Crea DataFrame
            df = pd.DataFrame({
                'timestamp': times,
                'SWDOWN': swdown.values,
                'lat_min': lat_bounds[0],
                'lat_max': lat_bounds[1],
                'lon_min': lon_bounds[0],
                'lon_max': lon_bounds[1]
            })
            
            all_data.append(df)
            ds.close()
            
        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")
            continue
    
    if not all_data:
        return None, None
        
    # Combinar todos los datos
    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.sort_values('timestamp')
    
    # Agregar informacion de tiempo
    final_df['date'] = final_df['timestamp'].dt.date
    final_df['hour'] = final_df['timestamp'].dt.hour
    final_df['day'] = final_df['timestamp'].dt.day
    final_df['month'] = final_df['timestamp'].dt.month
    
    # Considerar solo el mes de mayo
    final_df = final_df[final_df['month'] == 5]
    
    # Calcular el valor maximo diario
    daily_max = final_df.groupby('date').agg({
        'SWDOWN': 'max'
    }).round(2)
    daily_max.columns = ['max_SWDOWN']
    
    return final_df, daily_max

def plot_swdown_timeseries(df, output_prefix=''):
    """
    Crear graficos de la serie de tiempo de SWDOWN para mayo utilizando matplotlib.
    
    Parametros:
    df: pandas DataFrame que contiene los datos de SWDOWN
    output_prefix
    """
    import matplotlib.pyplot as plt
    
    # Hourly values plot for May
    fig, ax1 = plt.subplots(figsize=(26, 12))
    ax1.plot(df['timestamp'], df['SWDOWN'], 'b-', label='SWDOWN hourly')
    ax1.set_title(f'Valores horarios de radiación de onda corta (SWDOWN) - Mayo 2022\nDominio CAMe')
    ax1.set_xlabel('Fecha')
    ax1.set_ylabel('SWDOWN (W/m²)')
    ax1.grid(True)
    ax1.legend()
    
    plt.tight_layout()
    plt.savefig(f'{output_prefix}swdown_may_timeseries.png')
    plt.close()
    
    # Daily maximum plot for May
    daily_max = df.groupby('date')['SWDOWN'].max()
    
    fig, ax2 = plt.subplots(figsize=(26, 12))
    ax2.plot(daily_max.index, daily_max.values, 'r-', label='Valor maximo diario')
    ax2.set_title(f'Valores maximo de radiación de onda corta diaria (SWDOWN) - Mayo 2022\nDominio CAMe')
    ax2.set_xlabel('Fecha')
    ax2.set_ylabel('SWDOWN (W/m²)')
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(f'{output_prefix}swdown_may_daily_max.png')
    plt.close()

if __name__ == "__main__":
    # Directory containing WRF output files
    wrf_dir = "/LUSTRE/ID/hidromet/WRF/Salidas_WRF_mayo_2022"
    
    # Define area of interest
    lon_bounds = [-99.26, -98.88]
    lat_bounds = [19.3, 19.75]
    
    print("Starting time series extraction...")
    df, daily_max = extract_swdown_timeseries(wrf_dir, lon_bounds, lat_bounds)
    
    if df is not None:
        # Save to CSV
        print("Saving results to CSV files...")
        output_prefix = f"swdown_may_area_{lat_bounds[0]}-{lat_bounds[1]}N_{abs(lon_bounds[0])}-{abs(lon_bounds[1])}W_"
        df.to_csv(f"{output_prefix}hourly.csv", index=False)
        daily_max.to_csv(f"{output_prefix}daily_max.csv")
        
        # Create plots
        print("Creating plots...")
        plot_swdown_timeseries(df, output_prefix)
        
        # Print daily maximum values
        print("\nDaily Maximum SWDOWN Values for May:")
        print("=" * 50)
        print(daily_max)
    else:
        print("No data was processed successfully.")