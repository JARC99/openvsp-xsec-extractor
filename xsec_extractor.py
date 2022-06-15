import numpy as np
import matplotlib.pylab as plt
import matplotlib.patches as mpatches
import seaborn as sns
import ezdxf
import os

DPI = 300
COLORS = ["black", "darkblue", "darkred", "darkgreen", "darkorange",
          "darkcyan", "darkmagenta", "dimgray", "goldenrod"]
sns.set_theme(style="whitegrid", font="Palatino Linotype",
              context="paper", palette=COLORS)

DATA_DIR = "meshes/"
DXF_EXPORT_DIR = "dxf_files/"
PNG_EXPORT_DIR = "png_files/"
for dxf_file in os.listdir(DXF_EXPORT_DIR):
    os.remove(DXF_EXPORT_DIR + dxf_file)
for png_file in os.listdir(PNG_EXPORT_DIR):
    os.remove(PNG_EXPORT_DIR + png_file)

# %% Specify .tir file name and main axis

XSECS_FILE = DATA_DIR + "cessna172.tri"
NORMAL_AXIS = 'x'

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


#%% Plot the XSecs

    fig = plt.figure(dpi=DPI)
    ax = fig.add_subplot(111)
    ax.axis('equal')
    if NORMAL_AXIS == 'x':
        ax.set_title("XSec_{0}, x = {1} m".format(
            i, round(locs[i] - locs[0], 3)))
        ax.set_xlabel("y, m")
        ax.set_ylabel("z, m")
    else:
        ax.set_title("XSec {0}, y = {1} m".format(
            i, round(locs[i] - locs[0], 3)))
        ax.set_xlabel("x, m")
        ax.set_ylabel("z, m")

    plot_array = np.vstack((sorted_xsec_array, sorted_xsec_array[0, :]))
    ax.plot(plot_array[:, 0], plot_array[:, 1], alpha=1)


# %% Export XSecs as DXF

    doc = ezdxf.new('R12')
    msp = doc.modelspace()
    for k in range(int(np.size(sorted_xsec_array, 0))-1):
        msp.add_line(sorted_xsec_array[k], sorted_xsec_array[k+1])
    msp.add_line(sorted_xsec_array[-1], sorted_xsec_array[0])

    msp.add_line((0.2, 0.2), (0.2, -0.2))
    msp.add_line((0.2, -0.2), (-0.2, -0.2))
    msp.add_line((-0.2, -0.2), (-0.2, 0.2))
    msp.add_line((-0.2, 0.2), (0.2, 0.2))

    doc.saveas(DXF_EXPORT_DIR + "XSec_{0}.dxf".format(i))

# %% Export XSecs as PNG

    fig = plt.figure(dpi=DPI)
    ax = fig.add_subplot(111)
    ax.grid(False)
    ax.axis(False)
    ax.axis('equal')
    
    # poly = mpatches.Polygon(sorted_xsec_array[:, :2])
    # ax.add_patch(poly)
    
    plot_array = np.vstack((sorted_xsec_array, sorted_xsec_array[0, :]))
    ax.plot(plot_array[:, 0], plot_array[:, 1], alpha=1)
    
    height = np.max(sorted_xsec_array[:, 1]) - np.min(sorted_xsec_array[:, 1])
    width = np.max(sorted_xsec_array[:, 0]) - np.min(sorted_xsec_array[:, 0])
    
    ax.hlines(0, -width/2, width/2, linestyle="dashed", color="red")
    ax.vlines(0, -height/2, height/2, linestyle="dashed", color="red")
    
    ax.hlines(height/2, -width/2, width/2, linestyle="dotted", color="blue")
    ax.hlines(-height/2, -width/2, width/2, linestyle="dotted", color="blue")
    
    fig.savefig(PNG_EXPORT_DIR + "XSec_{0}.png".format(i),
        format="png", bbox_inches="tight")
