from sys import maxsize 
from vendor.gdmc_http_client.worldLoader import WorldSlice
from typing import List, Tuple
from constants import MAX_DETOUR, DEBUG_DRAW_WORKINGS, BLOCK_BATCH_SIZE #, WATER_CODES
from classes.ENUMS.block_codes import block_codes
from vendor.gdmc_http_client.interfaceUtils import placeBlockBatched, sendBlocks

class bool_map():
    class tile_info():
        def __init__(self):
            self.avoid = False
            self.avoid_water = False
            self.is_near_obstacle = False
            self.has_road = False
            self.already_goes_to = {}

    def __init__(self, areas: Tuple[int, int, int, int], avoid_rects: List[Tuple[int,int,int,int]], margin: int, world_slice: WorldSlice):
        """description of class"""
        self.minX = areas[0]
        self.minZ = areas[1]
        self.width = areas[2]
        self.depth = areas[3]

        self.matrix = [ [ self.tile_info() for j in range(self.depth) ] for i in range(self.width) ]

        self.route_list = []

        for rect in avoid_rects:  #type: Tuple[int,int,int,int]
            for i in range(rect[0] - self.minX, rect[2] - self.minX + 1):
                for j in range(rect[1] - self.minZ, rect[3] - self.minZ + 1):
                    if 0 <= i < self.width and 0 <= j < self.depth :
                        self.matrix[i][j].avoid = True

        #TODO: only loop through intersection of matrix and world_slice
        sea_floor = world_slice.heightmaps['OCEAN_FLOOR']
        surface = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES']

        for i in range(world_slice.rect[2]): #type: int
            for j in range(world_slice.rect[3]): #type: int
                if sea_floor[i][j] < surface[i][j] :
                    j_m = world_slice.rect[1] + j - self.minZ
                    i_m = world_slice.rect[0] + i - self.minX
                    if 0 <= i_m < self.width and 0 <= j_m < self.depth :
                        self.matrix[i_m][j_m].avoid_water = True
                        self.matrix[i_m][j_m].avoid = True

        changes = []
        for i in range(margin, self.width - margin): #type: int
            for j in range(margin, self.depth - margin): #type: int
                if not self.matrix[i][j].avoid :
                    for k in range(1, margin + 1):
                        if self.matrix[i-k][j].avoid :
                            changes.append((i,j))
                            break
                        elif self.matrix[i][j-k].avoid :
                            changes.append((i,j))
                            break
                        if self.matrix[i+k][j].avoid :
                            changes.append((i,j))
                            break
                        elif self.matrix[i][j+k].avoid :
                            changes.append((i,j))
                            break
        for change in changes:
            self.matrix[change[0]][change[1]].is_near_obstacle = True

    @classmethod
    def create(  cls, centers: List[Tuple[int, int]], radii: List[int], margin_width: int
                    ) -> Tuple[ List[Tuple[int,int,int,int]], 'bool_map', WorldSlice] :

        areas_min_x, areas_min_z = maxsize, maxsize
        areas_max_x, areas_max_z = -maxsize, -maxsize

        site_areas = []
        for location_index in range(len(centers)): #type: int
            radius = radii[location_index]
            center = centers[location_index]

            site_area = (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius)

            site_areas.append(site_area)

            areas_min_x, areas_min_z = min(areas_min_x, site_area[0]), min(areas_min_z, site_area[1])
            areas_max_x, areas_max_z = max(areas_max_x, site_area[2]), max(areas_max_z, site_area[3])

        map_area = (   areas_min_x - MAX_DETOUR, areas_min_z - MAX_DETOUR
                     , areas_max_x - areas_min_x + 2 * MAX_DETOUR
                     , areas_max_z - areas_min_z + 2 * MAX_DETOUR)

        world_slice = WorldSlice(map_area)
        world_map = bool_map(map_area, site_areas, margin_width, world_slice)

        if DEBUG_DRAW_WORKINGS :
            for rect in site_areas: #type: Tuple[int,int,int,int]
                for rect_x in range(rect[0], rect[2]): #type: int
                    for rect_z in range(rect[1], rect[3]): #type: int
                        rect_y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][rect_x-world_slice.rect[0]][rect_z-world_slice.rect[1]]
                        placeBlockBatched(rect_x, rect_y - 1, rect_z, block_codes.WHITE_TERRACOTTA.value, BLOCK_BATCH_SIZE)
            sendBlocks()

        return map_area, world_map, world_slice

    def get_avoid_value(self, x: int, z: int) -> bool:
        return self.matrix[x - self.minX][z - self.minZ].avoid

    def get_avoid_water_value(self, x: int, z: int) -> bool:
        return self.matrix[x - self.minX][z - self.minZ].avoid_water

    def get_avoid_building_value(self, x: int, z: int) -> bool:
        return self.matrix[x - self.minX][z - self.minZ].avoid and not self.matrix[x - self.minX][z - self.minZ].avoid_water

    def get_is_near_obstacle(self, x: int, z: int) -> bool:
        return self.matrix[x - self.minX][z - self.minZ].is_near_obstacle

    def get_has_road_value(self, x: int, z: int) -> bool:
        return self.matrix[x - self.minX][z - self.minZ].has_road

    def set_road(self, coords: List[Tuple[int, int, int]], goes_to: Tuple[int, int]):
        route_index = len(self.route_list)
        self.route_list.append(coords)

        for coord in coords:
            current_tile = self.matrix[coord[0] - self.minX][coord[2] - self.minZ]
            current_tile.has_road = True
            current_tile.already_goes_to[goes_to] = route_index

    def check_already_goes_to(self, x: int, z: int, goes_to: Tuple[int, int]) -> Tuple[bool, bool, List[Tuple[int, int, int]]] :
        current_tile = self.matrix[x - self.minX][z - self.minZ]

        if current_tile.has_road and goes_to in current_tile.already_goes_to :
            has_road = True
            route = self.route_list[current_tile.already_goes_to[goes_to]]

            current_address = (x, z)
            for index in range(len(route)) : #type: int
                if x == route[index][0] and z == route[index][2] :
                    return has_road, True, route[0:index+1]
        else :
            has_road = False
        return has_road, False, None
