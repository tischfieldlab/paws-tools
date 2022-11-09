import click
import sleap_io
import pandas as pd

from paws_tools.slp_to_csv import get_xy_list_from_labels


@click.group()
@click.version_option()
def cli():
    """Toolbox for working with PAWS"""
    pass  # pylint: disable=unnecessary-pass


@cli.command(name="slp-to-paws-csv", short_help="convert SLEAP .slp file to PAWS importable csv files")
@click.argument("slp_file", type=click.Path(exists=True, dir_okay=False))
@click.option("-bp", "--body-part", default="Toe", help="Name of the body part to extract")
def slp_to_paws_csv(slp_file, body_part):
    """Please document this with doc strings. The information shows up in the CLI
    when the --help flag is passed
    """

    labels = sleap_io.load_slp(slp_file)

    # get_xy_list_from_labels(labels, node_name='Toe')
    toe_x, toe_y = get_xy_list_from_labels(labels, body_part)

    coor = pd.DataFrame({"x": toe_x, "y": toe_y})

    coor.to_csv("toe_xy.tsv", sep="\t", index=False)


if __name__ == "__main__":
    cli()
