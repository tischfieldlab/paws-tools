from sleap_io import Labels
from paws_tools.slp_to_csv import get_nodes_for_bodyparts


def assert_lists_equal_ignore_order(actual: list, expected: list):
    """Assertion helper to compare two lists, ignoring order.

    Constrints:
    - Order of the list elements does not matter
    - Duplicates are not allowed
    - Assumed no un-hashable objects in the list

    See:
        https://stackoverflow.com/a/61494686

    Args:
        actual: list of actual values
        expected: list of expected values
    """
    seen = set()
    duplicates = list()
    for x in actual:
        if x in seen:
            duplicates.append(x)
        else:
            seen.add(x)

    lacks = set(expected) - set(actual)
    extra = set(actual) - set(expected)
    message = f"Lacks elements {lacks} " if lacks else ""
    message += f"Extra elements {extra} " if extra else ""
    message += f"Duplicate elements {duplicates}" if duplicates else ""
    assert not message


def test_get_nodes_for_bodyparts(slp_typical: Labels):
    """Test getting the nodes given some bodyparts."""

    # test getting a single bodypart
    nodes = get_nodes_for_bodyparts(slp_typical, slp_typical.skeletons[0].nodes[0].name)
    expected_nodes = [slp_typical.skeletons[0].nodes[0]]
    assert len(nodes) == len(expected_nodes)
    assert_lists_equal_ignore_order(nodes, expected_nodes)

    # test getting all bodyparts explicitly
    nodes = get_nodes_for_bodyparts(slp_typical, slp_typical.skeletons[0].node_names)
    expected_nodes = slp_typical.skeletons[0].nodes
    assert len(nodes) == len(expected_nodes)
    assert_lists_equal_ignore_order(nodes, expected_nodes)

    # test getting all bodyparts via special `all` value
    nodes = get_nodes_for_bodyparts(slp_typical, "all")
    expected_nodes = slp_typical.skeletons[0].nodes
    assert len(nodes) == len(expected_nodes)
    assert_lists_equal_ignore_order(nodes, expected_nodes)
