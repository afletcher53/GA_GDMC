"""Class containing location genome

    Returns:
        LocationGenome: Genome with building location
        information
"""

import random
from typing import Tuple
from classes.Types import GridLocation
from constants import MAX_BUILDING_RADIUS


class LocationGenome:
    """Class for location genome"""

    def __init__(
        self,
        graph_space: tuple,  # graph space where genes can occur
        grid_location: GridLocation = None,  # Previous x,z coord
        init_random=False,  # random genome
        building_radius: int = 1,
    ):
        self.graph_space: GridLocation = graph_space
        self.fitness: int = 0
        self.water_distance_fitness: int = 0
        self.build_distance_fitness: int = 0
        self.flatness_fitness: int = 0
        self.building_radius: int = building_radius
        self.adjusted_fitness: int = 0  # adjusted fitness
        self.fitness_probability: int = 0  # Chance of selection
        self.build_locations: list = []
        self.build_coordinates: Tuple[int, int, int, int] = ()
        if init_random:
            self.x, self.z = self._get_random_possible_coordinate()

        elif not init_random:
            self.x = grid_location[0]
            self.z = grid_location[1]

    def get_vector_coord(self) -> GridLocation:
        """Return vector cordinates of the genome

        Returns:
            GridLocation: the x, z location of the genome
        """
        return (self.x, self.z)

    def _get_random_possible_coordinate(self) -> tuple:
        random_x_value = random.choice(
            range((MAX_BUILDING_RADIUS), (self.graph_space[0] - MAX_BUILDING_RADIUS))
        )
        random_z_value = random.choice(
            range((MAX_BUILDING_RADIUS), (self.graph_space[1] - MAX_BUILDING_RADIUS))
        )
        return (random_x_value, random_z_value)
