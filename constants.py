"""Constants for the project"""

from classes.ENUMS.biome_ids import biome_regions
from classes.ENUMS.block_codes import block_codes
from typing import Tuple, Dict

MAX_BUILDING_RADIUS: int = 13  # SHOULD BE ODD
MIN_BUILDING_RADIUS: int = 7
WATER_DISTANCE_WEIGHTING: float = 1.75
BUILDING_DISTANCE_WEIGHTING: float = 2
FLATNESS_FITNESS_WEIGHTING: float = 1
DEFAULT_MUTATION_RATE: float = 1 / 6
DEFAULT_POPULATION_SIZE: int = 5
GENERATIONS: int = 20
BUILDING_NUMBER: int = 50
POPULATION_SIZE: int = 100
AREA: Tuple[int, int, int, int] = (
    0,
    0,
    256,
    256,
)  # x position, z position, x size, z size
WATER_SEARCH_RADIUS: int = (
    MAX_BUILDING_RADIUS * 2
)  # How far to search from building location for water, should be larger than MAX_BUILDING_RADIUS
MAXIMUM_WATER_DISTANCE_PENALTY: int = MAX_BUILDING_RADIUS
MAXIMUM_HOUSE_DISTANCE_PENALTY: int = max(AREA[2], AREA[3])

IMAGE_DIR_FOLD: str = "data/images"

USE_BFS_WITH_LOCATION_COUNT = 12  # Set the number of properties BFS is used, above this number MCTS is used.  Set to -1 if want MCTS all the time...
MCTS_TIME_LIMIT_SECONDS: int = 120

DEBUG_DRAW_WORKINGS: bool = False  # yellow/orange-first in frontier, light blue-candidate, NOT_POSSIBLE: Gray-drop or black
MAX_DETOUR: int = 110
VISITS_PER_BUILDING_TYPE: Tuple[int] = (
    0,  # building_types.HOUSE
    2,  # building_types.RESTAURANT
    5,  # building_types.FACTORY
    3,  # building_types.SHOP
    0,  # building_types.FLATS
    1,  # building_types.TOWN_HALL
)
BLOCK_BATCH_SIZE: int = 1000
MAX_HEIGHT: int = 255
GRID_WIDTH: int = 15
NUMBER_OF_FAMILIES_IN_A_FLAT: int = 5
DRIVE_LENGTH: int = 1
BUILDING_MARGIN: int = 3
RANDOM_SEED: int = 10


# Dictionary mapping biome ID to internal biome regional id
BIOME_MAP_DICTIONARY: Dict[int, int] = dict(
    {
        4: 1,
        18: 1,
        27: 1,
        28: 1,
        29: 1,
        34: 1,
        132: 1,
        155: 1,
        156: 1,
        157: 1,
        179: 1,
        180: 1,
        3: 2,
        1: 2,
        129: 2,
        2: 3,
        17: 3,
        130: 3,
        12: 4,
        13: 4,
        140: 4,
        26: 4,
        30: 4,
        31: 4,
        42: 4,
        45: 4,
        158: 4,
        35: 5,
        36: 5,
        163: 5,
        164: 5,
    }
)

# Dictionary mapping regions to variable block type
BIOME_BLOCK_MAP_DICTIONARY: Dict[biome_regions, block_codes] = dict(
    {
        biome_regions.FOREST: block_codes.DARK_OAK_WOOD,
        biome_regions.PLAINS: block_codes.DARK_OAK_WOOD,
        biome_regions.DESERT: block_codes.SANDSTONE,
        biome_regions.COLD: block_codes.EMERALD_ORE,
        biome_regions.SAVANNA: block_codes.BROWN_TERRACOTTA,
    }
)
ENCOURAGE_PENALTY: float = 0.5
MAX_SNAP_TO_GRID_PENALTY: float = 2
NEAR_OBSTACLE_PENALTY: float = 1
THRESHOLD_GAIN_FOR_REENTRY_TO_FRONTIER: int = 2
LAMP_POST_SPACING: int = 10
ABORT_SEARCH_FOR_SITE_AFTER_ROUTE_NOT_FOUND_LIMIT: int = 4
MAX_HEIGHT_DROP: int = 1
MAX_DEPTH: int = 500
AREA_EXPANDED_MARGIN: int = 5


FOLIAGE_CLEARING_HEIGHT: int = 20
MINECRAFT_USERNAME: str = "EnviableMonkey"
