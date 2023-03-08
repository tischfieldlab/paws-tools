"""Please add doc string for this module."""

import os
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from sleap_io import Labels, Node, Track
from tqdm import tqdm
from typing_extensions import Literal


def add_track_to_slp(labels: Labels):
    """Adds sleap_io Track to 'labels' and return the updated 'labels'

    Args:
        labels: labels from which to extract data

    Returns:
        labels updated with added Track
    """

    my_track = Track("mouse")

    for frame in labels.labeled_frames:
        for instance in frame.predicted_instances:
            instance.track = my_track

    return labels


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

    Only the first predicted instance in each frame will be used.

    If a given frame does not have any predicted instances or the predicted instance does not contain
    a node in `nodes`, then the coordinates for that node and frame will be set to `numpy.nan` in the
    resulting dataframe.

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
            if (len(frame.predicted_instances) <= 0) or (node not in frame.predicted_instances[0].points):
                # we don't have any predicted instances, or this node was not present in this predicted instance
                # allocate space in the dataframe for this point, but set the values to NaNs.
                row[(node.name, "x")] = np.nan
                row[(node.name, "y")] = np.nan
            else:
                row[(node.name, "x")] = frame.predicted_instances[0].points[node].x
                row[(node.name, "y")] = frame.predicted_instances[0].points[node].y
        data.append(row)

    df = pd.DataFrame(data)  # convert to pandas dataframe
    df = df.sort_values(["video", "frame_idx"])  # ensure data is sorted by video name, then by frame_idx
    df = df.set_index(["video", "frame_idx"])  # set the index as a multi-index using video and frame index
    df.columns = pd.MultiIndex.from_product([[n.name for n in nodes], ["x", "y"]])  # set the columns as a multi-index

    return df


def read_dataframe_from_csv(filename: str) -> pd.DataFrame:
    """Read a csv file and convert to a dataframe.

    Handles automatically detecting the delimiter type (tab for TSV files or comma for CSV)
    Handles correctly constructing the multi-index

    Args:
        filename: path to the file to read

    Returns:
        `pandas.DataFrame` containing data read from the csv file
    """
    kwargs = {}
    if filename.lower().endswith("tsv"):
        kwargs["sep"] = "\t"

    return pd.read_csv(filename, index_col=[0, 1], header=[0, 1], **kwargs)


def save_dataframe_to_grouped_csv(
    df: pd.DataFrame, groupby: str, dest_dir: str, suffix: Optional[str] = None, format: Literal["tsv", "csv"] = "tsv"
) -> List[str]:
    """Split a dataframe into groups, and then save each group as a separate file.

    Args:
        df: dataframe to be saved
        groupby: how to group the dataframe
        dest_dir: destination directory for the produced files
        suffix: any suffix to add to the resulting filenames, just prior to the file extension
        format: format for the saved files, 'tsv' indicates tab-separated values, 'csv' indicated comma-separated values

    Returns:
        A list of strings indicating the filepaths which were saved to
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
    out_filenames = []
    for group, group_df in tqdm(df.groupby(groupby), desc=f"Saving {format.upper()} Files", leave=False):
        base = os.path.splitext(os.path.basename(group))[0]
        dest = os.path.join(dest_dir, f"{base}.{full_suffix}")
        out_filenames.append(dest)
        group_df.to_csv(dest, **to_csv_kwargs)

    return out_filenames


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
        try:
            box_cords = labels.numpy(video)[:, 0, (Top_index, Bot_index), 1]
            box_median = np.nanmedian(box_cords, axis=0)
            mm2px = true_dist / abs(np.diff(box_median))
            conv_factors[video.filename] = mm2px[0]

        except:
            tqdm.write(f'WARNING: Unable to find coordinates for calibration nodes! Skipping calibration for video "{video.filename}"')
            conv_factors[video.filename] = None

    for frame in tqdm(labels.labeled_frames, desc="Applying Conversion Factors", leave=False):
        mm2px = conv_factors[frame.video.filename]
        if mm2px is not None:
            for instance in frame.predicted_instances:
                for key, val in instance.points.items():
                    instance.points[key].x = val.x * mm2px
                    instance.points[key].y = val.y * mm2px

    return labels


def plot_bodyparts_y_pos_over_time(
    df: Union[pd.DataFrame, str],
    dest_dir: str,
    nodes: List[Union[Node, str]],
    ax: Axes = None,
    suffix: Optional[str] = None,
    format: str = "png",
) -> None:
    """Extracts a single point from `labels` and returns as a pandas DataFrame.

    Saves plot y-coordinates vs. time line graph as a file png in directory.

    Args:
        df: a `pandas.DataFrame` created by `node_positions_to_dataframe()` or a path to a file containing equivelent data
        dest_dir: file path for the destination directory
        nodes: bodyparts for which to plot
        ax: Axes to plot on, if not provided, one will be created
        suffix: any suffix to add to the resulting filenames, just prior to the file extension
        format: format for the saved plots, 'png' is the default
    """
    if isinstance(df, str):
        df = read_dataframe_from_csv(df)

    # convert nodes to strings
    str_nodes = [node.name if isinstance(node, Node) else node for node in nodes]

    if ax is None:
        fig, ax = plt.subplots(figsize=(20, 10))
        own_fig = True
    else:
        fig = ax.get_figure()
        own_fig = False

    palette = sns.color_palette("Paired", len(str_nodes))

    for i, node in enumerate(str_nodes):
        ax.plot(df.index.get_level_values("frame_idx"), df[(node, "y")], c=palette[i])

    ax.set_ylabel(f"Bodypart Y Position")
    ax.set_xlabel("Frame Index")
    ax.legend([f"{node}" for node in str_nodes])
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))

    video_name = os.path.basename(df.index.get_level_values("video")[0])
    node_names = "_".join([node for node in str_nodes])
    ax.set_title(f"{video_name}_[{node_names}]_ycord_vs_time")

    max_x = int(df.index.max()[1])
    ax.set_xticks(np.arange(0, max_x, 50))
    ax.set_xticklabels(np.arange(0, max_x, 50), rotation=90)
    ax.axis(xmin=-10, xmax=max_x + 10)

    fig.tight_layout()

    # ensure destination directory exists
    os.makedirs(dest_dir, exist_ok=True)

    # generate the full suffix, including file extension
    full_suffix = f"{suffix}.{format}" if suffix is not None else format
    dest = os.path.join(dest_dir, f"{video_name}_[{node_names}]_ycord_vs_time.{full_suffix}")
    fig.savefig(dest)
    if own_fig:
        plt.close(fig)
