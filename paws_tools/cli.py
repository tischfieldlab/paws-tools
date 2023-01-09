"""CLI entry-point for paws-tools."""


import os

import click
import sleap_io

from paws_tools.slp_to_csv import convert_physical_units, invert_y_axis, node_positions_to_dataframe, slp_csv_plot
from paws_tools.util import click_monkey_patch_option_show_defaults


# Show click option defaults
click_monkey_patch_option_show_defaults()


@click.group()
@click.version_option()
def cli():
    """Toolbox for working with PAWS."""
    pass  # pylint: disable=unnecessary-pass


@cli.command(name="slp-to-paws-csv", short_help="Convert SLEAP .slp file to PAWS importable csv files")
@click.argument("slp_file", type=click.Path(exists=True, dir_okay=False))
@click.option("-bp", "--body-part", default="Toe", help="Name of the body part to extract")
@click.option("--cal-node1", default="Top_Box", help="Name of calibration point one")
@click.option("--cal-node2", default="Bot_Box", help="Name of calibration point two")
@click.option("--cal-dist", default=1.0, type=float, help="Physical distance between --cal-node1 and --cal-node2")
@click.option("--frame-height", default=512, type=int, help="Pixel height of video frames")
@click.option(
    "--dest-dir",
    default=os.getcwd(),
    type=click.Path(file_okay=False),
    help="Directory where resulting TSV files should be saved",
)
def slp_to_paws_csv(
    slp_file: str, body_part: str, cal_node1: str, cal_node2: str, cal_dist: float, frame_height: int, dest_dir: str
):
    """Given a SLEAP *.slp file, extract the coordinates for the body part specified by \
--body-part and save a tab-separated-values (TSV) file, for each video in the dataset.

    Additionally, this command will convert from pixel units to physical units given proper
    calibration information. See options --cal-*.

    The y-axis may also be inverted given --frame-height.
    """
    labels = sleap_io.load_slp(slp_file)

    # convert labels coords to physical units
    labels = invert_y_axis(labels, frame_height)
    labels = convert_physical_units(labels, cal_node1, cal_node2, cal_dist)
    coords = node_positions_to_dataframe(labels, body_part)

    # for each video, save the dataframe subset to a TSV file
    os.makedirs(dest_dir, exist_ok=True)
    for group, df in coords.groupby("video"):
        base = os.path.splitext(os.path.basename(group))[0]
        dest = os.path.join(dest_dir, f"{base}.tsv")
        df.to_csv(dest, sep="\t", index=False)


cli.command(name="slp-to-paws-plot", short_help="Plot slp_csv file to trace graph png file")


@click.argument("slp_csv", type=click.Path(exists=True, dir_okay=False))
@click.option("-bp", "--body-part", default="Toe", help="Name of the body part to extract")
@click.option(
    "--dest-dir",
    default=os.getcwd(),
    type=click.Path(file_okay=False),
    help="Directory where resulting TSV files should be saved",
)
def plot_trace(slp_csv: str, dest_dir: str, body_part: str):
    """Given a str slp_csv file name and destination directionry filename (dest_dir), and\
--body-part and save a png file of trace graph from slp_csv file to destination directory.
    """

    slp_csv_plot(slp_csv, dest_dir, body_part)


if __name__ == "__main__":
    cli()
