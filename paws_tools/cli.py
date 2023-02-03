"""CLI entry-point for paws-tools."""


import copy
import os
from typing import List, Literal

import click
import sleap_io
from tqdm import tqdm

from paws_tools.slp_to_csv import (
    convert_physical_units,
    get_nodes_for_bodyparts,
    invert_y_axis,
    node_positions_to_dataframe,
    save_dataframe_to_grouped_csv,
    plot_bodyparts_y_pos_over_time,
)
from paws_tools.util import click_monkey_patch_option_show_defaults


# Show click option defaults
click_monkey_patch_option_show_defaults()


@click.group()
@click.version_option()
def cli():
    """Toolbox for working with PAWS."""
    pass  # pylint: disable=unnecessary-pass


@cli.command(name="slp-to-csv", short_help="Convert SLEAP .slp file to PAWS importable csv files")
@click.argument("slp_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "-bp",
    "--body-part",
    default=["Toe"],
    multiple=True,
    help="Name of the body part(s) to extract. Also accepts special value 'all', which will select all bodyparts.",
)
@click.option(
    "-ibp",
    "--ignore-body-part",
    multiple=True,
    help="Name of body part(s) to ignore. These will be subtracted from the set specified by --body-part.",
)
@click.option("--calibrate/--no-calibrate", default=True, help="Perform calibration to physical units")
@click.option("--cal-node1", default="Top_Box", help="Name of calibration point one")
@click.option("--cal-node2", default="Bot_Box", help="Name of calibration point two")
@click.option("--cal-dist", default=1.0, type=float, help="Physical distance between --cal-node1 and --cal-node2")
@click.option("--frame-height", default=512, type=int, help="Pixel height of video frames, used to invert the y-axis")
@click.option(
    "--format",
    type=click.Choice(["tsv", "csv"]),
    default="tsv",
    help="Format of the resulting files: 'tsv' gives tab-separated values, 'csv' gives comma-separated values",
)
@click.option(
    "--dest-dir",
    default=os.getcwd(),
    type=click.Path(file_okay=False),
    help="Directory where resulting files should be saved",
)
@click.option("--plot/--no-plot", default=True, help="Plot traces of the bodyparts")
def slp_to_csv(
    slp_file: str,
    body_part: List[str],
    ignore_body_part: List[str],
    calibrate: bool,
    cal_node1: str,
    cal_node2: str,
    cal_dist: float,
    frame_height: int,
    format: Literal["tsv", "csv"],
    dest_dir: str,
    plot: bool,
):
    """Given a SLEAP *.slp file, extract the coordinates for the body-part(s) specified by \
--body-part and then, for each video in the dataset, save a delimiter-separated-values (TSV/CSV) file, and generate trace plot.

    Add body-parts to be extracted through the -bp or --body-part options. This also accepts a special
    value, 'all', which will use all body-parts found in the slp file. Body-parts can be removed from the
    final set through the use of -ibp or --ignore-body-part.

    Additionally, this command will convert from pixel units to physical units given proper
    calibration information. See options --cal-*. Use --calibrate (default) to turn on calibration
    or --no-calibrate to turn off calibration. If calibration is turned on, both pixel-unit and physical-unit
    variants of the data will be saved, otherwise only pixel-unit data will be saved.

    Use --format to specify the format of the resulting data. 'tsv' for tab-separated values,
    or 'csv' for comma-separated values.

    The y-axis may also be inverted given --frame-height.
    """
    print()  # give some breathing room in the console

    # parse the provided *.slp file
    print("Loading SLEAP data (this may take a few minutes)....")
    labels = sleap_io.load_slp(slp_file)
    print(" -> Done!\n")

    # get the nodes to operate upon
    nodes = get_nodes_for_bodyparts(labels, body_part)
    ignore_nodes = get_nodes_for_bodyparts(labels, ignore_body_part)
    nodes = list(set(nodes) - set(ignore_nodes))  # subtract any nodes the user wanted to ignore

    # convert labels coords to physical units
    labels = invert_y_axis(labels, frame_height)
    coords = node_positions_to_dataframe(labels, nodes)
    csv_files = save_dataframe_to_grouped_csv(coords, "video", dest_dir, "px", format=format)

    if plot:
        for csv_file in tqdm(csv_files, desc="Generating Plots (non-calibrated)", leave=False):
            plot_bodyparts_y_pos_over_time(csv_file, dest_dir, nodes)

    if calibrate:
        labels = convert_physical_units(copy.deepcopy(labels), cal_node1, cal_node2, cal_dist)
        coords = node_positions_to_dataframe(labels, nodes)
        csv_files = save_dataframe_to_grouped_csv(coords, "video", dest_dir, "mm", format=format)

        if plot:
            for csv_file in tqdm(csv_files, desc="Generating Plots (non-calibrated)", leave=False):
                plot_bodyparts_y_pos_over_time(csv_file, dest_dir, nodes)


@cli.command(name="slp-to-paws-plot-trace", short_help="Plot slp_csv file to body part trace graph png file")
@click.argument("slp_csv", type=click.Path(exists=True, dir_okay=False))
@click.option("-bp", "--body-part", default="Toe", help="Name of the body part to extract")
@click.option(
    "--dest-dir",
    default=os.getcwd(),
    type=click.Path(file_okay=False),
    help="Directory where resulting TSV files should be saved",
)
def plot_trace(slp_csv: str, dest_dir: str, body_part: str):
    """Given a str slp_csv file name and destination directionry filename (dest_dir), and spicified by body-part -bp.

    Save a png file named f"{video_name}_{body_part}_ycord_vs_time.png" trace graph and saved to destination directory.
    """
    plot_bodyparts_y_pos_over_time(slp_csv, dest_dir, [body_part])


if __name__ == "__main__":
    cli()
