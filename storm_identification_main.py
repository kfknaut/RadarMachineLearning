#%%
import cv2, os, glob, h5py, pickle, itertools,gc, imageio
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import canny
import skimage.segmentation
import skimage.color
import configparser

from sklearn.cluster import KMeans
from skimage import io, exposure, filters, measure
from skimage.filters import roberts, sobel
from skimage.transform import rescale
from PIL import Image, ImageDraw
from shapely.geometry import Polygon
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini')
individual_path = config['Directories']['radardump']
if not os.path.exists(f"{individual_path}\\scraped_individual"):
    os.makedirs(f"{individual_path}\\scraped_individual")

training_data = 'storm_training_dataset.hdf5'

def add_to_dataset(image, labels, dataset_file):
    with h5py.File(dataset_file, 'a') as f:
        image_dataset = f['images']
        num_image = len(image_dataset)
        print("Making an attempt")
        try:
            img_array = np.asarray(image)
            if img_array.shape[-1] == 4:
                img_array = img_array[:, :, :3]

            img_array = np.expand_dims(img_array, axis=0)

            image_dataset.resize(num_image+1, axis=0)
            image_dataset[-1:] = img_array

            gc.collect()
        except:
            print("Failed to load image:", image)

def pixelate(image, pixel_size):
    if not isinstance(image, Image.Image):
        image = Image.open(image)
    
    width, height = image.size
    x_pixels = width // pixel_size
    y_pixels = height // pixel_size

    pixelated_image = image.resize((x_pixels, y_pixels), Image.NEAREST)
    pixelated_image = pixelated_image.resize((width, height), Image.NEAREST)

    return pixelated_image

def run_scraped_data(scraped_image, radar_site):
    print("Entering scraped run")
    extraction = scraped_image.split('\\')[-1][3:]
    extraction = extraction[4:]
    imported = Image.open(scraped_image)
    original = np.copy(imported)
    cover = Image.open("scraper_mask.png").convert("RGBA")
    imported.paste(cover, (0, 0), cover)
    imported.save("masked_scrape.png")
    print("Image mask applied")

    img = Image.open("masked_scrape.png")
    colors_to_remove = [[230, 0, 0, 255], [255, 255, 0, 255], [112, 219, 147, 255], [255, 171, 127, 255]]
    print("masked scrape open, image array next")
    background_color = (0, 0, 0, 255) 
    img_array = np.array(img)

    for color in colors_to_remove:
        print("Removing")
        mask = np.all(img_array == color, axis=-1)
        img_array[mask] = background_color
        print("img array")
        
    print("img_array made")
    modified_img = Image.fromarray(img_array[:, :, :3], mode='RGB')
    modified_img.save("modified_scraped_image.png")
    print("About to dim image")           
    
    #hsv_img = cv2.cvtColor(img_array, cv2.COLOR_BGR2HSV)
    #h, s, v = cv2.split(hsv_img)
    #inv_h = h - 120
    #inv_hsv_img = cv2.merge((inv_h, s, v))

    #b, g, r = cv2.split(img_array)
    rimg = cv2.imread('modified_scraped_image.png')
    b, g, r = cv2.split(rimg)
    _, mask = cv2.threshold(r, 150, 255, cv2.THRESH_BINARY)
    red_only = cv2.bitwise_and(rimg, rimg, mask=mask)

    hsv = cv2.cvtColor(red_only, cv2.COLOR_BGR2HSV)
    hue = hsv[:,:,0] + 80
    saturation = hsv[:,:,1] * 1.5
    hue = np.clip(hue, 0, 255).astype(np.uint8)
    saturation = np.clip(saturation, 0, 255).astype(np.uint8)
    hsv[:,:,0] = hue
    hsv[:,:,1] = saturation
    output = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    dim = exposure.adjust_gamma(output, gamma = 10)
    imageio.imwrite('gamma_corrected_image.png', dim)

    img_smooth = cv2.GaussianBlur(dim, (15, 15), 0)
    imported_masked = Image.fromarray(np.uint8(img_smooth))
    gray = cv2.cvtColor(np.array(imported_masked), cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)

    kernel = np.ones((10,10), np.uint8) 
    thresh = cv2.dilate(thresh, kernel, iterations=2)
    cv2.imwrite('threshold.png', thresh)
    cv2.imwrite('gray.png', gray)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    img_boxes = cv2.cvtColor(np.array(original), cv2.COLOR_RGBA2RGB)
    print("About to run save_dir")

    save_dir = f"{individual_path}\\scraped_individual\\{radar_site}"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for img in os.listdir(save_dir):
        img_path = os.path.join(save_dir, img)
        if os.path.isfile(img_path) and img !='storm_data.txt':
            os.remove(img_path)
    
    storm_data_file = os.path.join(save_dir, 'storm_data.txt')

    if not os.path.exists(storm_data_file):
        with open(storm_data_file, 'w') as f:
            print("Doesn't exist, making the data file")
            f.write("")
    strm_count = 1
    for idx, cnt in enumerate(contours):
        try:
            area = cv2.contourArea(cnt)
            if area > 600: 
                x, y, w, h = cv2.boundingRect(cnt)
                color = tuple(np.random.randint(0, 255, 3).tolist())  
                img_boxes = cv2.rectangle(img_boxes, (x, y), (x + w, y + h), (255, 210, 210), 2)
                aspect_ratio = 3/2

                center_x = x + w/2
                center_y = y + h/2
                
                bearing = 0
                with open(storm_data_file, 'a') as f:
                    f.write(f"STRM_{strm_count}, {center_x},{center_y}, {bearing}\n")

                print(f"Storm {strm_count} is centered at {center_x},{center_y}")

                if w > h:
                    zoom_width = w
                    zoom_height = w
                else:
                    zoom_height = h
                    zoom_width = h

                left = int(center_x - zoom_width/2)
                right = int(center_x + zoom_width/2)
                top = int(center_y - zoom_height/2)
                bottom = int(center_y + zoom_height/2)

                if top < 0:
                    bottom += abs(top)
                    top = 0

                zoomed_img = None
                if top < bottom and left < right:
                    cropped_array = img_array[top:bottom, left:right]
                    if cropped_array.shape[0] > 0 and cropped_array.shape[1] > 0:
                        zoomed_img = Image.fromarray(cropped_array)
                        square_img = zoomed_img.crop((0, 0, min(zoomed_img.size), min(zoomed_img.size)))
                        resized_img = square_img.resize((369, 369))

                c_time = datetime.today().strftime("%m_%d_%Y")
                cv2.putText(img_boxes, f"STRM_{strm_count}_{c_time}", (int(x), int(y) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 222, 222), 1)
                #label = f"STRM_{idx}{len(contours)}" 
                #draw = ImageDraw.Draw(resized_img)
                #draw.text((10, 10), label, fill=(255, 255, 255)) 

                filename = f"STRM_{strm_count}_{c_time}.png"
                filepath = os.path.join(save_dir, filename)
                print(f"Saved to {filepath}")
                resized_img.save(filepath)
                print(f"Storm number {strm_count}")
                strm_count +=1
        except:
            print("Failed to save specific storm")
    try:
        c_time = datetime.today().strftime("%m_%d_%Y")
        plt.imshow(img_boxes)
        plt.axis("off")
        plt.savefig(os.path.join(individual_path, c_time,f'{radar_site}_bxed-bas{extraction}.png'), dpi=243.5, bbox_inches='tight', pad_inches=0)
    except:
        c_time = datetime.today().strftime("%m_%d_%Y")
        print("No storms found")
        output_p = os.path.join(individual_path, c_time,f'{radar_site}_bxed-bas{extraction}.png')
        np.array(original).tofile(output_p)

    for filename in os.listdir(save_dir):
        file_path = os.path.join(save_dir, filename)
        img = skimage.io.imread(file_path)
        if img.shape[2] == 4:
            img = skimage.color.rgba2rgb(img)

        v_min, v_max = np.percentile(img, (88, 99))
        grsca = skimage.color.rgb2gray(img)
        contr = exposure.rescale_intensity(grsca, in_range=(v_min, v_max), out_range=(-50, 50))

        is_black = np.all(img == 0, axis=-1)
        contr[is_black] = np.nan
        num_levels = 1
        img_quant = np.floor(contr * num_levels) / num_levels
        img_quant[is_black] = 0

        pix = pixelate(Image.fromarray((img_quant*255).astype(np.uint8)), 4)
        pix = np.array(pix) / 255.0

        strm_edges = skimage.filters.sobel(pix)
        threshold_v = 0.1 * np.max(strm_edges)
        binary = strm_edges > threshold_v

        storm_shape = np.zeros_like(grsca)
        storm_shape[binary] = grsca[binary]

        plt.imshow(storm_shape, cmap='gray')
        plt.axis('off')
        #plt.show()

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

    dim = exposure.adjust_gamma(img_col, gamma = 4)

    v_min, v_max = np.percentile(img, (38, 99))
    contr = exposure.rescale_intensity(img, in_range=(v_min, v_max), out_range=(-50, 50))

    r = roberts(contr)

    filtered = filters.median(filters.median(filters.median(r)))
    final = canny(filtered, sigma = 3)
    sob = sobel(final)

    # --------------------- warning edge finder and precip intensity ---------------------------
    lower_red_color = np.array([222, 0, 0])
    upper_red_color = np.array([224, 5, 5])

    lower_yellow_color = np.array([210, 210, 0])
    upper_yellow_color = np.array([225, 230, 5])

    red_mask = cv2.inRange(img_col, lower_red_color, upper_red_color)
    yellow_mask = cv2.inRange(img_col, lower_yellow_color, upper_yellow_color)
    selected_pixels = cv2.bitwise_or(red_mask, yellow_mask)

    selected_pixels_img = np.zeros_like(img[:, :])
    selected_pixels_img[selected_pixels > 0] = 255

    padding = 3
    selected_pixels_img = cv2.copyMakeBorder(selected_pixels_img, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=0)

    kernel = np.ones((3, 3), np.uint8)
    selected_pixels_img = cv2.dilate(selected_pixels_img, kernel, iterations=1)

    selected_pixels_img = cv2.threshold(selected_pixels_img, 0, 255, cv2.THRESH_BINARY)[1]

    contours = measure.find_contours(selected_pixels_img, 0.5)

    max_area = 0
    largest_contour = None
    for contour in contours:
        if contour[0, 0] == contour[-1, 0] and contour[0, 1] == contour[-1, 1]:
            polygon = Polygon(contour)
            area = polygon.area
            if area > max_area:
                max_area = area
                largest_contour = contour
                
    #print(largest_contour)

    min_x, min_y = np.min(largest_contour, axis=0)
    max_x, max_y = np.max(largest_contour, axis=0)
    width = int(max_x - min_x)
    height = int(max_y - min_y)
    print(f"W: {width} H: {height}")
    if width > height:
        padding = (width/2) + 100
    else:
        padding = (height/2) + 100

    center_x, center_y = ((min_x + max_x) / 2) - 50 , ((min_y + max_y) / 2) - 50

 
    img_h = max_y/2
    if height > img_h:
        padding = img_h
    print(f"Center is at:X:{center_x},{center_y}")
    new_min_x, new_min_y = center_x - padding, center_y - padding
    new_max_x, new_max_y = center_x + padding, center_y + padding
    print("MaxMin")
    fig, ax = plt.subplots()
    ax.imshow(img_col[int(new_min_x):int(new_max_x), int(new_min_y):int(new_max_y)], cmap=plt.cm.gray, extent=(new_min_y, new_max_y, new_max_x, new_min_x))
    ax.plot(largest_contour[:, 1], largest_contour[:, 0], linewidth=0)
    print("AXIMSHOW")
    ax.add_patch(
        plt.Rectangle(
            (new_min_y, new_min_x), 
            new_max_y - new_min_y,
            new_max_x - new_min_x, 
            fill=False,
            edgecolor='black',
            linewidth=0,
        )
    )
    print (f"New center: {(new_min_x + new_max_x)/2},{(new_min_y + new_max_y)/2}")
    print("ADDEDPATCH")
    ax.grid(False)
    ax.axis('image')
    ax.set_xticks([])
    ax.set_yticks([])
    print("About to save cropped col")
    plt.savefig('cropped_img_col.png', bbox_inches='tight', pad_inches=0)

    plt.imshow(img_col[int(new_min_x):int(new_max_x), int(new_min_y):int(new_max_y)], cmap=plt.cm.gray)
    plt.plot(largest_contour[:, 1], largest_contour[:, 0], linewidth=2)
    plt.axis('off')
    #plt.show()

    cropped = dim[int(new_min_x) :int(new_max_x), int(new_min_y):int(new_max_y)]
    plt.imshow(selected_pixels_img, cmap = plt.cm.gray)
    plt.axis('off')
    plt.savefig('cropped_dim.png', bbox_inches='tight', pad_inches=0)
    find_highest_precipitation(colormap,'cropped_dim.png')
    #plt.show()
    print("About to run storm edges")
    # ------------------------------- storm edges ----------------------------------------
    grsc = skimage.color.rgb2gray(cropped)
    strm_edges = skimage.filters.sobel(grsc)
    threshold_v = 0.001
    binary = strm_edges > threshold_v

    storm_shape = np.zeros_like(grsc)
    storm_shape[binary] = grsc[binary]

    plt.imshow(storm_shape, cmap='gray')
    plt.savefig('train_img.png', bbox_inches='tight', pad_inches=0)
    plt.axis('off')
    #plt.show()
    img_t = Image.open('train_img.png')
    print("exiting image aquisition")
    return img_t

def identify_to_train(start_index, data_dir):
    global training_data
    sub_dirs = ['Hail', 'HailAndWind', 'Tornado', 'TornadoAndHail', 'TornadoAndHailAndWind', 'TornadoAndWind', 'Wind']
    unverified_dir = os.path.join(data_dir, 'Unverified')
    verified_dir = os.path.join(data_dir, 'Verified')
    product = itertools.product([unverified_dir, verified_dir], sub_dirs)

    for index, (dir_path, sub_dir) in enumerate(product, start=start_index):
        for sub_dir in sub_dirs:
            sub_dir_path = os.path.join(dir_path, sub_dir)
            file_paths = glob.glob(os.path.join(sub_dir_path, '*.png'))
            num_batches = int(np.ceil(len(file_paths) / 32))

            for batch_idx in range(num_batches):
                batch_file_paths = file_paths[batch_idx * 32:(batch_idx + 1) * 32]
                batch_images = []

                for file_path in batch_file_paths:
                    index+=1
                    print(file_path)
                    label = sub_dir
                    try:
                        manipulated_image = run_training_data(file_path)
                        add_to_dataset(manipulated_image, label, training_data)
                        print(f"Added storm number {index}")
                    except:
                        print(f"Failed to process image: {file_path}")

                    with open('last_index.txt', 'w') as f:
                        f.write(f"{index}\n{file_path}\n")

                    if index >= 250:
                        gc.collect()
                        index = 0

if os.path.exists('location.pickle'):
    with open('location.pickle', 'rb') as f:
        start_index = pickle.load(f)
else:
    start_index = 0

#identify_to_train(0, "E:\TrainingData")

def identify_couplets(velocity,cc):
    print("couplet")

def identify_hail(vil, echo):
    ind_vil = 0
    ind_echo = 0
    hail_size = 0.0028 * ind_vil**0.734 * (ind_echo - 18)^0.88
    print("hail")

#identify_to_train()
#run_training_data('sample.png')
#run_scraped_data('testimg_2.png')
# %%
