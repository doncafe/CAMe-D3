import xarray as xr
import pandas as pd

def get_radiation_variables(wrf_file_path):
    """
    Extraer variables relacionadas a Radiacion de Onda Corta (SWDOWN) a partir de 
    una lista de palabras 

    Parametros:
    wrf_file_path (str): Ruta de archivos del WRF NetCDF 
    
    Returns:
    pandas.DataFrame: DataFrame containing radiation-related variables
    """
    # Common keywords related to shortwave radiation in WRF
    sw_keywords = [
        'swdown', 
    ]
    
    try:
        ds = xr.open_dataset(wrf_file_path)
        
        rad_vars = []

        for var_name in ds.variables:
            var = ds[var_name]
            attrs = var.attrs
            
            is_radiation_var = any(keyword in var_name.lower() for keyword in sw_keywords)
            if 'description' in attrs:
                is_radiation_var = is_radiation_var or any(
                    keyword in attrs['description'].lower() for keyword in sw_keywords
                )
            
            if is_radiation_var:
                rad_vars.append({
                    'Variable': var_name,
                    'Dimensions': ', '.join(var.dims),
                    'Units': attrs.get('units', 'No units specified'),
                    'Description': attrs.get('description', 'No description available'),
                    'Shape': str(var.shape)
                })
        
        ds.close()
        
        df = pd.DataFrame(rad_vars)
        if not df.empty:
            df = df.sort_values('Variable').reset_index(drop=True)
            
            common_vars = {
                'SWDOWN': 'Downward shortwave radiation flux at ground surface',
            }
            
            df['Standard_Description'] = df['Variable'].map(common_vars)
            
        return df
    
    except Exception as e:
        print(f"Error reading WRF file: {str(e)}")
        return None

def print_radiation_summary(df):
    if df is None or df.empty:
        print("\nNo shortwave radiation variables found in the WRF output file.")
        return
        
    print("\nShortwave Radiation Variables in WRF Output:")
    print("=" * 100)
    
    for _, row in df.iterrows():
        print(f"\nVariable: {row['Variable']}")
        print(f"Dimensions: {row['Dimensions']}")
        print(f"Shape: {row['Shape']}")
        print(f"Units: {row['Units']}")
        print(f"Description: {row['Description']}")
        if pd.notna(row.get('Standard_Description')):
            print(f"Standard Description: {row['Standard_Description']}")
        print("-" * 100)

# Example usage
if __name__ == "__main__":
    wrf_file = "/LUSTRE/ID/hidromet/WRF/Salidas_WRF_mayo_2022/wrfout_d02_2022-05-02_00.nc" 
    
    radiation_df = get_radiation_variables(wrf_file)
    
    if radiation_df is not None:
        # Save to CSV for later reference
        radiation_df.to_csv("wrf_radiation_variables.csv", index=False)
        
        # Print formatted summary
        print_radiation_summary(radiation_df)
