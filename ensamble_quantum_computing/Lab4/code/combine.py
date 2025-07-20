import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Load the images
img1 = mpimg.imread('/Users/runzhaoguo/Documents/MQST-UCLA/411/A_Final_Report/exp_plot/CNOTC00.png')
img2 = mpimg.imread('/Users/runzhaoguo/Documents/MQST-UCLA/411/A_Final_Report/exp_plot/CNOTC01.png')
img3 = mpimg.imread('/Users/runzhaoguo/Documents/MQST-UCLA/411/A_Final_Report/exp_plot/CNOTC10.png')
img4 = mpimg.imread('/Users/runzhaoguo/Documents/MQST-UCLA/411/A_Final_Report/exp_plot/CNOTC11.png')

# Create a 2x2 grid
fig, axs = plt.subplots(2, 2, figsize=(10, 10))

# Show each image in a subplot
axs[0, 0].imshow(img1)
axs[0, 0].axis('off')  # Turn off axes if you don't want them

axs[0, 1].imshow(img2)
axs[0, 1].axis('off')

axs[1, 0].imshow(img3)
axs[1, 0].axis('off')

axs[1, 1].imshow(img4)
axs[1, 1].axis('off')

# Add a main title if needed
# plt.suptitle('CNOT', fontsize=16)

plt.tight_layout()
plt.show()

# Optionally, save the figure
# fig.savefig('combined_plot.png', dpi=300)
