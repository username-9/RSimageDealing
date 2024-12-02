import numpy as np
from scipy.interpolate import griddata
from scipy.stats import gaussian_kde
from matplotlib.colors import LinearSegmentedColormap


def scatter_with_density(X, Y, XList, YList, colorList=None):
    """
    draw scatter picture with dot density plot
    :param X: x location
    :param Y: y location
    :param XList: x list for constructing grid for calculating density
    :param YList: y list for constructing grid for calculating density
    :param colorList: for color mapping to density
    :return: CData: color of each point; h: kernel density of each point; Xmesh, Ymesh, Zmesh: Kernel density surface data
    colorList_for_vis: color list which has been transmitted for visualization
    """
    # Create meshgrid
    XMesh, YMesh = np.meshgrid(XList, YList)
    XYi = np.vstack([XMesh.ravel(), YMesh.ravel()])

    # Perform kernel density estimation
    kde = gaussian_kde([X, Y], bw_method='scott')
    F = kde(XYi).reshape(XMesh.shape)

    # Interpolate the density values back to the original points
    h = griddata(np.vstack([XMesh.ravel(), YMesh.ravel()]).T, F.ravel(), (X, Y), method='linear')

    # Define color list if not provided
    if colorList is None:
        colorList = np.array([
            [0.2700, 0.0000, 0.3300],
            [0.2700, 0.2300, 0.5100],
            [0.1900, 0.4100, 0.5600],
            [0.1200, 0.5600, 0.5500],
            [0.2100, 0.7200, 0.4700],
            [0.5600, 0.8400, 0.2700],
            [0.9900, 0.9100, 0.1300]
        ])

    # Create color mapping function
    def colorFuncFactory(colorList):
        x = np.linspace(0, 1, len(colorList))
        y1, y2, y3 = colorList.T

        def colorFunc(X):
            return np.array([np.interp(X, x, y1), np.interp(X, x, y2), np.interp(X, x, y3)]).T

        return colorFunc

    colorFunc = colorFuncFactory(colorList)

    # Normalize h and map to colors
    h_norm = (h - np.min(h)) / (np.max(h) - np.min(h))
    CData = colorFunc(h_norm)

    # Create colormap for visualization (if needed)
    cmap = LinearSegmentedColormap.from_list('custom_cmap', colorList / 255.0)
    colorList_for_vis = cmap(np.linspace(0, 1, 100))[:, :3]  # Convert to RGB for visualization

    return CData, h, XMesh, YMesh, F, colorList_for_vis

# Example usage:
# X, Y = ...  # Your data points
# XList, YList = np.linspace(...), np.linspace(...)  # Define your meshgrid limits and resolution
# CData, h, XMesh, YMesh, ZMesh, colorList = density2C(X, Y, XList, YList)