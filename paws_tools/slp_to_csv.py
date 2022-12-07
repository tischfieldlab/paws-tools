"""Please add doc string for this module."""

import pandas as pd
from sleap_io import Labels
import numpy as np


def node_positions_to_dataframe(labels: Labels, node_name: str = "Toe") -> pd.DataFrame:
    """Extracts a single point from `labels` and returns as a pandas DataFrame.

    Args:
        labels: labels from which to extract data
        node_name: name of the node for which to extract data

    Returns:
       pandas DataFrame containing node locations, frame index, and video data
    """
    data = []
    node = labels.skeletons[0][node_name]
    for frame in labels.labeled_frames:

        data.append(
            {
                "video": frame.video.filename,
                "frame_idx": frame.frame_idx,
                "x": frame.predicted_instances[0].points[node].x,
                "y": frame.predicted_instances[0].points[node].y,
            }
        )

    return pd.DataFrame(data)


def convert_physical_units(
    labels: Labels, top_node: str, bot_node: str, pix_height: int, true_distance: float
) -> Labels:
    """Converts the coordinates in `labels` from px to physical distance units (i.e. millimeters).

    Args:
        labels: labels instance to convert
        top_node: node name of first calibration point
        bot_node: node name of second calibration point
        true_distance: true physical distance between `top_node` and `bot_node`

    Returns:
        Labels instance with point units converted to physical distances
    """
    Top_index = labels.skeletons[0].index(top_node)
    Bot_index = labels.skeletons[0].index(bot_node)

    conv_factors = {}
    for video in labels.videos:
        box_cords = labels.numpy(video)[:, 0, (Top_index, Bot_index), 1]

        box_median = np.nanmedian(box_cords, axis=0)
        mm2px = true_distance / abs(np.diff(box_median))
        conv_factors[video.filename] = mm2px[0]

    for frame in labels.labeled_frames:
        mm2px = conv_factors[frame.video.filename]
        height = 512
        for instance in frame.predicted_instances:
            for key, val in instance.points.items():
                instance.points[key].x = val.x * mm2px
                instance.points[key].y = (height - val.y) * mm2px

    return labels
