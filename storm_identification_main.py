import sys
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, filters, segmentation, measure

storm_img = sys.argv[1] 

def process_storm():
    global storm_img
    radar_img = io.imread(storm_img)
    radar_img_gray = io.imread(storm_img, as_gray=True)
    edges = filters.sobel(radar_img_gray)

    # Apply thresholding to identify regions of interest
    thresh = filters.threshold_otsu(edges)
    binary = edges > thresh

    # Label regions
    label_image = measure.label(binary)

    # Identify severe storms
    regions = measure.regionprops(label_image)
    severe_regions = []
    for region in regions:
        # Calculate the area and perimeter of each region
        area = region.area
        perimeter = region.perimeter
        # Check if the region meets the criteria for a severe storm
        if area >= 1000 and perimeter >= 100:
            severe_regions.append(region)

    # Classify severe storms based on hail, tornado, and strong wind threat
    for region in severe_regions:
        # Extract the region from the original image
        region_img = np.zeros_like(radar_img)
        region_img[label_image == region.label] = 1
        region_img = np.multiply(radar_img, region_img)
        # Apply segmentation to identify hail, tornado, and strong wind threat
        segmented_img = segmentation.slic(region_img, compactness=10, n_segments=4)
        # Calculate the mean intensity of each segment
        segment_intensities = []
        for i in range(4):
            mean_intensity = np.mean(region_img[segmented_img == i])
            segment_intensities.append(mean_intensity)
        # Classify the severe storm based on the segment intensities
        if segment_intensities[0] > 0.5:
            print('Severe storm with hail detected')
        elif segment_intensities[1] > 0.5:
            print('Severe storm with tornado detected')
        elif segment_intensities[2] > 0.5 or segment_intensities[3] > 0.5:
            print('Severe storm with strong wind threat detected')
        else:
            print('Severe storm detected, but no hail, tornado, or strong wind threat detected')

process_storm()