from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from colorlib import *
from sklearn.cluster import KMeans, MiniBatchKMeans
from QueryManager import QueryManager
from time import time


def img_to_scene(img, scene_name: str, queryman: QueryManager, debugging=False) -> str:
    """
    Input an RGB image and it will create a scene on the Hue corresponding to that image.
    Returns a scene_id.
    If debugging, you can call plt.show() after executing this method and it will plot the scene analysis.
    """
    ##
    ## SECTION ONE: PRE-PROCESSING THE IMAGE
    ##
    blank_hsv = [0, 0, 0.95]
    sat_threshold = 0.2
    bri_threshold = 0.5
    subtick = time()
    print(f"\t(debugging={debugging})")
    if debugging:
        img_hsv = rgb_img_to_hsv_img(img)  # convert
        # First mask the HSV pixels with low S or low V
        img_hsv_masked = mask_pixels_by_channel(img=img_hsv,
                                                channel_index=1,
                                                channel_filter=lambda sat: sat > sat_threshold,
                                                blank=blank_hsv)
        img_hsv_masked = mask_pixels_by_channel(img=img_hsv_masked,
                                                channel_index=2,
                                                channel_filter=lambda val: val > bri_threshold,
                                                blank=blank_hsv)
        # Apply the same mask in RGB space
        img_rgb_masked = hsv_img_to_rgb_img(img_hsv_masked)

        # Now actually filter out the masked pixels. Reduces data size.
        # TODO symptoms of bad design here.
        # TODO I should have designed my functions to flatten vertically, not horizontally, to avoid this mess.
        dim, pixels_hsv_unfiltered = flatten_image(img_hsv_masked)
        pixels_hsv_tidy = np.array([px for px in np.transpose(pixels_hsv_unfiltered) if not np.array_equal(px, blank_hsv)])
        pixels_hsv = np.transpose(pixels_hsv_tidy)
        prop_pixels_retained = np.shape(pixels_hsv)[1] / (np.shape(img_hsv)[0] * np.shape(img_hsv)[1])
    else:
        dim, pixels_rgb = flatten_image(img)  # flatten
        pixels_hsv = rgb_to_hsv(pixels_rgb)  # convert
        pixels_hsv_tidy = np.transpose(pixels_hsv)  # transpose
        pixels_hsv_tidy = pixels_hsv_tidy[np.nonzero((pixels_hsv[1] > sat_threshold)  # filter
                                                     * (pixels_hsv[2] > bri_threshold))]
        pixels_hsv = np.transpose(pixels_hsv_tidy)

    subtock = time()
    print(f"\t3a. Filter the image: {subtock - subtick:.2f}s")
    ##
    ## SECTION TWO: SELECTING A COLOR PALETTE
    ##

    subtick = time()
    n_clusters = 6
    kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=4004, batch_size=2048).fit(X=pixels_hsv_tidy,
                                                                  sample_weight=np.exp(pixels_hsv[1]))
    subtock = time()
    print(f"\t3b. Cluster the pixels: {subtock - subtick:.2f}s")

    color_centers_hsv = np.transpose(kmeans.cluster_centers_)
    # We're not done here.

    subtick = time()
    # First, color centers need to be ordered in a way that is not jarring.
    hue = color_centers_hsv[0]
    v_x = sum(np.cos(hue * 2 * np.pi / 360))
    v_y = sum(np.sin(hue * 2 * np.pi / 360))
    mean_hue = np.arctan2(v_y, v_x)
    opposite_hue = ((mean_hue + np.pi) % (2 * np.pi)) * (360 / (2 * np.pi))
    # sort the colors by going "clockwise" (increasing hue) from the opposite_hue
    # e.g. if hue = [1, 215, 260, 305, 340] and opposite_hue = 120,
    #      then we count 215, 260, 305, 340, 1+360.
    #      the "+360" is added to complete the spiral
    hue_index = np.argsort(hue + 360*(hue < opposite_hue))
    color_centers_hsv = color_centers_hsv[:, hue_index]

    # Next, color centers need to be represented in other forms
    color_centers_hsv_flat = np.copy(color_centers_hsv)
    color_centers_hsv_flat[2] = 1  # No "blackness" value in a hue lamp
    # Color centers also look better with a little extra saturation
    color_centers_hsv_flat[1] = 0.6*color_centers_hsv_flat[1]**2 + 0.4
    color_centers_rgb_flat = hsv_to_rgb(np.copy(color_centers_hsv_flat)).astype(int)
    color_centers_hex_flat = [rgb_to_hex(color) for color in np.transpose(color_centers_rgb_flat)]
    color_centers_xyb_flat = rgb_to_xyb(np.copy(color_centers_rgb_flat))

    ## SECTION THREE: PLOTTING EVERYTHING SO FAR
    if debugging:
        plt.subplot(1, 4, 1)
        plt.title(scene_name)
        plt.imshow(img)

        plt.subplot(1, 4, 2)
        plt.title("{:.2%} pixels retained\nsat > {}, bri > {}".format(prop_pixels_retained,
                                                                      sat_threshold,
                                                                      bri_threshold))
        plt.imshow(img_rgb_masked)

        plt.subplot(1, 4, 3, polar=True, theta_offset=np.pi / 2, theta_direction=-1)
        pixels_hsv_flat = np.copy(pixels_hsv)
        pixels_hsv_flat[2] = 1
        pixels_rgb_flat = hsv_to_rgb(np.copy(pixels_hsv_flat))
        pixel_colors_hex = [rgb_to_hex(pixel) for pixel in np.transpose(pixels_rgb_flat)]
        plt.scatter(pixels_hsv[0] * 2 * np.pi / 360, pixels_hsv[1],
                    color=pixel_colors_hex, s=5, alpha=0.02)
        # TODO why is color_centers_hsv so jank
        plt.scatter(color_centers_hsv_flat[0] * 2 * np.pi / 360, color_centers_hsv_flat[1],
                    color=color_centers_hex_flat, marker="o", edgecolors="black", s=50)
        plt.title("HS space")


        plt.subplot(1, 4, 4)
        ax = plt.gca()
        for i in range(n_clusters):
            ax.add_patch(Rectangle((0, i / n_clusters), 0.5, 1 / n_clusters,
                                   color=color_centers_hex_flat[i]))
            plt.text(0.75, (i + 0.5) / n_clusters, color_centers_hex_flat[i],
                     horizontalalignment='center', verticalalignment='top')
            plt.text(0.75, (i + 0.5) / n_clusters, str(color_centers_rgb_flat[:, i]),
                     horizontalalignment='center', verticalalignment='bottom')

        plt.subplots_adjust(left=0.05, right=0.95, top=1, bottom=0)

    ##
    ## SECTION FOUR: CREATING AND APPLYING THE SCENE
    ##
    subtock = time()
    scene_id = queryman.post_scene(sceneName=scene_name,
                                   x=color_centers_xyb_flat[0],
                                   y=color_centers_xyb_flat[1])
    print(f"\t3c. Clustering output formatting: {subtock - subtick:.2f}s")
    return scene_id