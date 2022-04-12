"""
Conversion structure:
XYB <--> RGB <--> HSV'
Thus, a conversion from XYB to HSV necessitates an intermediary conversion to RGB


RANGES IN THIS FILE
R G B range: 0-255 0-255 0-255
H S V range: 0-360 0-1 0-1
X Y B range: 0-1 0-1 0-1

RANGES IN PHILIPS HUE
R G B range: 0-255 0-255 0-255
H S V range: 0-65535 0-254 0-254
X Y B range: 0-1 0-1 0-254
"""

import numpy as np



# TODO remove this?
# Input 0-255 RGB. Output hexcode
def rgb_to_hex(rgb):
    return '#' + ''.join([hex(val)[2:] for val in rgb])

def flatten_image(img) -> (tuple, np.array):
    """
    Reformat a (X,Y,3) image to a (3,X*Y) array of pixels for linear processing
    Color-space agnostic.
    """
    dim = np.shape(img)
    num_of_pixels = dim[0]*dim[1]
    pixels = np.transpose(np.reshape(img, (num_of_pixels, -1)))
    #pixels = np.transpose(img.reshape(3,num_of_pixels, order='F'))
    return dim, pixels

def unflatten_image(dim, pixels):
    """
    Reformat a (3,X*Y) array of pixels to a (X,Y,3) image for viewing.
    Color-space agnostic.
    """
    return np.reshape(np.transpose(pixels), dim)


def rgb_to_xyb(rgb):
    """Convert a (3,X*Y) array of RGB pixels to XYB pixels"""
    # Implemented using https://developers.meethue.com/develop/application-design-guidance/color-conversion-formulas-rgb-to-xy-and-back/#Color-rgb-to-xy
    # 1. convert RGB values to 0-1
    rgb = rgb / 255

    # 2. gamma-correction
    gamma_correction = np.vectorize(lambda c: pow((c+0.055)/1.055, 2.4) if c > 0.04045 else c / 12.92)
    rgb = gamma_correction(rgb)

    # 3 and 4. RGB to XYZ to xyb
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


def xyb_to_rgb(xyb):
    """Convert a (3,X*Y) array of XYB pixels to RGB pixels"""
    # Implemented using https://developers.meethue.com/develop/application-design-guidance/color-conversion-formulas-rgb-to-xy-and-back/#Color-rgb-to-xy
    # TODO are we gonna skip steps 1 and 2?
    x = xyb[0]
    y = xyb[1]
    z = 1 - x - y
    Y = xyb[2]
    X = Y / y * x
    Z = Y / y * z

    conversion_matrix = np.array([[1.656492, 0.354851, 0.255038],
                                  [-0.707196, 1.655397, 0.036152],
                                  [0.051713, 0.121364, 1.011530]])
    rgb = np.matmul(conversion_matrix, xyb)

    reverse_gamma_correction = np.vectorize(lambda c: 12.92 * c if c <= 0.0031308 else 1.055 * (c**(1/2.4)) - 0.055)
    rgb = reverse_gamma_correction(rgb)
    return rgb


def rgb_to_hsv(rgb):
    """Convert a (3,X*Y) array of RGB pixels to HSV pixels
    HSV range: [0,360]:[0,1]:[0,1]"""
    # Implemented from https://www.rapidtables.com/convert/color/rgb-to-hsv.html
    rgb = rgb/255

    c_max_ind = np.argmax(rgb, axis=0)
    c_min_ind = np.argmin(rgb, axis=0)
    c_med_ind = 3 - c_max_ind - c_min_ind
    num_of_pixels = np.shape(rgb)[1]
    col_indices = np.arange(num_of_pixels)

    c_max = rgb[(c_max_ind, col_indices)]
    c_min = rgb[(c_min_ind, col_indices)]
    delta = c_max - c_min

    c_one_after_max_ind = (c_max_ind + 1) % 3
    c_two_after_max_ind = (c_max_ind + 2) % 3
    phi = rgb[(c_one_after_max_ind, col_indices)] - rgb[(c_two_after_max_ind, col_indices)]

    H = np.empty(num_of_pixels)
    for i in range(num_of_pixels):
        kernel = 0
        if delta[i] == 0:
            kernel = 0
        elif c_max_ind[i] == 0:
            kernel = (phi[i] / delta[i]) % 6
        elif c_max_ind[i] == 1:
            kernel = phi[i] / delta[i] + 2
        elif c_max_ind[i] == 2:
            kernel = phi[i] / delta[i] + 4
        H[i] = 60*kernel

    safe_reciprocal = np.vectorize(lambda x: 1/x if x != 0 else 0)
    S = delta * safe_reciprocal(c_max)
    V = c_max

    return np.row_stack((H,S,V))


def hsv_to_rgb(hsv):
    """
    Convert a (3,X*Y) array of XYB pixels to RGB pixels
    """
    # Implemented from https://developers.meethue.com/develop/application-design-guidance/color-conversion-formulas-rgb-to-xy-and-back/#hsv-to-rgb-color
    num_of_pixels = np.shape(hsv)[1]
    s = hsv[1]
    v = hsv[2]
    C = s*v
    X = C*(1-abs(((hsv[0]/60) % 2) - 1))
    m = v - C
    r = np.empty(num_of_pixels)
    g = np.empty(num_of_pixels)
    b = np.empty(num_of_pixels)
    for i in range(num_of_pixels):
        hue = hsv[0][i]
        if (hue < 60):
            r[i], g[i], b[i] = (C[i],X[i],0)
        elif (hue < 120):
            r[i], g[i], b[i] = (X[i],C[i],0)
        elif (hue < 180):
            r[i], g[i], b[i] = (0,C[i],X[i])
        elif (hue < 240):
            r[i], g[i], b[i] = (0,X[i],C[i])
        elif (hue < 300):
            r[i], g[i], b[i] = (X[i],0,C[i])
        else:
            r[i], g[i], b[i] = (C[i],0,X[i])
    R = r + m
    G = g + m
    B = b + m
    return (255*np.row_stack((R,G,B))).astype(int)


def rgb_img_to_xyb_img(rgb):
    """
    Convert a (X,Y,3) array of RGB pixels to XYB pixels
    """
    dim, pixels = flatten_image(rgb)
    pixels = rgb_to_xyb(pixels)
    xyb = unflatten_image(dim, pixels)
    return xyb

def xyb_img_to_rgb_img(xyb):
    """
    Convert a (X,Y,3) array of XYB pixels to RGB pixels
    """
    dim, pixels = flatten_image(xyb)
    pixels = xyb_to_rgb(pixels)
    rgb = unflatten_image(dim, pixels)
    return rgb

def rgb_img_to_hsv_img(rgb):
    """
    Convert a (X,Y,3) array of RGB pixels to HSV pixels
    """
    dim, pixels = flatten_image(rgb)
    pixels = rgb_to_hsv(pixels)
    hsv = unflatten_image(dim, pixels)
    return hsv

def hsv_img_to_rgb_img(hsv):
    """
    Convert a (X,Y,3) array of HSV pixels to RGB pixels
    """
    dim, pixels = flatten_image(hsv)
    pixels = hsv_to_rgb(pixels)
    rgb = unflatten_image(dim, pixels)
    return rgb

def xyb_img_to_hsv_img(xyb):
    """
    Convert a (X,Y,3) array of XYB pixels to HSV pixels
    """
    dim, pixels = flatten_image(xyb)
    pixels = xyb_to_rgb(pixels)
    pixels = rgb_to_hsv(pixels)
    hsv = unflatten_image(dim, pixels)
    return hsv

def hsv_img_to_xyb_img(hsv):
    """
    Convert a (X,Y,3) array of HSV pixels to XYB pixels
    """
    dim, pixels = flatten_image(hsv)
    pixels = hsv_to_rgb(pixels)
    pixels = rgb_to_xyb(pixels)
    xyb = unflatten_image(dim, pixels)
    return xyb

def filter_channel(img, channel_index, channel_filter, blank=0):
    """
    channel: the index of a vector to filter on
    filter: a function that inputs a channel vector and returns a boolean vector
            e.g. lambda x: x < 0.8
    range: the resulting pixel to insert. Must have shape=(3,1) (column vector in R^3).
    """
    img = np.ndarray.copy(img)  # don't want to modify the old img in-place and lose it.
    dim, pixels = flatten_image(img)
    marked_pixel_map = channel_filter(pixels[channel_index])
    marked_pixel_cols = np.nonzero(marked_pixel_map)
    num_of_marked_pixels = np.shape(marked_pixel_cols)[1]
    #r0 = np.tile(np.array([0,1,2], dtype=np.int64), num_of_marked_pixels)
    #r1 = np.repeat(marked_pixel_cols, 3)
    r0 = np.repeat(channel_index, num_of_marked_pixels)
    r1 = marked_pixel_cols
    marked_pixel_coords = (r0, r1)
    pixels[marked_pixel_coords] = blank
    filtered_img = unflatten_image(dim, pixels)
    return filtered_img

def filter_pixels_by_channel(img, channel_index, channel_filter, blank=[0,0,0]):
    """
    Filters all three channels of a pixel based off the channel_filter.
    Computationally equivalent to a single call.
    """
    img = np.ndarray.copy(img)  # don't want to modify the old img in-place and lose it.
    dim, pixels = flatten_image(img)
    marked_pixel_map = channel_filter(pixels[channel_index])
    marked_pixel_cols = np.nonzero(marked_pixel_map)
    num_of_marked_pixels = np.shape(marked_pixel_cols)[1]
    r0 = np.tile(np.array([0,1,2], dtype=np.int64), num_of_marked_pixels)
    r1 = np.repeat(marked_pixel_cols, 3)
    marked_pixel_coords = (r0, r1)
    objective = np.tile(np.array(blank, dtype=np.int64), num_of_marked_pixels)
    pixels[marked_pixel_coords] = objective
    filtered_img = unflatten_image(dim, pixels)
    return filtered_img

#foo = np.array([[[6*x+3*y, 8*x+4*y, 10*x+5*y] for x in range(3)] for y in range(3)])
#bar = filter_pixels_by_channel(foo, 2, lambda x: x > 10, blank=[255,255,255])

"""
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
    """
