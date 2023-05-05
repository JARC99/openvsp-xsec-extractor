# %% Import required modules
import numpy as np
import matplotlib.pylab as plt
import seaborn as sns
import ezdxf
import os

DPI = 600
COLORS = ["black", "darkblue", "darkred"]
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

XSECS_FILE = DATA_DIR + "piae_fuse.tri"
NORMAL_AXIS = 'x'
UNIT = "cm"

MIN_POINTS = 5
START_POS = 4.48

# %% XSec extractor

n_points = int(np.loadtxt(XSECS_FILE, max_rows=1)[0])
xsecs_data = np.loadtxt(XSECS_FILE, skiprows=1, max_rows=n_points)

if NORMAL_AXIS == 'x':
    locs = np.unique(xsecs_data[:, 0])

    xsec_list = []
    for i, loc in enumerate(locs):
        xsec = xsecs_data[xsecs_data[:, 0] == loc][:, 1:]
        xsec_list.append(xsec)

else:
    locs = np.unique(xsecs_data[:, 1])

    xsec_list = []
    for i, loc in enumerate(locs):
        xsec = np.stack((xsecs_data[xsecs_data[:, 1] == loc]
                        [:, 0], xsecs_data[xsecs_data[:, 1] == loc][:, -1]), 1)
        xsec_list.append(xsec)

for i, xsec in enumerate(xsec_list):
    if np.size(xsec, 0) < MIN_POINTS:
        continue

    h_center_val = (np.max(xsec[:, 0]) -
                    np.min(xsec[:, 0]))/2 + np.min(xsec[:, 0])
    v_center_val = (np.max(xsec[:, 1]) -
                    np.min(xsec[:, 1]))/2 + np.min(xsec[:, 1])

    cent_xsec_array = xsec - np.array([h_center_val, v_center_val])

    angle_array = np.arctan2(cent_xsec_array[:, 1], cent_xsec_array[:, 0])
    dist_array = np.sqrt(cent_xsec_array[:, 0]**2 + cent_xsec_array[:, 1]**2)

    sorted_xsec_array = cent_xsec_array[np.lexsort((dist_array, angle_array))]


# %% Plot the XSecs

    fig = plt.figure(dpi=DPI)
    # ax = fig.add_subplot(111)
    # ax.axis('equal')
    # if NORMAL_AXIS == 'x':
    #     ax.set_title("XSec_{0}, x = {1} {2}".format(
    #         i+1, round(locs[i] - locs[0] + START_POS, 3), UNIT))
    #     ax.set_xlabel("y, {0}".format(UNIT))
    #     ax.set_ylabel("z, {0}".format(UNIT))
    # else:
    #     ax.set_title("XSec {0}, y = {1} {2}".format(
    #         i, round(locs[i] - locs[0] + START_POS, 3), UNIT))
    #     ax.set_xlabel("x, {0}".format(UNIT))
    #     ax.set_ylabel("z, {0}".format(UNIT))

    # plot_array = np.vstack((sorted_xsec_array, sorted_xsec_array[0, :]))
    # ax.plot(plot_array[:, 0], plot_array[:, 1], alpha=1)


# # %% Export XSecs as DXF

#     doc = ezdxf.new('R12')
#     msp = doc.modelspace()
#     for k in range(int(np.size(sorted_xsec_array, 0))-1):
#         msp.add_line(sorted_xsec_array[k], sorted_xsec_array[k+1])
#     msp.add_line(sorted_xsec_array[-1], sorted_xsec_array[0])

#     msp.add_line((0.2, 0.2), (0.2, -0.2))
#     msp.add_line((0.2, -0.2), (-0.2, -0.2))
#     msp.add_line((-0.2, -0.2), (-0.2, 0.2))
#     msp.add_line((-0.2, 0.2), (0.2, 0.2))

#     doc.saveas(DXF_EXPORT_DIR + "XSec_{0}.dxf".format(i+1))

# %% Export XSecs as PNG

    fig = plt.figure(dpi=DPI)
    ax = fig.add_subplot(111)
    ax.grid(False)
    ax.axis(False)
    ax.axis('equal')

    plot_array = np.vstack((sorted_xsec_array, sorted_xsec_array[0, :]))
    ax.plot(plot_array[:, 0], plot_array[:, 1], alpha=1)

    height = np.max(sorted_xsec_array[:, 1]) - np.min(sorted_xsec_array[:, 1])
    width = np.max(sorted_xsec_array[:, 0]) - np.min(sorted_xsec_array[:, 0])

    ax.hlines(0, -width/2, width/2, linestyle="dashed", color="red", lw=0.25)
    ax.vlines(0, -height/2, height/2, linestyle="dashed", color="red", lw=0.25)

    ax.hlines(height/2, -width/2, width/2, linestyle="dotted", color="blue", lw=0.25)
    ax.hlines(-height/2, -width/2, width/2, linestyle="dotted", color="blue", lw=0.25)

    fig.savefig(PNG_EXPORT_DIR + "XSec_{0}.png".format(i+1),
        format="png", bbox_inches="tight")
