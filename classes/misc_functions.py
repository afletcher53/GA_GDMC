from classes.Types import GridLocation
from typing import Tuple
from classes.ENUMS.orientations import orientations
from constants import MINECRAFT_USERNAME
from vendor.gdmc_http_client.interfaceUtils import runCommand


def get_build_coord(location: GridLocation, building_radius: int) -> list:
    """Get building locations for buidling based on radius

    Args:
        location (GridLocation): Centre of the building
        building_radius ([type]): Building radius

    Returns:
        list: Vectors used to paint building
    """
    build_cord = []
    start_z = location[1] - building_radius
    end_z = (location[1] + building_radius) + 1
    for x_value in range(
        (location[0] - building_radius), ((location[0] + building_radius) + 1)
    ):
        for z_value in range(start_z, end_z):
            build_cord.append((x_value, z_value))
    return build_cord


def rectangles_overlap(
    rect1: Tuple[int, int, int, int], rect2: Tuple[int, int, int, int]
) -> bool:
    def point_in_rectangle(
        rect: Tuple[int, int, int, int], point: Tuple[int, int]
    ) -> bool:
        return rect[0] <= point[0] <= rect[2] and rect[1] <= point[1] <= rect1[3]

    # bottom left corner of rect 2 in rect 1
    if point_in_rectangle(rect1, (rect2[0], rect2[1])):
        return True

    # bottom right corner of rect 2 in rect 1
    if point_in_rectangle(rect1, (rect2[2], rect2[1])):
        return True

    # top left corner of rect 2 in rect 1
    if point_in_rectangle(rect1, (rect2[0], rect2[3])):
        return True

    # top right corner of rect 2 in rect 1
    if point_in_rectangle(rect1, (rect2[2], rect2[3])):
        return True

    return False


def cut_out_bounds(value: int, maximum: int) -> int:
    return max(min(value, maximum), 0)


def draw_sign(
    x: int,
    y: int,
    z: int,
    facing_direction: orientations,
    text_line_1: str,
    text_line_2: str = "",
    text_line_3: str = "",
    text_line_4: str = "",
) -> str:

    # /setblock 301 69 269 birch_sign[rotation=5]{Text1:'"My chest"',Text2:'"Do not open!"'}

    rotation_value = ["4", "8", "12", "0"][facing_direction.value]  # wnes

    return runCommand(
        "setblock "
        + str(x)
        + " "
        + str(y)
        + " "
        + str(z)
        + " birch_sign[rotation="
        + rotation_value
        + "]"
        + "{Text1:'\""
        + text_line_1
        + "\"', "
        "Text2:'\"" + text_line_2 + "\"', "
        "Text3:'\"" + text_line_3 + "\"', "
        "Text4:'\"" + text_line_4 + "\"'}"
    )


def teleport_player(x_value: int, y_value: int, z_value: int):
    tp_string = (
        "tp "
        + MINECRAFT_USERNAME
        + " "
        + str(x_value)
        + " "
        + str(y_value)
        + " "
        + str(z_value)
    )
    runCommand(tp_string)
