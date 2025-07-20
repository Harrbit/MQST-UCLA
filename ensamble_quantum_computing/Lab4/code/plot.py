import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import numpy as np

folder_path = '/Users/runzhaoguo/Documents/MQST-UCLA/411/A_Final_Report/exp_data/dj/4'  # Replace with your actual folder path

csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

common_freq = None
sum_intensity = None

for i, file in enumerate(csv_files):
    df = pd.read_csv(file)
    freq = df.iloc[:, 0].values
    intensity = df.iloc[:, 1].values

    if i == 0:
        common_freq = freq
        sum_intensity = intensity.copy()
    else:
        interp_intensity = np.interp(common_freq, freq, intensity)
        sum_intensity += interp_intensity
output_df = pd.DataFrame({'Frequency': common_freq, 'Summed Intensity': sum_intensity})
# output_df.to_csv('/Users/runzhaoguo/Documents/MQST-UCLA/411/A_Final_Report/exp_data_C/cnot_surgry/CNOT10/summed_intensity.csv', index=False)
plt.figure(figsize=(8, 6))
plt.plot(common_freq, sum_intensity, 'k.-')
plt.xlabel('Frequency', fontsize=16)
plt.xlim(0,10)
plt.ylabel('Intensity', fontsize=16)
# plt.title('c', fontsize=24)
plt.show()
