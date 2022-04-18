# A development script to experiment on pulling Hue colors from splash art.
# This file uses the deprecated phue library, which uses the deprecated PHue art.

import requests
import random
import numpy as np
from PIL import Image
from io import BytesIO
from matplotlib import pyplot as plt
from phue import Bridge
from math import pow
from colorlib import *
from sklearn.cluster import MiniBatchKMeans
import time

# League constants
patch = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
data_dragon_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/"
# Hue constants
ip = "10.0.0.50"
active_IDs = [3,4,5]
username = "t9EuSmHFC2o7bTtt5Lyq5eUMKNU0otLLN4nHE9wO"
#lights = Bridge(ip=ip, username=username).get_light_objects('id')


# From a championID and skinID, get the url to query its splash art.
# If none is given, generate the url for a random skin's splash.
def splash_url(championID=None, skinID=None) -> str:
    if championID is None or skinID is None:
        allChampionData = requests.get(data_dragon_url+"champion.json").json()["data"]
        randomChampionID = random.choice(list(allChampionData.keys()))
        randomChampionData = requests.get(f"{data_dragon_url}champion/{randomChampionID}.json").json()
        numberOfSkins = len(randomChampionData["data"][randomChampionID]["skins"])
        randomSkinID = random.randint(0, numberOfSkins)
        championID = randomChampionID
        skinID = randomSkinID
    return f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{championID}_{skinID}.jpg"


# Fetch from url and return image as np array.
# Returns None if no image is found.
def load_image(url) -> np.ndarray:
    res = requests.get(url)
    if res.status_code != 200:
        return None
    img = np.array(Image.open(BytesIO(res.content)))
    return img

# TODO remove
# Given a color encoded in xyb, set a collection of lightIDs to that color
def set_xyb(IDs, xyb):
    for ID in IDs:
        lights[ID].xy = xyb[0:2]
        lights[ID].brightness = int(xyb[2])


#test = np.array([[[6*x+3*y, 8*x+4*y, 10*x+5*y] for x in range(3)] for y in range(3)])
#dim, test_flat = flatten_image(test)
#test_dupl = unflatten_image(dim, test_flat)



# TODO remove
def examine_color(R, G, B, bri=100) -> None:
    """
    Applies these colors to my hue lights at home.
    For testing only.
    Input: ints R, G, B in [0,255],
           int brightness in [0,100]
    """
    xyb = rgb_to_xyb(np.array([[[R,G,B]]]))
    print(xyb)
    set_xyb(active_IDs, [xyb[0][0], xyb[1][0], bri])


champion = "Corki"
skinID = 18
url = splash_url(champion, skinID)
threshold=0.3
print(url)
img = load_image(url)
if img is None:
    raise ImportError("Unable to fetch splash art for this skin!")

# TODO remove
def remove_dark_pixels(rgb, threshold=0.8):
    xyb = rgb_img_to_xyb_img(rgb)

    brightnesses = xyb[:,:,2]
    pixels_to_wipe = brightnesses < threshold
    pixel_coords = np.nonzero(pixels_to_wipe)
    num_of_pixels_to_wipe = np.shape(pixel_coords)[1]

    r0 = np.repeat(pixel_coords[0], 3)
    r1 = np.repeat(pixel_coords[1], 3)
    r2 = np.tile(np.array([0,1,2], dtype=np.int64), num_of_pixels_to_wipe)
    coords = (r0, r1, r2)

    rgb[coords] = 255
    return(rgb)


rgb = np.array([[[0.1,0.5,0.1],[0.3,0.2,0.9]],
                  [[0.8,0.8,0.1],[0.8,0.8,0.1]],
                  [[0.4,0.3,0.1],[0.8,0.8,0.9]]])

#foo = remove_dark_pixels(rgb)
#exit()


#fig, axs = plt.subplots(ncols=2)

"""
img = np.array([[[0.1,0.5,0.1],[0.3,0.2,0.9]],
                  [[0.8,0.8,0.1],[0.8,0.8,0.1]],
                  [[0.4,0.3,0.1],[0.8,0.8,0.9]]])

rgb = np.array([[[250,150,100],[250,100,150]],
                [[100,150,200],[100,200,150]]])

hsv_true = np.array([[[20,60,98],[340,60,98]],
                     [[210,50,78],[150,50,78]]])

hsv_test = rgb_img_to_hsv_img(rgb)
print(hsv_test)

rgb_test = hsv_img_to_rgb_img(hsv_test)

print(rgb_test)
exit()
"""
plt.subplot(1,4,1)
plt.title(f"{champion}, skin #{skinID}")
plt.imshow(img)

plt.subplot(1,4,2)
# First map the de-saturated or dark pixels to a grey pixel
blank_hsv = [0,0,0.95]
sat_threshold = 0.15
bri_threshold = 0.5
img_hsv = rgb_img_to_hsv_img(img)
img_hsv_filtered = filter_pixels_by_channel(img=img_hsv,
                                            channel_index=1,
                                            channel_filter=lambda sat: sat > sat_threshold,
                                            blank=blank_hsv)

img_hsv_filtered = filter_pixels_by_channel(img=img_hsv_filtered,
                                            channel_index=2,
                                            channel_filter=lambda val: val > bri_threshold,
                                            blank=blank_hsv)


img_rgb_filtered = hsv_img_to_rgb_img(img_hsv_filtered)

# Now actually remove the desaturated or dark pixels
dim, pixels_hsv = flatten_image(img_hsv_filtered)
pixels_hsv_tidy = np.array([px for px in np.transpose(pixels_hsv) if not np.array_equal(px, blank_hsv)])
dim, pixels_hsv = (np.shape(pixels_hsv_tidy), np.transpose(pixels_hsv_tidy))
pixels_rgb = hsv_to_rgb(pixels_hsv)

plt.imshow(img_rgb_filtered)
plt.title("{:.2%} pixels retained\nsat > {}, bri > {}".format(
    np.shape(pixels_hsv)[1]/(np.shape(img_hsv)[0] * np.shape(img_hsv)[1]),
    sat_threshold,
    bri_threshold))


plt.subplot(1,4,3, polar=True, theta_offset=np.pi/2, theta_direction=-1)
pixels_hsv[2] = 1
pixels_rgb = hsv_to_rgb(np.copy(pixels_hsv))
colors_hex = [rgb_to_hex(pixel) for pixel in np.transpose(pixels_rgb)]
plt.scatter(pixels_hsv[0]*2*np.pi/360, np.log(1+pixels_hsv[1]), color = colors_hex, s=5, alpha=0.1)
plt.title("HSV space\n(human-readable)")

plt.subplot(1,4,4)
pixels_xyz = rgb_to_xyb(pixels_rgb)
plt.scatter(pixels_xyz[0], pixels_xyz[1], color = colors_hex, s=5, alpha=0.02)
plt.xlim([0,0.8])
plt.ylim([0,0.9])
plt.plot([0.6915,0.17,0.1532,0.6915],[0.3038,0.7,0.0475,0.3038], color="black", linewidth=2)
plt.gca().set_aspect('equal')
plt.show()
# HSV pixels should be plotted as:
    # r = S
    # theta = H
    # V = 0.8
    # color = hsv_to_rgb(hsv[2=0.8]) / 255

# XYZ pixels should be plotted as:
    # x = x
    # y = y
    #

plt.show()


"""
tick = time.time()
### old code to convert RGB to XY
rgb_vals = np.reshape(img, (-1,3))
xy_vals = [rgb_to_xyb(rgb)[0:2] for rgb in rgb_vals]
tock = time.time()
print(f"First conversion to XY: f{tock - tick}")
"""
### new code to convert RGB to XY
tick = time.time()
xy_vals_new = rgb_img_to_xyb_img(img)
tock = time.time()
print(f"Second conversion to XY: f{tock - tick}")
