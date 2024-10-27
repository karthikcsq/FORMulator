import numpy as np
import matplotlib.pyplot as plt

from skimage import transform
from skimage.io import imread, imshow
import cv2

# -----------> HOMOGRAPHY ATTEMPT | IT FAILED <-------------

monopoly = imread('monopoly.jpg')

imshow(monopoly)

# Convert the image from BGR to RGB for proper visualization with Matplotlib
monopoly = cv2.cvtColor(monopoly, cv2.COLOR_BGR2RGB)

# Define the source points
src = np.array([281, 115,
                1450, 616,
                248, 632,
                1292, 106,
]).reshape((4, 2))

# Plot the image
# plt.imshow(monopoly)

# Plot the points on the image with red color
plt.scatter(src[:, 0], src[:, 1], color='red', marker='o')

# Show the image with the plotted points
plt.show()

dst = np.array([0, 100,
                1500, 1000,
                0, 1000,
                1500, 100,
]).reshape((4, 2))
tform = transform.estimate_transform('projective', src, dst)

tf_img = transform.warp(monopoly, tform.inverse)
fig, ax = plt.subplots()
ax.imshow(tf_img)
_ = ax.set_title('projective transformation')

plt.imshow(tf_img)

cv2.imwrite("newImg.jpg", tf_img)




