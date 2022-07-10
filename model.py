from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.gridspec import GridSpec
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
    subtick = time()



    # changes an individual pixel
    # inputs three channel vectors and returns a 3xN pixel grid
    effect = lambda h, s, v: np.array([h, s, np.repeat(1, len(v))])

    dim, pixels_rgb = flatten_image(img)

    pixels_hsv = rgb_to_hsv(pixels_rgb)

    sat_threshold = 0.1
    bri_threshold = 0.1

    information = (pixels_hsv[1] + pixels_hsv[2])/2
    information_cutoff = np.percentile(information, [75])[0]

    # determines whether we keep a pixel or not
    # inputs three channel vectors and returns a boolean vector
    filter = lambda h, s, v: (s > sat_threshold) & (v > bri_threshold) & ((s+v)/2 > information_cutoff)

    pixels_to_keep = filter(pixels_hsv[0], pixels_hsv[1], pixels_hsv[2])
    if debugging:
        print(f"\t(debugging={debugging})")
        pixels_to_remove = ~ pixels_to_keep
        # Blank out the pixels_to_remove
        blank_hsv = [0, 0, 0.95]
        for c, val in enumerate(blank_hsv):
            pixels_hsv[c, pixels_to_remove] = val

        # Process the pixels_to_keep
        pixels_hsv[:,pixels_to_keep] = effect(pixels_hsv[0,pixels_to_keep],
                                              pixels_hsv[1,pixels_to_keep],
                                              pixels_hsv[2,pixels_to_keep])
        # Create our image, then discard the blanked pixels
        img_rgb_filtered = unflatten_image(dim, hsv_to_rgb(pixels_hsv))
        pixels_hsv = pixels_hsv[:,pixels_to_keep]
        pixels_hsv_tidy = np.transpose(pixels_hsv)
        prop_pixels_retained = np.shape(pixels_hsv)[1] / (dim[0] * dim[1])

    else:
        pixels_hsv = pixels_hsv[:,pixels_to_keep] # discard pixels to remove
        pixels_hsv = effect(pixels_hsv[0,:],  # process the pixels that we kept
                            pixels_hsv[1,:],
                            pixels_hsv[2,:])
        pixels_hsv_tidy = np.transpose(pixels_hsv)  # transpose for clustering
    subtock = time()
    print(f"\t3a. Filter the image: {subtock - subtick:.2f}s")


    ##
    ## SECTION TWO: SELECTING A COLOR PALETTE
    ##
    # TODO I should balance the hues going in, shouldn't I...
    """
    v_x = sum(np.cos(pixels_hsv[0] * 2 * np.pi / 360))
    v_y = sum(np.sin(pixels_hsv[0] * 2 * np.pi / 360))
    mean_hue = np.arctan2(v_y, v_x)
    opposite_hue = ((mean_hue + np.pi) % (2 * np.pi)) * (360 / (2 * np.pi))
    """

    n_clusters = 6
    subtick = time()
    kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=4004, batch_size=2048).fit(X=pixels_hsv_tidy,
                                                                                            sample_weight=np.exp(pixels_hsv[1]))
    subtock = time()
    print(f"\t3b. Cluster the pixels: {subtock - subtick:.2f}s")
    color_centers_hsv = np.transpose(kmeans.cluster_centers_)

    subtick = time()
    # We're not done here.
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
        fig = plt.figure(constrained_layout=True)
        gs = GridSpec(2, 4, figure=fig)
        aspect_ratio = np.shape(img)[1]/np.shape(img)[0]
        if aspect_ratio > 0.8:  # then it's wide enough to stack img on top of img_filtered
            ax_img = fig.add_subplot(gs[0,0:2])
            ax_filtered_img = fig.add_subplot(gs[1,0:2])
        else:
            ax_img = fig.add_subplot(gs[:,0])
            ax_filtered_img = fig.add_subplot(gs[:,1])
        ax_color_wheel = fig.add_subplot(gs[:, 2],
                                         polar=True, theta_offset=np.pi / 2, theta_direction=-1)
        ax_palette = fig.add_subplot(gs[:, 3])

        # Plot the image
        ax_img.imshow(img)
        ax_img.set_title(scene_name)

        # Plot the filtered image
        ax_filtered_img.set_title("{:.2%} pixels retained\nsat > {:.2f}, bri > {:.2f}".format(prop_pixels_retained,
                                                                                      sat_threshold,
                                                                                      bri_threshold))
        ax_filtered_img.imshow(img_rgb_filtered)

        # Plot filtered pixels on polar HSV scale
        pixels_hsv_flat = np.copy(pixels_hsv)
        pixels_hsv_flat[2] = 1
        pixels_rgb_flat = hsv_to_rgb(np.copy(pixels_hsv_flat))
        pixel_colors_hex = [rgb_to_hex(pixel) for pixel in np.transpose(pixels_rgb_flat)]
        ax_color_wheel.scatter(pixels_hsv[0] * 2 * np.pi / 360, pixels_hsv[1],
                               color=pixel_colors_hex, s=5, alpha=0.5)
        ax_color_wheel.scatter(color_centers_hsv_flat[0] * 2 * np.pi / 360, color_centers_hsv_flat[1],
                               color=color_centers_hex_flat, marker="o", edgecolors="black", s=50)
        ax_color_wheel.set_title("HS space")


        for i in range(n_clusters):
            ax_palette.add_patch(Rectangle((0, i / n_clusters), 0.5, 1 / n_clusters,
                                           color=color_centers_hex_flat[i]))
            ax_palette.text(0.75, (i + 0.5) / n_clusters, color_centers_hex_flat[i],
                            horizontalalignment='center', verticalalignment='top')
            ax_palette.text(0.75, (i + 0.5) / n_clusters, str(color_centers_rgb_flat[:, i]),
                            horizontalalignment='center', verticalalignment='bottom')

        #plt.subplots_adjust(left=0.05, right=0.95, top=1, bottom=0)

    ##
    ## SECTION FOUR: CREATING AND APPLYING THE SCENE
    ##
    subtock = time()
    scene_id = queryman.post_scene(sceneName=scene_name,
                                   x=color_centers_xyb_flat[0],
                                   y=color_centers_xyb_flat[1])
    print(f"\t3c. Clustering output formatting: {subtock - subtick:.2f}s")
    return scene_id