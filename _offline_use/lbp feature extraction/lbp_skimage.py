import os
import cv2
import numpy as np
from time import time
from matplotlib import pyplot as plt
from skimage.feature import local_binary_pattern as lbp


folder_awal = 'KELAS_DATA/'
folder_tujuan = 'KELAS_DATA_lbp/'
ls = os.listdir(folder_awal)

if folder_tujuan not in ls:
    os.mkdir(folder_tujuan)

R = 3           #radius
P = 8 * R       #himpunan titik ketetanggaan

total = 0
for i in range(len(ls)):
    now = time()
    filename = ls[i]
    filepath = folder_awal + filename

    img      = cv2.imread(filepath, 1)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_lbp  = lbp(img_gray, P, R, method='default')

    plt.imsave(folder_tujuan + 'lbp_' + filename, img_lbp, cmap='gray')

    print("{}/{} done in {:.2f}s. ({}%)".format(i + 1, len(ls),\
        time() - now, 100 * float(i + 1) / (len(ls))))
    total += (time() - now)

print('Total {:.2f}s.'.format(total))