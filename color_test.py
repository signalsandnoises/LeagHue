# A development script to experiment on pulling Hue colors from splash art.

import requests
import random
import numpy as np
from PIL import Image
from io import BytesIO
from matplotlib import pyplot as plt
from phue import Bridge
from math import pow
import time

# League constants
patch = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
data_dragon_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/"
# Hue constants
ip = "10.0.0.50"
active_IDs = [3,4,5]
username = "t9EuSmHFC2o7bTtt5Lyq5eUMKNU0otLLN4nHE9wO"
lights = Bridge(ip=ip, username=username).get_light_objects('id')


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


# Given a color encoded in xyb, set a collection of lightIDs to that color
def set_xyb(IDs, xyb):
    for ID in IDs:
        lights[ID].xy = xyb[0:2]
        lights[ID].brightness = int(xyb[2])


# Input 0-255 RGB. Output hexcode
def rgb_to_hex(rgb):
    return '#' + ''.join([hex(val)[2:] for val in rgb])

## Given a (X,Y,3) image, compute a (3,X*Y) ndarray of x-values, y-values, and b-values
## Good for use with matplotlib or position-agnostic sampling
def rgb_to_xyb_rows(rgb):
    ## Implemented using https://developers.meethue.com/develop/application-design-guidance/color-conversion-formulas-rgb-to-xy-and-back/#Color-rgb-to-xy
    # 1. convert RGB values to 0-1
    rgb = rgb / 255

    # 2. gamma-correction
    gamma_correction = np.vectorize(lambda c: pow((c+0.055)/1.055, 2.4) if c > 0.04045 else c / 12.92)
    img = gamma_correction(rgb)

    # 3 and 4. RGB to XYZ to xyb
    num_of_pixels = np.prod(np.shape(img)[:2])
    rgb = np.transpose(img.reshape((num_of_pixels,3), order='F'))
    rgb2xyz = np.array([[0.4124, 0.3576, 0.1805],
                        [0.2126, 0.7152, 0.0722],
                        [0.0193, 0.1192, 0.9505]])
    foobar = np.array([[1,0,0],
                       [0,1,0],
                       [1,1,1]])
    rgb2xySum = np.matmul(foobar, rgb2xyz)
    xySum = np.matmul(rgb2xySum, rgb)  # (3,P) matrix with rows: x, y, x+y+z

    xyb = np.array([xySum[0]/(xySum[2]+0.0000001),
                    xySum[1]/(xySum[2]+0.0000001),
                    xySum[1]])
    # TODO do we need steps 5,6 or does the bridge take care of it?
    return(xyb)

# Given a (X,Y,3) RGB image, return a (X,Y,3) image in XYB format
def rgb_to_xyb_img(rgb):
    dim = np.shape(rgb)
    xyb = rgb_to_xyb_rows(rgb)
    return np.reshape(np.transpose(xyb), dim)



def examine_color(R, G, B, bri=100) -> None:
    """
    Applies these colors to my hue lights at home.
    For testing only.
    Input: ints R, G, B in [0,255],
           int brightness in [0,100]
    """
    xyb = rgb_to_xyb(0.5*np.array([R, G, B]))
    print(xyb)
    set_xyb(active_IDs, [xyb[0], xyb[1], bri])
    time.sleep(2)

    xyb = rgb_to_xyb_new(np.array([[[R,G,B]]]))
    print(xyb)
    set_xyb(active_IDs, [xyb[0][0], xyb[1][0], bri])


#img = np.array([[[6*x+3*y, 8*x+4*y, 10*x+5*y] for x in range(3)] for y in range(3)])
url = splash_url("Seraphine", 1)
print(url)
img = load_image(url)
if img is None:
    raise ImportError("Unable to fetch splash art for this skin!")

xyb = rgb_to_xyb_img(img)

def remove_dark_pixels(rgb, threshold=0.8):
    #xyb = rgb_to_xyb_img(rgb)
    xyb = rgb

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

plt.subplot(1,2,1)
plt.imshow(img)
plt.subplot(1,2,2)
img_filtered = remove_dark_pixels(img, threshold=100)
plt.imshow(img_filtered)
plt.show()


"""
tick = time.time()
### old code to convert RGB to XY
rgb_vals = np.reshape(img, (-1,3))
xy_vals = [rgb_to_xyb(rgb)[0:2] for rgb in rgb_vals]
tock = time.time()
print(f"First conversion to XY: f{tock - tick}")

### new code to convert RGB to XY
tick = time.time()
xy_vals_new = rgb_to_xyb_new(img)
tock = time.time()
print(f"Second conversion to XY: f{tock - tick}")
"""