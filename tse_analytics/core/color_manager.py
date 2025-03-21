import seaborn as sns
from matplotlib.colors import rgb2hex

colormap_name = "tab20"
cmap = sns.color_palette(colormap_name, as_cmap=True)


def get_color_tuple(index: int) -> tuple[float, float, float, float]:
    if index > cmap.N:
        index = index - (cmap.N * (index // cmap.N))
    return cmap(index)


def get_color_hex(index: int) -> str:
    return rgb2hex(get_color_tuple(index))
