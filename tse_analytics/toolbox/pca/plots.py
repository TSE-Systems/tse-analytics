import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle
from matplotlib.ticker import MaxNLocator
from sklearn.decomposition import PCA


def pca_explained_variance_plot(pca: PCA, figsize: tuple[float, float]) -> Figure:
    fig, axes = plt.subplot_mosaic("AB;CD", figsize=figsize, layout="tight")

    var = [0] + list(np.cumsum(pca.explained_variance_ratio_))
    comp = range(0, len(var))
    axes["A"].plot(comp, var, marker="o", markersize=16, alpha=0.8)
    axes["A"].axhline(y=1, color="black", ls=":")
    axes["A"].set(xlabel="Number of components", ylabel="Explained variance (fraction)")
    axes["A"].xaxis.set_major_locator(MaxNLocator(integer=True))

    var = 1 - np.array([0] + list(np.cumsum(pca.explained_variance_ratio_)))
    comp = range(0, len(var))
    axes["B"].axhline(y=0, color="black", ls=":")
    axes["B"].plot(comp, var, marker="X", markersize=16, alpha=0.8, color="black", linestyle="--")
    axes["B"].set(xlabel="Number of components", ylabel="Residual variance (fraction)")
    axes["B"].xaxis.set_major_locator(MaxNLocator(integer=True))

    var = pca.explained_variance_ratio_
    comp = [f"PC{i + 1}" for i in range(len(var))]
    xpos = range(len(var))
    axes["C"].bar(xpos, var)
    axes["C"].set_xticks(xpos)
    axes["C"].set_xticklabels(
        comp,
        rotation="vertical",
    )
    axes["C"].set(
        xlabel="Principal component",
        ylabel="Explained variance (fraction) per component",
    )

    eigenvalues = pca.explained_variance_
    comp = range(1, len(eigenvalues) + 1)
    axes["D"].plot(comp, eigenvalues, marker="o", markersize=16, lw=3)
    axes["D"].set(title="Scree plot", xlabel="Principal component", ylabel="Eigenvalue")
    axes["D"].xaxis.set_major_locator(MaxNLocator(integer=True))
    axes["D"].set_xlim(min(comp) - 0.25, max(comp) + 0.25)

    return fig


def variable_contributions_plot(pca: PCA, variable_names: list[str], figsize: tuple[float, float]) -> Figure:
    components = pca.components_
    label = "Coefficients"
    # rows: PC, columns: variables
    comp = [f"PC{i + 1}" for i in range(pca.n_components_)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, layout="tight")
    heatmap(
        components.T,
        variable_names,
        comp,
        axi=ax1,
        cbarlabel=label,
        bubble=True,
        cmap="RdBu_r",
        vmin=-1,
        vmax=1,
    )

    components = np.abs(components)
    label = "Absolute coefficients"
    heatmap(
        components.T,
        variable_names,
        comp,
        axi=ax2,
        cbarlabel=label,
        bubble=True,
        cmap="Reds",
        vmin=0,
        vmax=1,
    )

    return fig


def create_bubbles(data, img, axi):
    """Create bubbles for a heat map.

    Parameters
    ----------
    data : object like :class:`numpy.ndarray`
        A 2D numpy array of shape (N, M).
    img : object like :class:`matplotlib.image.AxesImage`
        The heat map image we have generated.
    axi : object like :class:`matplotlib.axes.Axes`
        The axis to add the bubbles to.

    """
    vals = img.get_array()
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            value = img.norm(vals[i, j])
            radius = np.abs(vals[i, j]) * 0.5 * 0.9
            color = img.cmap(value)
            if i % 2 == 0:
                rect = Rectangle((j - 0.5, i - 0.5), 1, 1, color="0.8")
            else:
                rect = Rectangle((j - 0.5, i - 0.5), 1, 1, color="0.9")
            axi.add_artist(rect)
            circle = Circle((j, i), radius=radius, color=color)
            axi.add_artist(circle)
    img.set_visible(False)


def heatmap(data, row_labels, col_labels, axi=None, fig=None, cbar_kw=None, cbarlabel="", bubble=False, **kwargs):
    """Create a heat map from a numpy array and two lists of labels.

    Parameters
    ----------
    data : object like :class:`numpy.ndarray`
        A 2D numpy array of shape (N, M).
    row_labels : list of strings
        A list or array of length N with the labels for the rows.
    col_labels : list of strings
        A list or array of length M with the labels for the columns.
    axi : object like :class:`matplotlib.axes.Axes`, optional
        An axis to plot the heat map. If not provided, a new axis
        will be created.
    fig : object like :class:`matplotlib.figure.Figure`, optional
        The figure where the axes resides in. If given, tight layout
        will be applied.
    cbar_kw : dict, optional
        A dictionary with arguments to the creation of the color bar.
    cbarlabel : string, optional
        The label for the color bar.
    bubble : boolean, optional
        If True, we will draw bubbles indicating the size
        of the given data points.
    **kwargs : dict, optional
        Additional arguments for drawing the heat map.

    Returns
    -------
    fig : object like :class:`matplotlib.figure.Figure`
        The figure in which the heatmap is plotted.
    axi : object like :class:`matplotlib.axes.Axes`
        The axis to which the heatmap is added.
    img : object like :class:`matplotlib.image.AxesImage`
        The generated heat map.
    cbar : object like :class:`matplotlib.colorbar.Colorbar`
        The color bar created for the heat map.

    """
    # Plot the heatmap:
    img = axi.imshow(data, **kwargs)
    # Check if this is a bubble map:
    if bubble:
        create_bubbles(data, img, axi)

    # Create colorbars:
    if cbar_kw is None:
        cbar_kw = {}
    cbar = axi.figure.colorbar(img, ax=axi, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # Show ticks using the provided labels:
    axi.set_xticks(np.arange(data.shape[1]))
    axi.set_xticklabels(col_labels, rotation=-30, horizontalalignment="right", rotation_mode="anchor")
    axi.set_yticks(np.arange(data.shape[0]))
    axi.set_yticklabels(row_labels)

    # Labels on top:
    axi.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

    # Hide spines off:
    for _, spine in axi.spines.items():
        spine.set_visible(False)

    # Add grid:
    axi.grid(False)
    axi.set_xticks(np.arange(data.shape[1] + 1) - 0.5, minor=True)
    axi.set_yticks(np.arange(data.shape[0] + 1) - 0.5, minor=True)
    if bubble:
        axi.grid(which="minor", color="white", linestyle="-", linewidth=3)
        axi.tick_params(which="minor", bottom=False, left=False)
        axi.tick_params(which="major", top=False, left=False)
    else:
        axi.grid(which="minor", color="white", linestyle="-", linewidth=3)
        axi.tick_params(which="minor", bottom=False, left=False)
    if fig is not None:
        fig.tight_layout()
    return fig, axi, img, cbar
