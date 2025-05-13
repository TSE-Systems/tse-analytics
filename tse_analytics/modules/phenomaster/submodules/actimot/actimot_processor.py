import numpy as np
import pandas as pd
import traja
from PySide6.QtGui import QImage, QPixmap

from tse_analytics.modules.phenomaster.submodules.actimot.actimot_settings import ActimotSettings

x_range = range(64)
y_range = range(32)


def get_normalized_bit(value, bit_index):
    return (value >> bit_index) & 1


def get_bit(value, bit_index):
    return value & (1 << bit_index)


lookup_table = []
for bit in range(64):
    lookup_table.append(1 << bit)


def get_bit_lookup(value, bit_index):
    return value & lookup_table[bit_index]


def get_centroid(value, value_range):
    result = 0
    bits_count = 0
    for i in value_range:
        if get_normalized_bit(value, i) == 0:
            result += i
            bits_count += 1

    if bits_count != 0:
        return result / bits_count
    else:
        return np.nan


def get_centroid_lookup(value, value_range):
    result = 0
    bits_count = 0
    for i in value_range:
        if get_bit_lookup(value, i) == 0:
            result += i
            bits_count += 1

    if bits_count != 0:
        return result / bits_count
    else:
        return np.nan


def get_pixmap_and_centroid(x: int, y: int) -> (QPixmap, tuple):
    bitmask = np.zeros([32, 64], dtype=np.uint8)

    for index_x in x_range:
        if get_normalized_bit(x, index_x) == 0:
            for index_y in y_range:
                if get_normalized_bit(y, index_y) == 0:
                    bitmask[index_y, index_x] = 255

    centroid = [np.average(indices) for indices in np.where(bitmask == 255)]

    image = QImage(bitmask, 64, 32, 64, QImage.Format.Format_Indexed8)
    pixmap = QPixmap.fromImage(image)

    return pixmap, centroid


def calculate_trj(original_df: pd.DataFrame, actimot_settings: ActimotSettings) -> (pd.DataFrame, traja.TrajaDataFrame):
    df = original_df[["DateTime", "X", "Y"]].copy()
    df.dropna(subset=["X", "Y"], inplace=True)
    df.reset_index(inplace=True, drop=True)

    first_timestamp = df.at[0, "DateTime"]
    df["time"] = df["DateTime"] - first_timestamp

    df["x"] = df["X"].apply(get_centroid_lookup, value_range=x_range)
    df["y"] = df["Y"].apply(get_centroid_lookup, value_range=y_range)

    # df["CentX"] = df["X"].map(lambda  x: get_centroid(x, x_range))
    # df["CentY"] = df["Y"].map(lambda  x: get_centroid(x, y_range))

    # df["CentX"] = df["X"].apply(get_centroid, value_range=x_range)
    # df["CentY"] = df["Y"].apply(get_centroid, value_range=y_range)

    trj_df = traja.from_df(df=df)
    trj_df.spatial_units = "cm"

    if actimot_settings.use_smooting:
        trj_df = traja.smooth_sg(
            trj_df, w=actimot_settings.smoothing_window_size, p=actimot_settings.smoothing_polynomial_order
        )

    preprocessed_trj = traja.get_derivatives(trj_df)

    result = pd.concat([df, preprocessed_trj], ignore_index=False, axis="columns")
    result.reset_index(inplace=True, drop=True)

    return result, trj_df
