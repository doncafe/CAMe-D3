import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from datetime import datetime

def load_and_process_data():
    """
    Load and process both O3 and SWDOWN data
    """
    # Read O3 data
    o3_df = pd.read_csv('RAMA_O3_MAYO_2022_155ppb.csv', 
                        names=['timestamp', 'o3_concentration'])
    
    # Convert O3 timestamps to datetime
    o3_df['timestamp'] = pd.to_datetime(o3_df['timestamp'])
    
    # Read SWDOWN data
    swdown_df = pd.read_csv('swdown_hourly_area_timeseries.csv')
    swdown_df['timestamp'] = pd.to_datetime(swdown_df['timestamp'])
    
    # Merge datasets on timestamp
    merged_df = pd.merge(o3_df, swdown_df[['timestamp', 'SWDOWN']], 
                        on='timestamp', how='inner')
    
    return merged_df

def create_correlation_plots(df):
    """
    Create correlation plots between O3 and SWDOWN
    """
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Scatter plot
    ax1.scatter(df['SWDOWN'], df['o3_concentration'], alpha=0.6)
    ax1.set_xlabel('SWDOWN (W/m²)')
    ax1.set_ylabel('O₃ Concentration (ppb)')
    ax1.set_title('O₃ vs SWDOWN Scatter Plot')
    ax1.grid(True)
    
    # Calculate and add regression line
    slope, intercept, r_value, p_value, std_err = stats.linregress(df['SWDOWN'], 
                                                                  df['o3_concentration'])
    line = slope * df['SWDOWN'] + intercept
    ax1.plot(df['SWDOWN'], line, color='red', 
             label=f'R² = {r_value**2:.3f}\np-value = {p_value:.3e}')
    ax1.legend()
    
    # Time series plot
    ax2.plot(df['timestamp'], df['o3_concentration'], 
             label='O₃ Concentration', color='blue')
    ax2_twin = ax2.twinx()
    ax2_twin.plot(df['timestamp'], df['SWDOWN'], 
                 label='SWDOWN', color='red', alpha=0.6)
    
    ax2.set_xlabel('Time')
    ax2.set_ylabel('O₃ Concentration (ppb)', color='blue')
    ax2_twin.set_ylabel('SWDOWN (W/m²)', color='red')
    
    # Adjust legend
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2_twin.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    ax2.set_title('O₃ and SWDOWN Time Series')
    
    plt.tight_layout()
    plt.savefig('o3_swdown_correlation.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Print statistics
    print(f"Correlation Analysis Results:")
    print(f"Pearson correlation coefficient (R): {r_value:.3f}")
    print(f"R-squared (R²): {r_value**2:.3f}")
    print(f"P-value: {p_value:.3e}")
    print(f"Slope: {slope:.3f}")
    print(f"Intercept: {intercept:.3f}")
    
    return r_value**2, p_value

if __name__ == "__main__":
    print("Loading and processing data...")
    data = load_and_process_data()
    
    print("\nCreating correlation plots...")
    r_squared, p_value = create_correlation_plots(data)
    
    # Additional analysis
    print("\nSummary Statistics:")
    print(data.describe())
    
    # Save processed data
    data.to_csv('o3_swdown_correlation_data.csv', index=False)
    print("\nProcessed data saved to 'o3_swdown_correlation_data.csv'")