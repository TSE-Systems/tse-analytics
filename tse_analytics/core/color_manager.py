import seaborn as sns
from matplotlib.colors import rgb2hex

from tse_analytics.core.data.shared import Animal, Factor

colormap_name = "tab20"
cmap = sns.color_palette(colormap_name, as_cmap=True)
# cmap = distinctipy.get_colormap(distinctipy.get_colors(32, pastel_factor=0.8))


def get_color_tuple(index: int) -> tuple[float, float, float, float]:
    if index > cmap.N:
        index = index - (cmap.N * (index // cmap.N))
    return cmap(index)


def get_color_hex(index: int) -> str:
    return rgb2hex(get_color_tuple(index))


def get_animal_to_color_dict(animals: dict[str, Animal]) -> dict[str, str]:
    result = {}
    for animal in animals.values():
        result[animal.id] = animal.color
    return result


def get_level_to_color_dict(factor: Factor) -> dict[str, str]:
    result = {}
    for level in factor.levels:
        result[level.name] = level.color
    return result
