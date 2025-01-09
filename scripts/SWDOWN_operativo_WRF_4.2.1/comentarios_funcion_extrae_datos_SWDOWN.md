
```
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
```
    
Enseguida se dan detalles de la sección superior de la función del código que extrae el valor promedio
y máximo de la variable `SWDOWN` para el área seleccionada definida por: 
`lon_bounds=[-99.26, -98.88]`, `lat_bounds=[19.3, 19.75]`)

Este código crea una máscara para seleccionar el área de estudio y calcula el valor promedio de `SWDOWN` dentro de esta área.

`lat_mask` y `lon_mask` crean máscaras booleanas para seleccionar valores de latitud y longitud dentro de los límites especificados (`lat_bounds` y `lon_bounds`). 

`combined_mask` combina estas dos máscaras usando una operación lógica AND: `&`, 
seleccionando sólo las celdas de la cuadrícula que caen dentro de los límites tanto de latitud como de longitud.
 
El método `where` aplica esta máscara combinada al conjunto de datos `SWDOWN`, seleccionando sólo los valores dentro del área de interés. 
El método `mean` calcula el valor promedio de los valores SWDOWN seleccionados sobre los ejes `south_north` y `west_east`. 
    
    
