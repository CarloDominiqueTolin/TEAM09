#https://medium.com/@itberrios6/introduction-to-motion-detection-part-1-e031b0bb9bb2

import cv2
import numpy as np

import sys
sys.path.append("C:/Users/user/Documents/Carlo Pogi/pI2")

from pi2py2 import *
pi = Pi2()

import matplotlib.pyplot as plt

def plot_histogram(image, title):
    hist, bins = np.histogram(image, bins=256, range=[-1, 1])
    
    # Plot histogram using Matplotlib
    plt.figure()
    plt.title(title)
    plt.xlabel('Intensity Value')
    plt.ylabel('Pixel Count')
    plt.plot(bins[:-1], hist)  # bins[:-1] to match the number of hist values
    plt.xlim([-1, 1])
    plt.show()


def mce_thresholding(x):
    mce_tresh = 0.25
    binary_mask = np.where(x < mce_tresh, 1.0, 0.0)
    print(binary_mask.shape)
    cv2.imshow("Mask",binary_mask)
    return binary_mask

def fixed_thresholding(x):
  unimodal_tresh = 0.250
  binary_mask = np.where(x < unimodal_tresh, 255, 0)
  return binary_mask


def hyta(x):
  std_thres = 0.03
  std = np.std(x)
  if std>std_thres:
    print("Bimodal",std)
    return (mce_thresholding(x))
  else:
    print("Unimodal",std)
    return(fixed_thresholding(x))


if __name__ == "__main__":
    # Path to the video file
    video_path = '5288342-sd_960_540_30fps.mp4'

    # Define the new dimensions for resizing
    new_width = 640
    new_height = 480

    # Create a VideoCapture object
    cap = cv2.VideoCapture(video_path)

    # Check if the video file was opened successfully
    if not cap.isOpened():
        print("Error: Could not open video file.")
        exit()

    # Read the first frame
    ret, prev_frame = cap.read()
    if not ret:
        print("Error reading first frame")
        exit()

    # Read until video is completed
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret:
            # Display the current frame
            resized_frame1 = cv2.resize(prev_frame, (new_width, new_height))
            resized_frame2 = cv2.resize(frame, (new_width, new_height))

            resized = cv2.resize(frame, (new_width, new_height))
            b, g, r = cv2.split(resized)
            r[r==0] = 1
            x = b/r
            n = (x-1)/(x+1)

            #plot_histogram(n,"Normalized B/R")

            cv2.imshow("Raw",resized)
            #cv2.imshow('HYTA',hyta(n))
            hyta(n)

            # Store the current frame as previous frame for the next iteration
            prev_frame = frame

            # Press Q on keyboard to exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break

    # Release the video capture object
    cap.release()

    # Close all OpenCV windows
    cv2.destroyAllWindows()