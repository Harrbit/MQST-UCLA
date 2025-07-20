import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit

class DataPlotter:
    def __init__(self):
        self.setup_prl_style()
    
    def setup_prl_style(self):
        """Set up PRL style parameters"""
        plt.rcParams['figure.figsize'] = [3.4, 2.5]
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.serif'] = ['Computer Modern Roman']
        plt.rcParams['text.usetex'] = True
        plt.rcParams['font.size'] = 8
        plt.rcParams['axes.labelsize'] = 9
        plt.rcParams['xtick.labelsize'] = 8
        plt.rcParams['ytick.labelsize'] = 8
        plt.rcParams['legend.fontsize'] = 8
        plt.rcParams['axes.linewidth'] = 0.5
        plt.rcParams['lines.linewidth'] = 1.0
        plt.rcParams['xtick.major.size'] = 3
        plt.rcParams['xtick.major.width'] = 0.5
        plt.rcParams['xtick.minor.size'] = 1.5
        plt.rcParams['xtick.minor.width'] = 0.5
        plt.rcParams['ytick.major.size'] = 3
        plt.rcParams['ytick.major.width'] = 0.5
        plt.rcParams['ytick.minor.size'] = 1.5
        plt.rcParams['ytick.minor.width'] = 0.5
        plt.rcParams['axes.xmargin'] = 0.02
        plt.rcParams['axes.ymargin'] = 0.02

    def lorentzian(self, x, amp, x0, gamma, offset):
        """Lorentzian line shape function"""
        return amp * gamma**2 / ((x - x0)**2 + gamma**2) + offset

    def find_peak(self, x_data, y_data):
        """Find peak using Lorentzian fit"""
        try:
            # Initial guess for parameters
            offset = np.min(y_data)
            amp = np.max(y_data) - offset
            x0 = x_data[np.argmax(y_data)]
            gamma = 0.1  # Initial guess for width
            
            # Fit Lorentzian
            popt, _ = curve_fit(self.lorentzian, x_data, y_data, 
                              p0=[amp, x0, gamma, offset],
                              maxfev=5000)
            
            # Get fitted parameters
            amp_fit, x0_fit, gamma_fit, offset_fit = popt
            
            # Generate fitted curve
            x_fit = np.linspace(np.min(x_data), np.max(x_data), 1000)
            y_fit = self.lorentzian(x_fit, *popt)
            
            return {
                'peak_position': x0_fit,
                'amplitude': amp_fit,
                'width': gamma_fit,
                'offset': offset_fit,
                'x_fit': x_fit,
                'y_fit': y_fit
            }
        
        except Exception as e:
            print(f"Error in peak finding: {str(e)}")
            return None

    def read_multiple_excel_files(self, folder_path, file_pattern='.csv', x_col=0, y_col=1):
        """Read multiple Excel or CSV files from a folder and sum their y columns linearly"""
        try:
            # List to store dataframes
            dataframes = []
            
            # Get all files in the folder that match the pattern
            file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                         if f.endswith(file_pattern)]
            
            if not file_paths:
                print(f"No {file_pattern} files found in {folder_path}")
                return None, None
                
            print(f"Reading {len(file_paths)} files from {folder_path}")
            
            # Read each file
            for file_path in file_paths:
                file_path = os.path.normpath(file_path)
                
                # Determine file type and read accordingly
                if file_path.endswith(('.xlsx', '.xls')):
                    data = pd.read_excel(file_path, header=None)
                elif file_path.endswith('.csv'):
                    data = pd.read_csv(file_path, header=None)
                else:
                    print(f"Unsupported file type: {file_path}")
                    continue
                
                dataframes.append(data)
            
            # Check if any valid dataframes were read
            if not dataframes:
                print("No valid files were read.")
                return None, None
            
            # Extract x and y columns from first file as reference
            x_data = dataframes[0].iloc[:, x_col].to_numpy()
            
            # Sum y columns from all files (linear summation instead of averaging)
            y_data_list = [df.iloc[:, y_col].to_numpy() for df in dataframes]
            y_data_summed = np.sum(y_data_list, axis=0)
            
            return x_data, y_data_summed
            
        except Exception as e:
            print(f"Error reading files: {str(e)}")
            return None, None

    def create_comparative_plot(self, x_data1, y_data1, x_data2, y_data2, 
                           folder1_name='Folder 1', folder2_name='Folder 2',
                           xlabel='ppm', ylabel='Signal',
                           color1='blue', color2='red',
                           marker1='o-', marker2='s-',
                           markersize=3):
        """Create a comparative plot with data from two different folders"""
        fig, ax = plt.subplots()
        # Plot data from second folder
        ax.plot(x_data2, y_data2, marker2, color=color2, markersize=markersize, 
                label=folder2_name)
        # Plot data from first folder
        ax.plot(x_data1, y_data1,  '-', color=color1, markersize=markersize, 
                label=folder1_name)
        
        
    
        # Find and analyze peaks
        peak_data1 = self.find_peak(x_data1, y_data1)
        peak_data2 = self.find_peak(x_data2, y_data2)
        
        # Plot peak fits if 
        if peak_data2:
            ax.plot(peak_data2['x_fit'], peak_data2['y_fit'], '--', color=color2, alpha=0.7, 
                   linewidth=0.8)
        if peak_data1:
            ax.plot(peak_data1['x_fit'], peak_data1['y_fit'], '--', color=color1, alpha=0.7, 
                   linewidth=0.8)
            
        
        
        # Customize plot
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.minorticks_on()
        ax.legend(loc='best', frameon=False)
    
        # Adjust layout
        plt.tight_layout(pad=0.4)
    
        return fig, ax, peak_data1, peak_data2


# Example usage
def main():
    # Initialize plotter
    plotter = DataPlotter()
    
    # Define folder paths
    folder1_path = r"/Users/runzhaoguo/Documents/MQST-UCLA/411/A_Final_Report/exp_data_C/CPMG_Had(1).csv"
    folder2_path =  r"/Users/runzhaoguo/Documents/MQST-UCLA/411/A_Final_Report/exp_data_C/CPMG_Had(1).csv"
    
    # Set folder display names
    folder1_name = os.path.basename(folder1_path)
    folder2_name = os.path.basename(folder2_path)
    
    # Read and sum data from the first folder
    x_data1, y_data1 = plotter.read_multiple_excel_files(folder1_path, file_pattern='.csv')
    # y_data1 = y_data1*0.5
    # Read and sum data from the second folder
    x_data2, y_data2 = plotter.read_multiple_excel_files(folder2_path, file_pattern='.csv')
    
    if (x_data1 is not None and y_data1 is not None and 
        x_data2 is not None and y_data2 is not None):
        
        # Create comparative plot
        fig, ax, peak_data1, peak_data2 = plotter.create_comparative_plot(
            x_data1, y_data1, x_data2, y_data2,
            folder1_name='', folder2_name='',
            color1='black', color2='red'
        )
        
        # Set x-axis limits (same as original)
        plt.xlim(20, 60)
        
        # Print peak analysis results
        print(f"\nPeak Analysis Results for {folder1_name}:")
        if peak_data1:
            print(f"Peak Position: {peak_data1['peak_position']:.4f}")
            print(f"Peak Width (HWHM): {peak_data1['width']:.4f}")
            print(f"Peak Amplitude: {peak_data1['amplitude']:.4f}")
            print(f"Baseline Offset: {peak_data1['offset']:.4f}")
        
        print(f"\nPeak Analysis Results for {folder2_name}:")
        if peak_data2:
            print(f"Peak Position: {peak_data2['peak_position']:.4f}")
            print(f"Peak Width (HWHM): {peak_data2['width']:.4f}")
            print(f"Peak Amplitude: {peak_data2['amplitude']:.4f}")
            print(f"Baseline Offset: {peak_data2['offset']:.4f}")
        
        # Save plot with higher DPI and tight layout
        plt.savefig('plot.png', dpi=600, bbox_inches='tight', format='png')
        
        # Show plot
        plt.show()
    else:
        print("Could not create comparative plot due to missing data.")

if __name__ == "__main__":
    main()