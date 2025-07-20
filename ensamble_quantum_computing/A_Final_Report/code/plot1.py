import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
data = pd.read_csv('/Users/runzhaoguo/Documents/MQST-UCLA/411/A_Final_Report/exp_data_C/CPMG_Had(1).csv')

# Plot the data
data.plot(x=data.columns[0], y=data.columns[1], kind='line')  # Specify the x and y columns
plt.xlabel('Time(s)')  # Replace with your x-axis label
plt.ylabel('Amplitude')  # Replace with your y-axis label
# plt.title('Plot Title')  # Replace with your plot title
plt.show()
