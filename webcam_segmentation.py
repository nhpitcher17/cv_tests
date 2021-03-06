import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pygame.camera
import pygame.image
import time

from skimage import io, exposure
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import closing, square
from skimage.color import label2rgb, rgb2gray
from skimage.transform import downscale_local_mean

def capture_image():
    t0 = time.time()
    # # capture image from webcam
    pygame.camera.init()
    my_cam = pygame.camera.list_cameras().pop()
    cam = pygame.camera.Camera(my_cam)
    cam.start()
    img = cam.get_image()
    pygame.image.save(img, "photo.bmp")
    pygame.camera.quit()

    t1 = time.time()
    capture_time = t1-t0
    print("Image capture time: ", capture_time)

    return capture_time

def segment_photo_bmp():
    # begin timing
    t0 = time.time()
    # begin segmentation process
    # make sure there's an image to segment
    try:
        im_file = io.imread("photo.bmp")
    except:
        capture_image()
    t1 = time.time()
    # scaled = downscale_local_mean(im_file, (1, 1, 1))
    # image = scaled[:, :, 2]
    img = rgb2gray(im_file)
    # io.imsave("images/webcam_test.png", image)
    image = exposure.adjust_gamma(img, 2)
    # Logarithmic
    # logarithmic_corrected = exposure.adjust_log(img, 1)

    # apply threshold
    thresh = threshold_otsu(image)
    bw = closing(image > thresh, square(5))

    # remove artifacts connected to image border
    cleared = clear_border(bw)

    # label image regions
    label_image = label(cleared)
    t2 = time.time()
    seg_time = t2 - t1
    print("Segmentation time: ", t2 - t1)

    return label_image, image, t2 - t0

def region_centroids(labelled_image, min_area = 20):
    centroids = []
    for region in regionprops(labelled_image):
        # calculate centroid
        minr, minc, maxr, maxc = region.bbox
        centroid = (minc + 0.5*(maxc - minc), minr + 0.5*(maxr - minr))
        print("Centroid of blob: ", centroid)
        centroids.append(centroid)
    return centroids

def filter_regions(labelled_image, min_area = 20):
    filtered_labels = []
    for region in regionprops(labelled_image):
        # take regions with large enough areas
        if region.area >= min_area:
            filtered_labels.append(region)
    return filtered_labels

def save_segmented_image(regions, image):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(image)

    for region in regions:
            # draw rectangle around segmented coins
            minr, minc, maxr, maxc = region.bbox
            rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=2)
            ax.add_patch(rect)
            centroid = (minc + 0.5*(maxc - minc), minr + 0.5*(maxr - minr))
            circ = mpatches.Circle(centroid, radius = 5, fill=False, edgecolor='blue', linewidth=2)
            ax.add_patch(circ)

    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig("images/webcam_seg0.png")

if __name__ == "__main__":
    _ = capture_image()
    labelled_image, image, _ = segment_photo_bmp()
    filtered_regions = filter_regions(labelled_image, min_area = 2)
    image_label_overlay = label2rgb(labelled_image, image=image)
    save_segmented_image(filtered_regions, image_label_overlay)
    centroids = region_centroids(labelled_image)
