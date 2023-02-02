"""Please add doc string for this module."""

import os
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sleap_io import Labels, Node
from tqdm import tqdm


def get_nodes_for_bodyparts(labels: Labels, body_parts: Union[str, Node, List[Union[str, Node]]]) -> List[Node]:
    """Given a set of body-part names, return a list of corresponding skeleton nodes.

    Order of returned nodes is not guarenteed!

    Supports the following special values:
    - `all`: return all nodes

    Args:
        labels: labels from which to select bodypart Nodes
        body_parts: list of bodypart names for which to select corresponding Nodes

    Returns:
        list of `Node`s corresponding to body_parts
    """
    # for convience, allow a single string or Node to be passed
    if isinstance(body_parts, str):
        body_parts = [body_parts]

    elif isinstance(body_parts, Node):
        body_parts = [body_parts.name]

    nodes = []
    for bp in body_parts:
        if isinstance(bp, Node):
            bp = bp.name

        if bp == "all":
            nodes.extend(labels.skeletons[0].nodes)
            continue

        if bp not in labels.skeletons[0].node_names:
            raise KeyError(
                f"Unable to find bodypart \"{bp}\" in the skeleton! Available bodyparts: [{', '.join(labels.skeletons[0].node_names)}]"
            )

        nodes.append(labels.skeletons[0][bp])

    return list(set(nodes))


def node_positions_to_dataframe(labels: Labels, nodes: List[Node]) -> pd.DataFrame:
    """Extracts a single node from `labels` and returns its coordinates as a pandas DataFrame.

    Args:
        labels: labels from which to extract data
        nodes: the nodes for which to extract data

    Returns:
       pandas DataFrame containing node coordinates, frame index, and video data. The returned dataframe
       is sorted by video filename and then by frame index, each in ascending order.
    """
    data = []
    for frame in tqdm(labels.labeled_frames, desc="Building Dataframe", leave=False):
        row: Dict[Union[str, Tuple[str, str]], Any] = {
            "video": frame.video.filename,
            "frame_idx": frame.frame_idx,
        }
        for node in nodes:
            row[(node.name, "x")] = frame.predicted_instances[0].points[node].x
            row[(node.name, "y")] = frame.predicted_instances[0].points[node].y
        data.append(row)

    df = pd.DataFrame(data)  # convert to pandas dataframe
    df = df.sort_values(["video", "frame_idx"])  # ensure data is sorted by video name, then by frame_idx
    df = df.set_index(["video", "frame_idx"])  # set the index as a multi-index using video and frame index
    df.columns = pd.MultiIndex.from_product([[n.name for n in nodes], ["x", "y"]])  # set the columns as a multi-index

    return df


def save_dataframe_to_grouped_csv(
    df: pd.DataFrame, groupby: str, dest_dir: str, suffix: Optional[str] = None, format: Literal["tsv", "csv"] = "tsv"
):
    """Split a dataframe into groups, and then save each group as a separate file.

    Args:
        df: dataframe to be saved
        groupby: how to group the dataframe
        dest_dir: destination directory for the produced files
        suffix: any suffix to add to the resulting filenames, just prior to the file extension
        format: format for the saved files, 'tsv' indicates tab-separated values, 'csv' indicated comma-separated values
    """
    # ensure destination directory exists
    os.makedirs(dest_dir, exist_ok=True)

    # generate the full suffix, including file extension
    full_suffix = f"{suffix}.{format}" if suffix is not None else format

    # setup any kwargs to be passed to `DataFrame.to_csv()`
    to_csv_kwargs = {}
    if format == "tsv":
        to_csv_kwargs["sep"] = "\t"

    # group by `groupby`, then save each group to a separate file
    for group, group_df in tqdm(df.groupby(groupby), desc=f"Saving {format.upper()} Files", leave=False):
        base = os.path.splitext(os.path.basename(group))[0]
        dest = os.path.join(dest_dir, f"{base}.{full_suffix}")
        group_df.to_csv(dest, **to_csv_kwargs)


def invert_y_axis(labels: Labels, frame_height: int) -> Labels:
    """Invert the Y-coordinates such that the origin is switched between bottom-left and top-left.

    If the origin is bottom-left, the resulting origin will be top-left.
    If the origin is top-left, the resulting origin will be bottom-left.

    Args:
        labels: labels instance to convert
        frame_height: height of the video frames

    Returns:
        Labels instance with point units converted to physical distances
    """
    for frame in tqdm(labels.labeled_frames, desc="Inverting Y-axis", leave=False):
        for instance in frame.predicted_instances:
            for key, val in instance.points.items():
                instance.points[key].y = frame_height - val.y

    return labels


def convert_physical_units(labels: Labels, top_node: Union[str, Node], bot_node: Union[str, Node], true_dist: float) -> Labels:
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
    for video in tqdm(labels.videos, desc="Calculating Conversion Factors", leave=False):
        box_cords = labels.numpy(video)[:, 0, (Top_index, Bot_index), 1]

        box_median = np.nanmedian(box_cords, axis=0)
        mm2px = true_dist / abs(np.diff(box_median))
        conv_factors[video.filename] = mm2px[0]

    for frame in tqdm(labels.labeled_frames, desc="Applying Conversion Factors", leave=False):
        mm2px = conv_factors[frame.video.filename]
        for instance in frame.predicted_instances:
            for key, val in instance.points.items():
                instance.points[key].x = val.x * mm2px
                instance.points[key].y = val.y * mm2px

    return labels


def slp_csv_plot(slp_csv: str, dest_dir: str, node_name: str = "Toe") -> None:
    """Extracts a single point from `labels` and returns as a pandas DataFrame.

    Saves plot y-coordinates vs. time line graph as a file png in directory.

    Args:
        slp_csv: csv file created by slp_to_paws_csv()
        dest_dir: file path for the destination directory
        node_name: name of the body part node for which ycord_list was extracted from
    """
    ycord_list = pd.read_table(slp_csv)
    ycord_list.sort_values(by=["frame_idx"])
    y_list = ycord_list["y"].tolist()
    fig, ax = plt.subplots(figsize=(20, 10))

    time = [x for x in range(len(y_list))]
    ax.plot(time, y_list)
    ax.set_ylabel(f"{node_name} Y Position")
    ax.set_xlabel("Frame Index")
    ax.set_xticks(np.arange(0, len(time) + 1, 50))
    ax.set_xticklabels(np.arange(0, len(time) + 1, 50), rotation=90)

    video_name = ycord_list["video"][0].split("/")[-1]
    ax.set_title(f"{video_name}_{node_name}_ycord_vs_time")
    ax.axis(xmin=-10, xmax=len(y_list) + 10)
    fig.tight_layout()
    ax.legend([f"{node_name} Y Position"])
    fig.savefig(f"{dest_dir}/{video_name}_{node_name}_ycord_vs_time.png")
