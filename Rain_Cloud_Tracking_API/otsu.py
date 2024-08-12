import numpy as np
import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu

# Generate synthetic bimodal data
data1 = np.random.normal(20, 5, 1000)
data2 = np.random.normal(60, 5, 1000)
data = np.concatenate([data1, data2])

# Calculate Otsu's threshold
otsu_threshold = threshold_otsu(data)

# Plot histogram and threshold
plt.hist(data, bins=50, alpha=0.7, color='blue')
plt.axvline(otsu_threshold, color='red', linestyle='dashed', linewidth=2)
plt.title('Otsu\'s Thresholding')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.show()

print('Otsu\'s threshold value:', otsu_threshold)