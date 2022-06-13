import numpy as np
import matplotlib.pylab as plt
import seaborn as sns
import ezdxf

DPI = 300
COLORS = ["darkblue", "darkred", "darkgreen", "darkorange",
          "darkcyan", "darkmagenta", "dimgray", "goldenrod"]
sns.set_theme(style="whitegrid", font="Palatino Linotype",
              context="paper", palette=COLORS)

DATA_DIR = "meshes/"
EXPORT_DIR = "dxf_files/"

# %% Specify .tir file name and main axis

XSECS_FILE = DATA_DIR + "f16.tri"
NORMAL_AXIS = 'x'


# %% XSec extractor

n_points = int(np.loadtxt(XSECS_FILE, max_rows=1)[0])
xsecs_data = np.loadtxt(XSECS_FILE, skiprows=1, max_rows=n_points)

if NORMAL_AXIS == 'x':
    locs = np.unique(xsecs_data[:, 0])

    xsecs_list = []
    for i in range(len(locs)):
        xsec = xsecs_data[xsecs_data[:, 0] == locs[i]][:, 1:]
        xsecs_list.append(xsec)

else:
    locs = np.unique(xsecs_data[:, 1])

    xsecs_list = []
    for i in range(len(locs)):
        xsec = np.stack((xsecs_data[xsecs_data[:, 1] == locs[i]]
                        [:, 0], xsecs_data[xsecs_data[:, 1] == locs[i]][:, -1]), 1)
        xsecs_list.append(xsec)

for i, xsec in enumerate(xsecs_list):
    h_center_val = (np.max(xsec[:, 0]) -
                    np.min(xsec[:, 0]))/2 + np.min(xsec[:, 0])
    v_center_val = (np.max(xsec[:, 1]) -
                    np.min(xsec[:, 1]))/2 + np.min(xsec[:, 1])

    righthalf_points = xsec[xsec[:, 0] >= h_center_val]
    quad1_points = righthalf_points[righthalf_points[:, 1] > v_center_val]
    quad4_points = righthalf_points[righthalf_points[:, 1] < v_center_val]

    sorted_quad1_points = quad1_points[quad1_points[:, 1].argsort()]
    sorted_quad4_points = quad4_points[quad4_points[:, 1].argsort()]
    sorted_righthalf_points = np.vstack(
        (sorted_quad4_points, sorted_quad1_points))

    lefthalf_points = xsec[xsec[:, 0] < h_center_val]
    quad2_points = lefthalf_points[lefthalf_points[:, 1] >= v_center_val]
    quad3_points = lefthalf_points[lefthalf_points[:, 1] <= v_center_val]

    sorted_quad2_points = quad2_points[quad2_points[:, 1].argsort()[::-1]]
    sorted_quad3_points = quad3_points[quad3_points[:, 1].argsort()[::-1]]
    sorted_lefthalf_points = np.vstack(
        (sorted_quad2_points, sorted_quad3_points))

    sorted_xsec = np.vstack((sorted_righthalf_points, sorted_lefthalf_points))

    norm_xsec = np.stack(
        (sorted_xsec[:, 0] - h_center_val, sorted_xsec[:, 1] - v_center_val), 1)

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
    ax.plot(norm_xsec[:, 0], norm_xsec[:, 1])

# %% Export XSecs as .dxf file

    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    for k in range(int(np.size(sorted_xsec, 0))-1):
        msp.add_line(norm_xsec[k], norm_xsec[k+1])
    msp.add_line(norm_xsec[-1], norm_xsec[0])
    doc.saveas(EXPORT_DIR + "XSec_{0}.dxf".format(i))
