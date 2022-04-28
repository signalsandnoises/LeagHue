from colorlib import *
import numpy as np

"""
rgb_true_img = np.array([[[250, 150, 100], [250, 100, 150]],
                     [[100,150,200],[100,200,150]]])

hsv_true_img = np.array([[[20,60,98],[340,60,98]],
                     [[210,50,78],[150,50,78]]])

dim, rgb_true = flatten_image(np.copy(rgb_true_img))
dim, hsv_true = flatten_image(np.copy(hsv_true_img))

hsv_calc = rgb_to_hsv(np.copy(rgb_true))

rgb_calc = hsv_to_rgb(np.copy(hsv_calc))

print(rgb_true)
print(rgb_calc)

print(hsv_true)
print(hsv_calc)
"""

xyb_pixel = np.array([[0.242],[0.213],[0.4]])
rgb_pixel = xyb_to_rgb(xyb_pixel)

#rgb_pixel = np.array([[255],[0],[255]])
#xyb_pixel = rgb_to_xyb(rgb_pixel)

print(f"xyb: {xyb_pixel}")
print(f"rgb: {rgb_pixel}")