"""Class containing all building locations and operations
    on the building sites
 """
from typing import Tuple
from classes.ENUMS.biome_ids import biome_regions
from classes.Location_Genome import LocationGenome
from classes.misc_functions import get_build_coord
from classes.Builder import Builder
from classes.ENUMS.block_codes import block_codes
from classes.ENUMS.building_styles import building_styles

import vendor.gdmc_http_client.interfaceUtils

USE_BATCH_PAINTING = True


class BuildingLocations:
    """Class containing all proposed building locations"""

    def __init__(self, world_slice) -> None:
        self.total_fitness = 0
        self.water_fitness = 0
        self.building_fitness = 0
        self.flatness_fitness = 0
        self.locations = []
        self.world_slice = world_slice
        self.biome_region: biome_regions
        self.variable_blocktype: block_codes

    def add_building(self, location: LocationGenome):
        """Adds a building location to the class

        Args:
            location (LocationGenome): Building Locations
        """
        vector_coordinate = location.get_vector_coord()
        radius = location.building_radius

        build_locations = get_build_coord(
            location=vector_coordinate,
            building_radius=radius,
        )
        location.build_locations = build_locations
        location.build_coordinates = (
            vector_coordinate[0] - radius,
            vector_coordinate[1] - radius,
            vector_coordinate[0] + radius,
            vector_coordinate[1] + radius,
        )
        self.locations.append(location)

    def get_biome(self, location: LocationGenome, y_index: int = 100) -> int:
        if location not in self.locations:
            raise ValueError(
                "Attempting to access biome information for a location that doesnt exist"
            )

        x_value = location.get_vector_coord()[0]
        z_value = location.get_vector_coord()[1]
        y_value = y_index

        return self.world_slice.getBiomeAt((x_value, y_value, z_value))

    def _evaluate(self):
        """Evaluates all building locations"""
        for member in self.locations:
            self.total_fitness += member.fitness
            self.water_fitness += member.water_distance_fitness
            self.building_fitness += member.building_distance_fitness
            self.flatness_fitness += member.flatness_fitness

    def paint_buildings(self):
        """Paints building platforms onto the minecraft world"""
        location_list = [(o.x, o.z) for o in self.locations]
        radii = [o.building_radius for o in self.locations]
        print(f"\nLocations: {location_list}")
        print(f"Radii: {radii}")
        vendor.gdmc_http_client.interfaceUtils.sendBlocks()

        print("\n\n****************")
        print("Starting PHASE 2")
        print("****************")

        Builder.analyze_and_create(
            location_list, radii, self.variable_blocktype, building_styles.CUSTOM
        )
