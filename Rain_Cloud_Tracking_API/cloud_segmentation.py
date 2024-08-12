#https://medium.com/@itberrios6/introduction-to-motion-detection-part-1-e031b0bb9bb2

import cv2
import numpy as np
import matplotlib.pyplot as plt
from patchify import patchify
import os
from skimage.filters import threshold_otsu


def hyta_segmentation(image, save=False, output_name=None, verbose=False, STD_THRESHOLD = 0.3):
    b, g, r = cv2.split(image)
    r[r==0] = 1
    x = b/r
    n = (x-1)/(x+1)
    
    # Generate a histogram and bin edges
    hist, bins = np.histogram(n, bins=256, range=[0, 1])
    # Calculate the bin midpoints
    bin_mids = (bins[:-1] + bins[1:]) / 2
    
    std = np.std(x)
    if std>STD_THRESHOLD:
        # Apply Otsu's thresholding method directly to the image
        otsu_threshold = threshold_otsu(n)
        binary_threshold = otsu_threshold
        if verbose:
            print(f"Bimodal Image with STD: {std}")
            print('Otsu\'s threshold value:', binary_threshold)
    else:
        binary_threshold = 0.250
        if verbose:
            print(f"Unimodal Image with STD: {std}")
            print('Fixed threshold value:', binary_threshold)
            
    output = np.where(n < binary_threshold, 255, 0)
        
    # Plot histogram and threshold
    if verbose:
        plt.figure(figsize=(10, 6))
        plt.bar(bin_mids, hist, width=0.005, alpha=0.7, color='blue')
        plt.axvline(binary_threshold, color='red', linestyle='dashed', linewidth=2)
        plt.title('HYTA Thresholding')
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.show()
        cv2.imshow("Segmented",output)
    
    if save:
        print(f"Saving to {output_name}")
        cv2.imwrite(output_name, output)
    
    return output


def video_demo():
    # # Path to the video file
    video_path = 'timelapse/4899355-uhd_3840_2160_30fps.mp4'

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
            resized = cv2.resize(frame, (new_width, new_height))
            cloud = hyta_segmentation(resized)

            cv2.imshow("Raw",resized)
            cv2.imshow('HYTA',cloud)

            # Press Q on keyboard to exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break

    # Release the video capture object
    cap.release()

    # Close all OpenCV windows
    cv2.destroyAllWindows()
    

def jaccard_index(ground_truth, predicted):
    """
    Compute the Jaccard Index between two binary mask images.
    
    Parameters:
    ground_truth (np.array): Binary mask image representing the ground truth.
    predicted (np.array): Binary mask image representing the predicted segmentation.
    
    Returns:
    float: Jaccard Index (IoU) score.
    """
    intersection = np.logical_and(ground_truth, predicted).sum()
    union = np.logical_or(ground_truth, predicted).sum()
    return intersection / union if union != 0 else 0


def evaluate_segmentation(raw_image, ground_truth_image, display=False):
    """
    Evaluate cloud segmentation using the Hybrid Thresholding Algorithm (HYTA).

    This function reads a raw input image and its corresponding ground truth 
    segmentation mask, applies the HYTA to segment clouds, and calculates the 
    Jaccard Index (IoU) to assess the segmentation accuracy. It also displays 
    the raw image, ground truth mask, and segmented image for visual inspection.

    Parameters:
    raw_image (str): Path to the raw input image.
    ground_truth_image (str): Path to the ground truth segmentation mask image.

    Returns:
    None
    """
    # Load the raw image
    raw = cv2.imread(raw_image)
    
    # Load and process the ground truth image
    ground_truth = cv2.imread(ground_truth_image, cv2.IMREAD_GRAYSCALE)

    # Apply HYTA segmentation to the raw image
    predicted = hyta_segmentation(raw)

    # Calculate and print the IoU score
    iou_score = jaccard_index(ground_truth, predicted)

    # Display the images
    if display:
        while True:
            cv2.imshow("Raw", raw)
            cv2.imshow("Ground Truth", ground_truth)
            cv2.imshow("HYTA Segmented", predicted)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        # Close all OpenCV windows
        cv2.destroyAllWindows()
    
    return iou_score


def patches_from_video(video_path, output_folder):
    cap = cv2.VideoCapture(video_path)

    ret, frame = cap.read()
    count = 1
    patch_num = 0
    while ret:
        ret, frame = cap.read()

        if count%30 == 0:
            print(count)

            patches = patchify(frame, (512, 512, 3), step=512)
            num_patches = patches.shape[0] * patches.shape[1]

            for i in range(patches.shape[0]):
                for j in range(patches.shape[1]):
                    patch = patches[i, j, 0]  # Extract the patch
                    patch_filename = os.path.join(output_folder, f'patch_{patch_num}.jpg')
                    cv2.imwrite(patch_filename, patch)
                    patch_num += 1
        
        count += 1


    print(f"Total patches saved: {patch_num}")
    

def compute_iou(pred_mask, gt_mask):
    intersection = np.logical_and(pred_mask, gt_mask).sum()
    union = np.logical_or(pred_mask, gt_mask).sum()
    if union == 0:
        return 1 if np.array_equal(pred_mask, gt_mask) else 0
    return intersection / union

def precision_recall_at_thresholds(iou_values, thresholds):
    precisions = []
    recalls = []

    for t in thresholds:
        tp = np.sum(iou_values >= t)
        fp = np.sum(iou_values < t)
        fn = len(iou_values) - tp
        precision = tp / (tp + fp) if tp + fp > 0 else 0
        recall = tp / (tp + fn) if tp + fn > 0 else 0
        precisions.append(precision)
        recalls.append(recall)

    return precisions, recalls

def average_precision(precisions, recalls):
    # Ensure precision is a monotonically decreasing function of recall
    precisions = np.array(precisions)
    recalls = np.array(recalls)
    for i in range(len(precisions) - 1, 0, -1):
        precisions[i - 1] = max(precisions[i - 1], precisions[i])

    # Integrate the precision-recall curve
    indices = np.where(recalls[1:] != recalls[:-1])[0] + 1
    average_precision = np.sum((recalls[indices] - recalls[indices - 1]) * precisions[indices])

    return average_precision

def mean_average_precision(pred_masks, gt_masks, thresholds=np.arange(0.5, 1.0, 0.05)):
    aps = []
    for pred_mask, gt_mask in zip(pred_masks, gt_masks):
        iou = compute_iou(pred_mask, gt_mask)
        precisions, recalls = precision_recall_at_thresholds([iou], thresholds)
        ap = average_precision(precisions, recalls)
        aps.append(ap)
    return np.mean(aps)



def test_segmentation(image_path):
    while True:
        cv2.imshow(
            "HYTA Segmented",
            hyta_segmentation(cv2.imread(image_path), verbose=True) 
        )
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    #video_demo()
    #image_demo('segmentation_dataset/Raw/B14.jpg','segmentation_dataset/Ground_truth/B14_3GT.png')
    #patches_from_video('timelapse/856171-hd_1920_1080_30fps.mp4', 'patches')
    #test_segmentation('HYTA/images/U3.jpg')

    #Find IOU in each image data
    '''
    for file in os.listdir("HYTA/3GT"):
        print(file, evaluate_segmentation(f"HYTA/images/{file.split('_')[0]}.jpg",f'HYTA/converted3GT/{file}'))
    '''
    
    #Generate Pred Masks
    '''
    for file in os.listdir("HYTA/images"):
        hyta_segmentation(
            cv2.imread(f"HYTA/images/{file}"), 
            save=True, 
            output_name=f"HYTA/pred_mask/{file.split('.')[0]}_pred.png",
            #verbose=True
        )
    '''
    
    # Example usage
    # pred_masks = [...]  # List of predicted masks
    # gt_masks = [...]    # List of ground truth masks

    # mAP = mean_average_precision(pred_masks, gt_masks)
    # print(f"Mean Average Precision (mAP): {mAP}")
    
    #Convert 3GT to 2GT
    '''
    for file in os.listdir("HYTA/3GT"):
        ground_truth = cv2.imread(f"HYTA/3GT/{file}", cv2.IMREAD_GRAYSCALE)
        cv2.imwrite(f"HYTA/converted3GT/{file}", np.where(ground_truth == 0, 0, 255).astype(np.uint8))
        print(f"Created Mask: {file}")
    '''
    
    #Mean Average Precision
    pred_masks = [cv2.imread(f'HYTA/pred_mask/{i}') for i in os.listdir("HYTA/pred_mask")]
    gt_masks = [cv2.imread(f'HYTA/converted3GT/{i}') for i in os.listdir("HYTA/converted3GT")]
    print('Mean Average Precision:',mean_average_precision(pred_masks, gt_masks))
    