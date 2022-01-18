import json
from typing import List, Tuple, Dict
from random import choice, seed
from classes.Building import building
from classes.ENUMS.building_types import building_types
from classes.ENUMS.building_styles import building_styles
from classes.ENUMS.building_names import building_names
from constants import MAX_BUILDING_RADIUS

class buildings(object):
    """List of all Buildings"""
    buildings = List[building]

    def __init__(self):
        data = json.load(open('data/building_maps/buildings.json'))
        self.buildings = list(map(building.from_json, data["buildings"]))

    @classmethod 
    def get_smallest_building_types(cls, building_style: building_styles = building_styles.UNKNOWN) -> Dict[building_types, int] :
        all_builds = cls()

        small_building_types: Dict[building_types, int] = {}

        max_dimension = MAX_BUILDING_RADIUS * 2

        if  building_style == building_styles.UNKNOWN :
            builds = all_builds.getBySize(max_dimension, max_dimension)
        else :
            builds = all_builds.getByStyleAndSize(building_style, max_dimension, max_dimension)

        for build in builds: #type: building
            if build.type not in small_building_types or build.longest_side() < small_building_types[build.type]:
                small_building_types[build.type] = build.longest_side()

        return small_building_types

    def getByName(self, building_name: building_names) -> building :
        """Return a building by name.  eg building_names.APPLE_STORE"""
        builds = list(filter(lambda b: b.id == building_name.value , self.buildings))
        if not builds :
            return None

        return builds[0]

    def getByType(self, building_type: building_types) -> List[building] :
        """Return all buildings of a certain type.  eg building_types.HOUSE"""
        return list(filter(lambda b: b.type == building_type , self.buildings))

    def getRandomByType(self, building_type: building_types) -> building :
        """Return one random building of a certain type.  eg building_types.HOUSE"""
        builds = self.getByType(building_type)

        if not builds :
            return None

        return choice(builds)

    def getBySize(self, maxWidth: int, maxDepth: int) -> List[building] :
        """Return all buildings of a certain size.  """
        return list(filter(lambda b: b.width <= maxWidth and b.depth <= maxDepth, self.buildings))

    def getRandomBySize(self, maxWidth: int, maxDepth: int) -> building :
        """Return one random building of a certain size."""
        builds = self.getBySize(maxWidth, maxDepth)

        if not builds :
            return None

        return choice(builds)

    def getByTypeAndSize(self, building_type: building_types, maxWidth: int, maxDepth: int) -> List[building] :
        """Return all buildings of a certain type.  eg building_types.HOUSE"""
        return list(filter(lambda b: b.type == building_type and b.width <= maxWidth and b.depth <= maxDepth, self.buildings))

    def getByStyleAndSize(self, building_style: building_styles, maxWidth: int, maxDepth: int) -> List[building] :
        """Return all buildings of a certain type.  eg building_types.HOUSE"""
        return list(filter(lambda b: b.style == building_style and b.width <= maxWidth and b.depth <= maxDepth, self.buildings))

    def getByTypeStyleAndSize(self, building_type: building_types, building_style: building_styles, maxWidth: int, maxDepth: int, get_other_style_if_none : bool = False) -> List[building] :
        """Return all buildings of a certain type, size and style.  eg building_types.HOUSE building_types.LOG <26x26"""

        if building_style != building_styles.UNKNOWN :
            buildings:List[building] =  list(filter(lambda b:   b.type == building_type 
                                                            and b.style == building_style 
                                                            and b.width <= maxWidth 
                                                            and b.depth <= maxDepth
                                                            , self.buildings))

            if not get_other_style_if_none or buildings :
                return buildings
        
        return self.getByTypeAndSize(building_type, maxWidth, maxDepth)

    def getRandomByTypeAndSize(self, building_type: building_types, maxWidth: int, maxDepth: int) -> building :
        """Return one random building of a certain type and size.  eg building_types.HOUSE less than 20x20"""
        builds = self.getByTypeAndSize(building_type, maxWidth, maxDepth)

        if not builds :
            return None

        return choice(builds)

    def getBiggestByTypeAndSize(self, building_type: building_types, maxWidth: int, maxDepth: int) -> building :
        """Return the largest building of a certain type within a specified size.  eg building_types.HOUSE less than 20x20"""
        builds = self.getByTypeAndSize( building_type, maxWidth, maxDepth)

        if not builds :
            return None

        builds.sort(key=lambda x:x.area())

        return builds[-1]

    def getBiggestByTypeStyleAndSize(self, building_type: building_types, building_style: building_styles, maxWidth: int, maxDepth: int, get_other_style_if_none : bool = False) -> building :
        """Return the largest building of a certain type within a specified size.  eg building_types.HOUSE less than 20x20"""
        builds = self.getByTypeStyleAndSize(building_type, building_style, maxWidth, maxDepth, get_other_style_if_none)

        if not builds :
            return None

        builds.sort(key=lambda x:x.area())

        return builds[-1]

    def getRandomByTypeStyleAndSize(self, building_type: building_types, building_style: building_styles, maxWidth: int, maxDepth: int, get_other_style_if_none : bool = False) -> building :
        """Return the largest building of a certain type within a specified size.  eg building_types.HOUSE less than 20x20"""
        builds = self.getByTypeStyleAndSize(building_type, building_style, maxWidth, maxDepth, get_other_style_if_none)

        if not builds :
            return None

        return choice(builds)

    def getBiggestBySize(self, maxWidth: int, maxDepth: int) -> building :
        """Return the largest building of a certain type within a specified size.  eg building_types.HOUSE less than 20x20"""
        builds = self.getBySize( maxWidth, maxDepth)

        if not builds :
            return None

        builds.sort(key=lambda x:x.area())

        return builds[-1]