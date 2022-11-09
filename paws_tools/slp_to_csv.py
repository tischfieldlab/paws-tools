from sleap_io import Labels


def get_name_list(labels: Labels) -> list[str]:
    """Please add doc strings to you functions

    Parameters:
    labels (Labels): What are these labels for?

    Returns:
    list[str] - List of node names found in Labels
    """
    node_name_list = []
    for frame in labels.labeled_frames:
        user_instances = frame.user_instances

        n_user_instances = len(user_instances)
        if n_user_instances == 0:
            continue  # skip frames which do not have a ground truth annotation

        f_length = len(frame.user_instances[0].skeleton.nodes)
        # print(f_length)

        for i in range(f_length):
            node_name_list.append(frame.user_instances[0].skeleton.nodes[i].name)

        # break

    return node_name_list


def get_xy_list_from_labels(labels: Labels, node_name: str = "Toe") -> tuple[list[float], list[float]]:
    """Please add doc strings to you functions

    Parameters:
    labels (Labels): What are these labels you are taking?
    node_name (str): What is node_name, and how does it affect this function

    Returns:
    tuple of lists of float - list of the x and y positions, respectively
    """

    topbox = "Top_Box"
    botbox = "Bot_Box"

    x_list = []
    y_list = []

    # make node_name_list to record the index of the target node
    node_name_list = get_name_list(labels)
    # print(node_name_list)

    for frame in labels.labeled_frames:

        user_instances = frame.user_instances
        n_user_instances = len(user_instances)

        # skip if no ground truth annotation
        if n_user_instances == 0:
            continue

        # need to get x,y by node name

        # calculate distance and mm
        top_index = node_name_list.index(topbox)
        top_y = frame.user_instances[0][top_index].y

        bot_index = node_name_list.index(botbox)
        bot_y = frame.user_instances[0][bot_index].y

        dist_frame = abs(top_y - bot_y)

        # 50 mm bc of camera angle
        unit_pixels_mm = float(dist_frame / 50)

        # index of target node to get x,y
        node_index = node_name_list.index(node_name)

        # want input unit as mm, thus pixels/(pixels/mm)
        x_list.append(frame.user_instances[0][node_index].x / unit_pixels_mm)
        y_list.append(frame.user_instances[0][node_index].y / unit_pixels_mm)

    return x_list, y_list
