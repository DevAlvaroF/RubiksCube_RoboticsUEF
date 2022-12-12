import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2
from natsort import natsorted
import os
from os import listdir
from os.path import isfile, join
import matplotlib.patches as patches


abs_file_path = os.path.join(os.getcwd(),"Photos/")
onlyfiles = [f for f in listdir(abs_file_path) if isfile(join(abs_file_path, f))]
onlyfiles = natsorted(onlyfiles)

# img_test = cv2.imread(join(abs_file_path, onlyfiles[0]))	
# gray = cv2.cvtColor(img_test, cv2.COLOR_BGR2GRAY)[150:150+273,500:500+273]
# blur = cv2.GaussianBlur(gray,(5,5),0)
# print(type(blur[0,0]))
# edges = cv2.Canny(image=blur, threshold1=35, threshold2=50) # Canny Edge Detection

# Extract the 9 3x3 RGB values

def euclidean_distance(array1,array2):
    return np.sqrt(np.sum(np.power((array1-array2),2)))

def get_letter(id):
    if id == 0:
        return 'U'
    elif id == 1:
        return 'R'
    elif id == 2:
        return 'F'
    elif id == 3:
        return 'D'
    elif id == 4:
        return 'L'
    elif id == 5:
        return 'B'

def start(method = 'rgb' ): # can be 'gray'

    offset = 105
    i_x = 20
    i_y = 20
    spatial_size = 20
    all_matrices = []
    all_matrices_gray = []
    central_color = []
    central_color_gray = []
    for f in onlyfiles:
        empty_rgb = np.empty((3,3,3),dtype=float)
        empty_gray = np.empty((3,3),dtype=float)

        img_rgb2 = cv2.imread(join(abs_file_path, f))	
        gray = cv2.cvtColor(img_rgb2, cv2.COLOR_BGR2GRAY)[150:150+273,500:500+273]
        img_rgb = np.array(Image.open(join(abs_file_path, f)))[150:150+273,500:500+273,:]
        for i in range(3):
            for j in range(3):
                row_val = i_y + i*offset
                col_val = i_x + j *offset
                empty_rgb[i,j,:] = np.mean(img_rgb[row_val:row_val+spatial_size, col_val:col_val+spatial_size,:], axis=(0,1))
                empty_gray[i,j] = np.mean(gray[row_val:row_val+spatial_size, col_val:col_val+spatial_size], axis=(0,1))
                

                if (i==1) and (j==1):
                    central_color.append(np.mean(img_rgb[row_val:row_val+spatial_size, col_val:col_val+spatial_size,:], axis=(0,1)))
                    central_color_gray.append(np.mean(gray[row_val:row_val+spatial_size, col_val:col_val+spatial_size], axis=(0,1)))

        all_matrices.append(empty_rgb)
        all_matrices_gray.append(empty_gray)


    estimated_faces = ''
    
    if method == 'rgb':
        for idx,tmp_face in enumerate(all_matrices):
            min_idx = 0
            min_value = np.inf
            for ii in range(3):
                for jj in range(3):
                    if ii != jj:
                        for T, m in enumerate(central_color):
                            res = euclidean_distance(tmp_face[ii,jj,:].flatten(), m.flatten())
                            #res = euclidean_distance(tmp_face[ii,jj], m)
                            if res < min_value:
                                min_value = res.copy()
                                min_idx = T
                        # Append letter of the Face with lowest distance
                        print(min_idx)
                        estimated_faces += get_letter(min_idx)
                    else:
                        estimated_faces += get_letter(idx)

    elif method == 'gray':
        for idx,tmp_face in enumerate(all_matrices_gray):
            min_idx = 0
            min_value = np.inf
            for ii in range(3):
                for jj in range(3):
                    if ii != jj:
                        for T, m in enumerate(central_color_gray):
                            #res = euclidean_distance(tmp_face[ii,jj,:].flatten(), m.flatten())
                            res = euclidean_distance(tmp_face[ii,jj], m)
                            if res < min_value:
                                min_value = res.copy()
                                min_idx = T
                        # Append letter of the Face with lowest distance
                        estimated_faces += get_letter(min_idx)
                    else:
                        estimated_faces += get_letter(idx)
    
    return estimated_faces

    # fig, axs = plt.subplots(nrows=1, ncols=1, dpi=100)
    # fig.suptitle("Tunable Images")


    # axs.imshow(img_rgb, cmap='gray')
    # # Row 1
    # rect1 = patches.Rectangle((i_x, i_y), 20, 20, linewidth=1, edgecolor='r', facecolor=(0,0,0,0)) # Red Patch
    # axs.add_patch(rect1)
    # rect2 = patches.Rectangle((i_x+1*offset, i_y), 20, 20, linewidth=1, edgecolor='r', facecolor=(0,0,0,0)) # Red Patch
    # axs.add_patch(rect2)
    # rect3 = patches.Rectangle((i_x+2*offset, i_y), 20, 20, linewidth=1, edgecolor='r', facecolor=(0,0,0,0)) # Red Patch
    # axs.add_patch(rect3)

    # # Row 2
    # rect4 = patches.Rectangle((i_x, i_y+1*offset), 20, 20, linewidth=1, edgecolor='r', facecolor=(0,0,0,0)) # Red Patch
    # axs.add_patch(rect4)
    # rect5 = patches.Rectangle((i_x+1*offset, i_y+1*offset), 20, 20, linewidth=1, edgecolor='r', facecolor=(0,0,0,0)) # Red Patch
    # axs.add_patch(rect5)
    # rect6 = patches.Rectangle((i_x+2*offset, i_y+1*offset), 20, 20, linewidth=1, edgecolor='r', facecolor=(0,0,0,0)) # Red Patch
    # axs.add_patch(rect6)

    # # Row 3
    # rect7 = patches.Rectangle((i_x, i_y+2*offset), 20, 20, linewidth=1, edgecolor='r', facecolor=(0,0,0,0)) # Red Patch
    # axs.add_patch(rect7)
    # rect8 = patches.Rectangle((i_x+1*offset, i_y+2*offset), 20, 20, linewidth=1, edgecolor='r', facecolor=(0,0,0,0)) # Red Patch
    # axs.add_patch(rect8)
    # rect9 = patches.Rectangle((i_x+2*offset, i_y+2*offset), 20, 20, linewidth=1, edgecolor='r', facecolor=(0,0,0,0)) # Red Patch
    # axs.add_patch(rect9)


    # plt.show()


