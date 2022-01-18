from enum import Enum

class building_types(Enum):
    """Master list of all building types"""
    UNKNOWN = -1

    HOUSE = 0
    RESTAURANT = 1
    FACTORY = 2
    SHOP = 3
    FLATS = 4
    TOWN_HALL = 5
