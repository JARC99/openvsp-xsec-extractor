import numpy as np
import matplotlib.pylab as plt
import seaborn as sns
import ezdxf
import os

DPI = 300
COLORS = ["darkblue", "darkred", "darkgreen", "darkorange",
          "darkcyan", "darkmagenta", "dimgray", "goldenrod"]
sns.set_theme(style="whitegrid", font="Palatino Linotype",
              context="paper", palette=COLORS)

DATA_DIR = "meshes/"
EXPORT_DIR = "dxf_files/"
for dxf_file in os.listdir(EXPORT_DIR):
    os.remove(EXPORT_DIR + dxf_file)

# %% Specify .tir file name and main axis

XSECS_FILE = DATA_DIR + "cessna172_ydir.tri"
NORMAL_AXIS = 'y'

# %% XSec extractor

n_points = int(np.loadtxt(XSECS_FILE, max_rows=1)[0])
xsecs_data = np.loadtxt(XSECS_FILE, skiprows=1, max_rows=n_points)

if NORMAL_AXIS == 'x':
    locs = np.unique(xsecs_data[:, 0])

    xsec_list = []
    for i in range(len(locs)):
        xsec = xsecs_data[xsecs_data[:, 0] == locs[i]][:, 1:]
        xsec_list.append(xsec)

else:
    locs = np.unique(xsecs_data[:, 1])

    xsec_list = []
    for i in range(len(locs)):
        xsec = np.stack((xsecs_data[xsecs_data[:, 1] == locs[i]]
                        [:, 0], xsecs_data[xsecs_data[:, 1] == locs[i]][:, -1]), 1)
        xsec_list.append(xsec)

for i, xsec in enumerate(xsec_list):
    
    if np.size(xsec, 0) < 10:
        continue
    
    h_center_val = (np.max(xsec[:, 0]) -
                    np.min(xsec[:, 0]))/2 + np.min(xsec[:, 0])
    v_center_val = (np.max(xsec[:, 1]) -
                    np.min(xsec[:, 1]))/2 + np.min(xsec[:, 1])

    cent_xsec_array = np.stack(
        (xsec[:, 0] - h_center_val, xsec[:, 1] - v_center_val), 1)

    angle_array = np.reshape(np.arctan2(
        cent_xsec_array[:, 1], cent_xsec_array[:, 0]), (int(np.size(xsec, 0)), 1))

    dist_array = np.reshape(np.sqrt(
        cent_xsec_array[:, 0]**2 + cent_xsec_array[:, 1]**2), (int(np.size(xsec, 0)), 1))

    polar_array = np.hstack((cent_xsec_array, angle_array, dist_array))
    sorted_xsec_array = polar_array[np.lexsort(
        (polar_array[:, 3], polar_array[:, 2]))]

    fig = plt.figure(dpi=DPI)
    ax = fig.add_subplot(111)
    if NORMAL_AXIS == 'x':
        ax.set_title("XSec_{0}, x = {1} m".format(
            i, round(locs[i] - locs[0], 3)))
        ax.axis('equal')
        ax.set_xlabel("y, m")
        ax.set_ylabel("z, m")
    else:
        ax.set_title("XSec {0}, y = {1} m".format(
            i, round(locs[i] - locs[0], 3)))
        ax.axis('equal')
        ax.set_xlabel("x, m")
        ax.set_ylabel("z, m")
    ax.plot(sorted_xsec_array[:, 0], sorted_xsec_array[:, 1])

# %% Export .dxf file

    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    for k in range(int(np.size(sorted_xsec_array, 0))-1):
        msp.add_line(sorted_xsec_array[k], sorted_xsec_array[k+1])
    msp.add_line(sorted_xsec_array[-1], sorted_xsec_array[0])
    doc.saveas(EXPORT_DIR + "XSec_{0}.dxf".format(i))
