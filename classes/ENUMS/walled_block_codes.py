from enum import Enum

from classes.ENUMS.block_codes import block_codes


class walled_block_codes(Enum):
    """Material block codes for which cannot be built upon

    Args:
        Enum ([type]): [description]
    """

    WATER = block_codes.WATER
    HOUSE = block_codes.HOUSE
    PROPOSE = block_codes.PROPOSED
    FENCE = block_codes.FENCE
