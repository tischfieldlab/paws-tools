"""Fixtures that return paths to .slp files."""
import pytest
import sleap_io


@pytest.fixture
def slp_typical() -> sleap_io.Labels:
    """Typical SLP file including  `PredictedInstance`, `Instance`, `Track` and `Skeleton` objects."""
    return sleap_io.load_slp(r"H:\Abraira_Lab\Tom V\2022_08_12_SLEAP\labels.v004.slp")
