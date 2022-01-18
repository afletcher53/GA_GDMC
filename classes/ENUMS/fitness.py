"""Enums for the fitness types used in the genetic algorithm 
    """


from classes.ENUMS.block_codes import ExtendedEnum


class fitness_functions(ExtendedEnum):
    WATER_DISTANCE = "water_distance"
    FLATNESS = "flatness"
    HOUSE_DISTANCE = "house_distance"
    WATER_BOOLEAN = "water_boolean"
