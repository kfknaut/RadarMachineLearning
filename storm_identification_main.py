#%%
import cv2
import os
import math
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import canny
import skimage.color
from skimage import io, exposure, filters, measure, draw
from skimage.filters import roberts, sobel, scharr, prewitt, gaussian
from skimage.transform import rescale, resize, resize_local_mean, downscale_local_mean
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import Polygon

import cv2
import numpy as np
from PIL import Image
from skimage import exposure
import matplotlib.pyplot as plt

def run_scraped_data(scraped_image):
    
    imported = Image.open(scraped_image)
    cover = Image.open("scraper_mask.png").convert("RGBA")
    imported.paste(cover, (0, 0), cover)
    imported.save("masked_scrape.png")

    img = Image.open("masked_scrape.png")
    colors_to_remove = [[230, 0, 0, 255], [255, 255, 0, 255], [112, 219, 147, 255], [255, 171, 127, 255]]

    img_array = np.array(img)
    for color in colors_to_remove:
        mask = np.all(img_array == color, axis=-1)
        img_array[np.where(mask)] = [0, 0, 0, 255]

    dim = exposure.adjust_gamma(img_array, gamma = 55)

    img_smooth = cv2.GaussianBlur(dim, (5, 5), 0)
    imported_masked = Image.fromarray(np.uint8(img_smooth))
    gray = cv2.cvtColor(np.array(imported_masked), cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)

    kernel = np.ones((5,5), np.uint8) 
    thresh = cv2.dilate(thresh, kernel, iterations=2)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    img_boxes = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2RGB)

    save_dir = "scraped_individual"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    for idx, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area > 600: 
            x, y, w, h = cv2.boundingRect(cnt)
            color = tuple(np.random.randint(0, 255, 3).tolist())  
            img_boxes = cv2.rectangle(img_boxes, (x, y), (x + w, y + h), (255, 210, 210), 2)
            aspect_ratio = 3/2

            center_x = x + w/2
            center_y = y + h/2

            if w > h:
                zoom_width = w + 40
                zoom_height = int(zoom_width / aspect_ratio)
            else:
                zoom_height = h + 40
                zoom_width = int(zoom_height * aspect_ratio)

            left = int(center_x - zoom_width/2)
            right = int(center_x + zoom_width/2)
            top = int(center_y - zoom_height/2)
            bottom = int(center_y + zoom_height/2)

            zoomed_img = Image.fromarray(img_array[top:bottom, left:right])
            zoomed_img = zoomed_img.resize((640, 480))

            filename = f"storm_{idx}.png"
            filepath = os.path.join(save_dir, filename)
            zoomed_img.save(filepath)


    plt.imshow(img_boxes)
    plt.axis("off")
    plt.savefig('overall_rad.png', dpi=300, bbox_inches='tight', pad_inches=0)


def run_training_data(training_image):
    colormap = [
    "#010101", # ND
    "#00A0A0", # 0
    "#0010CE", # 5
    "#0000CE", # 10
    "#00FF00", # 15
    "#003B00", # 20
    "#008e00", # 25
    "#FFFF00", # 30
    "#8D2E00", # 35
    "#FF0800", # 40
    "#FF0000", # 45
    "#590000", # 50
    "#2E0000", # 55
    "#FF00FF", # 60
    "#f800fd", # 65
    "#FFFFFF", # 70
    ]

    def find_highest_precipitation(colormap, img):
        image = Image.open(img)
        width, height = image.size
        highest_value = 0

        for y in range(height):
            for x in range(width):
                pixel = image.getpixel((x, y))
                pixel_color = tuple(pixel[:3])
                for i in range(len(colormap)-1, 0, -1):
                    colormap_color = tuple(int(colormap[i][j:j+2], 16) for j in (1, 3, 5))
                    if pixel_color == colormap_color:
                        value = i*5
                        if value > highest_value:
                            highest_value = value
                        break

        
        print("Highest precipitation value found in the image: ", highest_value)

    imported = Image.open(training_image)
    cover = Image.open('iowa_removal.png').convert("RGBA")

    imported.paste(cover, (0, 0), cover)
    imported.save('applied.png')

    img = io.imread("applied.png", as_gray = True)
    img_col = io.imread("applied.png")

    dim = exposure.adjust_gamma(img_col, gamma = 6)

    v_min, v_max = np.percentile(img, (38, 99))
    contr = exposure.rescale_intensity(img, in_range=(v_min, v_max), out_range=(-50, 50))

    resc = rescale(img, 1.0/3.0, anti_aliasing = True)
    r = roberts(contr)
    rr = sobel(r)
    e = canny(contr, sigma=1)
    re = roberts(e)

    filtered = filters.median(filters.median(filters.median(r)))
    final = canny(filtered, sigma = 3)
    sob = sobel(final)

    # --------------------- warning edge finder and precip intensity ---------------------------
    contours = measure.find_contours(sob, 0.1)

    max_area = 0
    largest_contour = None
    for contour in contours:
        if contour[0, 0] == contour[-1, 0] and contour[0, 1] == contour[-1, 1]:
            polygon = Polygon(contour)
            area = polygon.area
            if area > max_area:
                max_area = area
                largest_contour = contour

    print(largest_contour)

    min_x, min_y = np.min(largest_contour, axis=0)
    max_x, max_y = np.max(largest_contour, axis=0)
    width = int(max_x - min_x)
    height = int(max_y - min_y)
    print(f"W: {width} H: {height}")
    if width > height:
        padding = (width/2) + 100
    else:
        padding = (height/2) + 100

    center_x, center_y = (min_x + max_x) / 2, (min_y + max_y) / 2

    img_h = max_y/2
    if height > img_h:
        padding = img_h
    print(f"Center is at:X:{center_x},{center_y}")
    new_min_x, new_min_y = center_x - padding, center_y - padding
    new_max_x, new_max_y = center_x + padding, center_y + padding

    fig, ax = plt.subplots()
    ax.imshow(img_col[int(new_min_x):int(new_max_x), int(new_min_y):int(new_max_y)], cmap=plt.cm.gray, extent=(new_min_y, new_max_y, new_max_x, new_min_x))
    ax.plot(largest_contour[:, 1], largest_contour[:, 0], linewidth=2)
    ax.add_patch(
        plt.Rectangle(
            (new_min_y, new_min_x), 
            new_max_y - new_min_y,
            new_max_x - new_min_x, 
            fill=False,
            edgecolor='black',
            linewidth=2,
        )
    )
    ax.grid(False)
    ax.axis('image')
    ax.set_xticks([])
    ax.set_yticks([])

    plt.savefig('cropped_img_col.png', bbox_inches='tight', pad_inches=0)

    plt.imshow(img_col[int(new_min_x):int(new_max_x), int(new_min_y):int(new_max_y)], cmap=plt.cm.gray, extent=(new_min_y, new_max_y, new_max_x, new_min_x))
    plt.plot(largest_contour[:, 1], largest_contour[:, 0], linewidth=2)
    plt.axis('off')
    plt.show()

    cropped = dim[int(new_min_x):int(new_max_x), int(new_min_y):int(new_max_y)]
    plt.imshow(cropped, cmap = plt.cm.gray)
    plt.axis('off')
    plt.savefig('cropped_dim.png', bbox_inches='tight', pad_inches=0)
    find_highest_precipitation(colormap,'cropped_dim.png')
    plt.show()

    # ------------------------------- storm edges ----------------------------------------
    grsc = skimage.color.rgb2gray(cropped)
    strm_edges = skimage.filters.sobel(grsc)
    threshold_v = 0.001
    binary = strm_edges > threshold_v

    storm_shape = np.zeros_like(grsc)
    storm_shape[binary] = grsc[binary]

    plt.imshow(storm_shape, cmap='gray')
    plt.axis('off')
    plt.show()

run_training_data('sample.png')
run_scraped_data('testimg_2.png')
# %%
