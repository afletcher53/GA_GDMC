from classes.ENUMS.orientations import orientations
from classes.Building import building
from classes.Buildings import buildings
from classes.Bool_map import bool_map
from classes.ENUMS.building_types import building_types
from classes.ENUMS.building_styles import building_styles
from classes.ENUMS.building_names import building_names
from constants import VISITS_PER_BUILDING_TYPE, AREA_EXPANDED_MARGIN, MCTS_TIME_LIMIT_SECONDS, USE_BFS_WITH_LOCATION_COUNT
from typing import Tuple, List, Dict
from collections import Counter
from sys import maxsize 
import time
import math
import random


class building_site(object):
    """Specifics of a building instance"""
    x_center = 0
    z_center = 0
    y_min = 0

    coords = (0, 0, 0, 0)
    area_expanded = (0, 0, 0, 0)

    x_zero = 0
    z_zero = 0
    x_factor = 1
    z_factor = 1

    building_name = building_names.APPLE_STORE
    building_type = building_types.UNKNOWN
    orientation = orientations.SOUTH

    width = 0
    depth = 0
    final_x_length = 0
    final_z_length = 0
    raw_x_length = 0
    raw_z_length = 0

    area = 0

    door_location = 0
    sign_location = 0

    repeaterXs = []
    repeaterZs = []

    building_map_x_index = 0
    building_map_z_index = 2

    def __init__(
        self,
        building: building,
        x_center: int,
        z_center: int,
        orientation: orientations,
        required_width: int = 0,
        required_depth: int = 0,
    ):
        self.x_center = x_center
        self.z_center = z_center
        self.building_type = building.type
        self.building_name = building_names(building.id)
        self.orientation = orientation

        self.width = building.width
        self.depth = building.depth
        self.area = self.width * self.depth

        if orientation in (orientations.NORTH, orientations.SOUTH):
            self.raw_x_length = building.width
            self.raw_z_length = building.depth
            self.repeaterXs, self.repeaterZs = building.getRepeaters(
                required_width, required_depth
            )
            building_map_x_index = 0
            building_map_z_index = 2
        else:
            self.raw_x_length = building.depth
            self.raw_z_length = building.width
            self.repeaterZs, self.repeaterXs = building.getRepeaters(
                required_width, required_depth
            )
            self.building_map_x_index = 2
            self.building_map_z_index = 0

        self.final_x_length = self.raw_x_length + len(self.repeaterXs) - 1
        self.final_z_length = self.raw_z_length + len(self.repeaterZs) - 1
        self.area = self.final_x_length * self.final_z_length

        self.x_factor, self.z_factor = ((-1, 1), (-1, -1), (1, -1), (1, 1))[
            orientation.value
        ]  # w,n,e,s

        self.x_zero = x_center + (-1 * self.x_factor * int(self.final_x_length / 2))
        self.z_zero = z_center + (-1 * self.z_factor * int(self.final_z_length / 2))

        x_end = self.x_zero + (self.x_factor * self.final_x_length)
        z_end = self.z_zero + (self.z_factor * self.final_z_length)

        self.coords = (
            min(self.x_zero, x_end),
            min(self.z_zero, z_end),
            max(self.x_zero, x_end),
            max(self.z_zero, z_end),
        )
        self.area_expanded = (
            self.coords[0] - AREA_EXPANDED_MARGIN,
            self.coords[1] - AREA_EXPANDED_MARGIN,
            self.final_x_length + 2 * AREA_EXPANDED_MARGIN,
            self.final_z_length + 2 * AREA_EXPANDED_MARGIN,
        )

        if orientation in (orientations.NORTH, orientations.SOUTH):
            self.door_location = (
                self.x_center,
                self.side_wall_coordinate(orientation) + self.z_factor,
            )
            self.sign_location = (
                self.door_location[0] + self.x_factor * 4,
                self.door_location[1],
            )
        else:
            self.door_location = (
                self.side_wall_coordinate(orientation) + self.x_factor,
                self.z_center,
            )
            self.sign_location = (
                self.door_location[0],
                self.door_location[1] + self.z_factor * 4,
            )

        return

    def set_altitude(self, floor: int):
        self.y_min = floor

    def side_wall_coordinate(self, side: orientations) -> int:
        return self.coords[side.value]  # w,n,e,s

    def map_coords_to_site_coords(self, x: int, y: int, z: int) -> Tuple[int, int, int]:
        # coords undergo translation and rotation
        return (
            self.x_zero + self.x_factor * x,
            self.y_min + y,
            self.z_zero + self.z_factor * z,
        )

    def get_description(self) -> str:
        return f"{self.building_name.name} built at [{self.coords[0]},{self.coords[1]}] size: [{self.final_x_length},{self.final_z_length}] at height {self.y_min}"

    def calc_adjacent_location(
        self,
        buildOnWhichSide: orientations,
        gapBetweenBuildings: int,
        orientation: orientations,
        building: building,
        requiredWidth: int = -1,
        requiredDepth: int = -1,
    ) -> Tuple[int, int]:

        factorFrom = (-1, -1, 1, 1)[buildOnWhichSide.value]  # w,n,e,s
        factorToReverse = (1, 1, -1, -1)[orientation.value]  # w,n,e,s

        if orientation in (orientations.NORTH, orientations.SOUTH):
            half_x = int(building.width / 2)  # TODO - Should be final width
            half_z = int(building.depth / 2)
        else:
            half_x = int(building.depth / 2)
            half_z = int(building.width / 2)

        if buildOnWhichSide in (orientations.NORTH, orientations.SOUTH):
            x_center = self.side_wall_coordinate(orientation) + half_x * factorToReverse
            z_center = (
                self.side_wall_coordinate(buildOnWhichSide)
                + (gapBetweenBuildings + 1 + half_z) * factorFrom
            )
        else:
            x_center = (
                self.side_wall_coordinate(buildOnWhichSide)
                + (gapBetweenBuildings + 1 + half_x) * factorFrom
            )
            z_center = self.side_wall_coordinate(orientation) + half_z * factorToReverse

        return x_center, z_center

    @classmethod
    def move_location(
        self, location: Tuple[int, int], direction: orientations, distance: int
    ) -> Tuple[int, int]:
        factor = (-1, -1, 1, 1)[direction.value]  # w,n,e,s

        if direction in (orientations.NORTH, orientations.SOUTH):
            return location[0], location[1] + factor * distance
        else:
            return location[0] + factor * distance, location[1]

    @classmethod
    def get_locations(
        self,
        centers: List[Tuple[int, int]],
        radii: List[int],
        world_map: bool_map,
        drive_length: int,
    ) -> Tuple[
        List[orientations],  # building_orientations
        List[Tuple[int, int]],  # door_locations
        List[Tuple[Tuple[int, int], Tuple[int, int]]],  # roads
    ]:

        n_sites = len(centers)

        average_location = (0, 0)
        for location in centers:
            average_location = (
                average_location[0] + location[0],
                average_location[1] + location[1],
            )
        average_location = int(average_location[0] / n_sites), int(
            average_location[1] / n_sites
        )

        # Make sure building is facing the center of the village, if possible.
        direction_preferences = []
        for location in centers: #type: Tuple[int, int]
            if average_location[0] - location[0] > 0 :
                e_w_preference = (orientations.EAST, orientations.WEST)
            else:
                e_w_preference = (orientations.WEST, orientations.EAST)

            if average_location[1] - location[1] > 0 :
                n_s_preference = (orientations.SOUTH, orientations.NORTH)
            else:
                n_s_preference = (orientations.NORTH, orientations.SOUTH)

            if abs(average_location[0] - location[0]) < abs(average_location[1] - location[1]):
                direction_preferences.append((e_w_preference[0], n_s_preference[0], e_w_preference[1], n_s_preference[1]))
            else :
                direction_preferences.append((n_s_preference[0], e_w_preference[0], n_s_preference[1], e_w_preference[1]))


        building_orientations = []
        door_locations = []

        for location_index in range(n_sites): #type: int
            chosen = False
            for direction_preference in direction_preferences[location_index]:
                door_locations_candidate = building_site.move_location(
                    centers[location_index],
                    direction_preference,
                    radii[location_index] + drive_length,
                )

                if world_map.get_avoid_value(
                    door_locations_candidate[0], door_locations_candidate[1]
                ):
                    if world_map.get_avoid_water_value(
                        door_locations_candidate[0], door_locations_candidate[1]
                    ):
                        print(
                            f"Site {centers[location_index]}: potential door at {door_locations_candidate} blocked by water."
                        )
                    else:
                        print(
                            f"Site {centers[location_index]}: potential door at {door_locations_candidate} blocked by other building."
                        )
                else:
                    building_orientations.append(direction_preference)
                    door_locations.append(door_locations_candidate)
                    chosen = True
                    break
            if not chosen:
                raise Exception(
                    f"Building {centers[location_index]} has no possible door locations!"
                )

        roads = []

        for site1 in range(n_sites) :  #type: int
            for site2 in range(n_sites) :  #type: int
                if site1 != site2 :
                    if      (door_locations[site1], door_locations[site2]) not in roads \
                        and (door_locations[site2], door_locations[site1]) not in roads:
                        roads.append((door_locations[site1], door_locations[site2]))

        return building_orientations, door_locations, roads

    @classmethod
    def calc_building_types(self
                            , distances: List[List[int]]
                            , building_radii: List[int]
                            , number_of_families_in_a_flat: int
                            , building_style: building_styles = building_styles.UNKNOWN
                            ) -> List[Tuple[int, building_types]]:

        start_bfs = time.time()

        site_count = len(distances)
        locations_available = list(range(site_count))

        #*********************************************************************************************************
        #Not all buildings are always connected.  Find which is the most connected network

        #use only fully connected.  Any connected to network will be fully connected to all.
        site_roads_count = [[i] for i in range(site_count)] #Assign the site itself to its own list
        for site1 in locations_available: #type: int
            for site2 in locations_available: #type: int
                if site1 != site2 and distances[site1][site2]:
                    if site2 not in site_roads_count[site1]:
                        site_roads_count[site1].append(site2)
                    if site1 not in site_roads_count[site2]:
                        site_roads_count[site2].append(site1)
        
        #assign the most connected site list to locations_available
        locations_available = []
        for site_road_count in site_roads_count: #type: int
            if len(site_road_count) > len(locations_available) :
                locations_available = site_road_count

        available_site_count = len(locations_available)
        

        #*********************************************************************************************************
        #Calculate which buildings will fit in which sites.  For example, Town Hall might only fit in sites 1, and 6
        #Decide which building types will be placed in village and add to variable building_types_in_village.  This is decided by 
        #number of sites, and if there is physical space for building of that size.
        #
        #example_solution_sites_available tracks if there is space left - when a building type is requested, it is assigned 
        #to the smallest site where it will fit (in example_solution_sites_available).  If there are no available
        #spaces left where it will physically fit, that building type will not be added.  This assures that there is
        #at least one working combination of buildings in sites for BFS to find below

        building_types_in_village: List[building_types] = []

        smallest_building_size_by_type: Dict[building_types, int] = buildings.get_smallest_building_types(building_style)

        building_types_fit_in_sites: List[List[building_types]] = [[] for i in range(site_count)]

        for site_index in locations_available: #type: int
            site_diameter: int = building_radii[site_index] * 2

            for building_type, smallest_size in smallest_building_size_by_type.items(): #type: building_types, int
                if site_diameter >= smallest_size :
                    building_types_fit_in_sites[site_index].append(building_type)
                
        example_solution_sites_available: List[bool] = [i in locations_available for i in range(site_count)]

        def add_type(building_type: building_types) -> bool:
            winning_site_index: int = -1
            winning_site_radius: int = maxsize

            for index in range(site_count): #type: int
                if (        example_solution_sites_available[index] 
                        and building_type in building_types_fit_in_sites[index] 
                        and winning_site_radius >  building_radii[index]) :
                    winning_site_index = index
                    winning_site_radius = building_radii[index]

            if winning_site_index == -1:
                print(f"{building_type} can not be built due to no suitable sites.")
                return False

            example_solution_sites_available[winning_site_index] = False
            building_types_in_village.append(building_type)
            return True

        if available_site_count < 3 :
            raise TimerError(f"Not enough building sites! Some sites may have been removed due to no roads.")

        non_houses = (building_types.SHOP, building_types.FACTORY, building_types.FLATS, building_types.RESTAURANT)

        for index in range(available_site_count // 2): #type: int
            add_type(non_houses[index % len(non_houses)])

        if available_site_count > 8 :
            add_type(building_types.TOWN_HALL)

        while available_site_count > len(building_types_in_village): 
            if not add_type(building_types.HOUSE) :
                break

        can_build_type =  [[ build_type in building_types_fit_in_sites[location_l] \
                                for build_type in building_types if build_type != building_types.UNKNOWN ] \
                                for location_l in locations_available ]

        #Check the sites to make sure there is at least one building that will fit.
        sites_with_no_possible_buildings = list(filter(lambda site: site == True, example_solution_sites_available))
        for site in sites_with_no_possible_buildings:
            locations_available.remove(site)

        available_site_count = len(locations_available)

        print(f"Building types in village: " + str(Counter(building_types_in_village)))
        print(f"Building sites where no buildings fit: " + str(sites_with_no_possible_buildings) + "\n")

        building_types_in_village_not_houses = list(filter(lambda x: x != building_types.HOUSE, building_types_in_village))
        total_no_of_houses = available_site_count - len(building_types_in_village_not_houses)

        chosen_house_locations = []

        class attempt_details():
            def __init__(self, parent: 'attempt_details', location_index: int, building: building_types, is_top_node: bool = False):
                self.parent: 'attempt_details' = parent
                self.location_index: int = location_index
                self.building: building_types = building
                self.is_top_node: bool = is_top_node

            @classmethod
            def get_top_node(cls):
                return cls(None, -1, building_types.UNKNOWN, True)

        def bfs(  attempt: attempt_details
                                , house_count: int
                                , locations_list : List[int]) -> Tuple[int, List[Tuple[int, building_types]]]:
            print("\nStarting search for best locations")

            winning_score, winning_building_locations = recursive_bfs_step1(attempt, house_count, locations_list)

            mins, sec = divmod(time.time() - start_bfs, 60)
            print(f"\n\nTotal Time elapsed BFS: {mins:.0f}m {sec:.0f}s")
            print(f"BFS Total distance: {winning_score}")

            for winning_building_location in winning_building_locations: #type: Tuple[int, building_types]
                print(f"Building location: {winning_building_location[0]} -> {winning_building_location[1].name}")

            return winning_score, winning_building_locations    
        ################################################################################################################
        #find places for houses in step 1.  This is done first so that the following is not considered separately:
        #{HouseA in Location1, HouseB in Location2} and {HouseB in Location1, HouseA in Location2}
        #Step1 equates HouseA and HouseB as the same and so saves processing time
        #If only bfs_step2 was used, A and B would be considered as different entities
        def recursive_bfs_step1(  attempt: attempt_details
                                , house_count: int
                                , locations_list : List[int]) -> Tuple[int, List[Tuple[int, building_types]]]:
            if house_count == 0 :
                return recursive_bfs_step2(attempt, building_types_in_village_not_houses, locations_list)

            winning_score = maxsize
            winning_building_locations = []
            available_locations_count = len(locations_list) - house_count + 1

            for location_index in range(available_locations_count) : #type: int

                if house_count == total_no_of_houses :
                    mins, sec = divmod(time.time() - start_bfs, 60)
                    if winning_score == maxsize:
                        print(f"Find optimum locations {100*location_index/available_locations_count:.0f}% complete  {mins:.0f}m {sec:.0f}s No winning score found yet")
                    else:
                        print(f"Find optimum locations {100*location_index/available_locations_count:.0f}% complete  {mins:.0f}m {sec:.0f}s Winning score: {winning_score}")


                if can_build_type[location_index][building_types.HOUSE.value] :
                    location = locations_list.pop(location_index)

                    candidate_score, candidate_building_locations = recursive_bfs_step1(
                          attempt_details(attempt, location, building_types.HOUSE), house_count - 1, locations_list)

                    locations_list.insert(location_index, location)

                    if candidate_score < winning_score :
                        winning_score = candidate_score
                        winning_building_locations = candidate_building_locations

            return winning_score, winning_building_locations


        ################################################################################################################
        def recursive_bfs_step2(     attempt: attempt_details
                                   , buildings_list : List[building_types]
                                   , locations_list : List[int]) -> Tuple[int, List[Tuple[int, building_types]]]:

            if not locations_list :
        
                function_building_locations = []
                house_location_adresses = []
                building_locations = []
                flat_addresses = []

                while not attempt.is_top_node:
                    building_locations.append(
                        (attempt.location_index, attempt.building)
                    )
                    if attempt.building == building_types.HOUSE:
                        house_location_adresses.append(attempt.location_index)
                    elif attempt.building == building_types.FLATS:
                        flat_addresses.append(attempt.location_index)
                    else:
                        function_building_locations.append(
                            (attempt.location_index, attempt.building)
                        )
                    attempt = attempt.parent

                total_distance = 0
                for candidate_address, candidate_building in function_building_locations: #type: int, building_types
                    visit_count = VISITS_PER_BUILDING_TYPE[candidate_building.value]
                    
                    for house_address in house_location_adresses: #type: int
                        total_distance += visit_count * distances[candidate_address][house_address]
                    for flat_address in flat_addresses: #type: int
                        total_distance += visit_count * number_of_families_in_a_flat * distances[candidate_address][flat_address]

                return total_distance, building_locations

            winning_score = maxsize
            winning_building_locations = []

            location = locations_list.pop(0)

            can_build_type_at_location = can_build_type[locations_available.index(location)]

            for i in range(len(buildings_list)): #type: int

                if locations_list == [1,2,3] :
                    print("Here!")

                if can_build_type_at_location[buildings_list[i].value] :
                    building = buildings_list.pop(i)

                    candidate_score, candidate_building_locations = recursive_bfs_step2(
                          attempt_details(attempt, location, building), buildings_list, locations_list)

                    buildings_list.insert(i, building)

                    if candidate_score < winning_score :
                        winning_score = candidate_score
                        winning_building_locations = candidate_building_locations

            locations_list.insert(0, location)

            return winning_score, winning_building_locations

        class MCTS_details():
            def __init__(self
                         , parent: 'attempt_details'
                         , location_index: int
                         , remaining_location_indeces: List[int]
                         , build: building_types
                         , remaining_builds: List[building_types]
                         , is_top_node: bool = False):
                self.parent: 'MCTS_details' = parent
                self.total: int = 0
                self.visits: int = 0
                self.is_top_node: bool = is_top_node
                self.depth: int = 0 if is_top_node else parent.depth + 1


                self.location_index: int = location_index
                self.remaining_location_indeces: List[int] = remaining_location_indeces
                self.build: building_types =  build
                self.remaining_builds: List[building_types] = remaining_builds

                self.is_leaf: bool = True
                self.children: List['MCTS_details'] = []

            @classmethod
            def get_top_node(cls, all_location_indeces: List[int], building_types_in_village: List[building_types]):
                return cls(None, -1, all_location_indeces, building_types.UNKNOWN, building_types_in_village, True)

            def ucb1_score(self, variable_c: float, max_score: int) -> float :
                if self.visits == 0 :
                    return float('inf')
                elif self.is_top_node:
                    return 0
                else:
                    #max_score - average score is used so that lower scores are better.
                    #variable_c = sqrt(2) * the score range.  This will ecourage unlucky potentials, but also allow convergence.
                    return max(0, max_score - (self.total / self.visits)) + variable_c * math.sqrt(math.log(self.parent.visits) / self.visits)

            def lowest_scoring_child(self, variable_c: float, max_score: int) -> 'MCTS_details' :
                if len(self.children) == 0:
                    return None

                winning_score = self.children[0].ucb1_score(variable_c, max_score)
                winning_index = 0

                for index in range(1, len(self.children)): #type: int
                    s = self.children[index].ucb1_score(variable_c, max_score)
                    if s == float('inf') :
                        return self.children[index]
                    elif s > winning_score :
                        winning_score = s
                        winning_index = index

                return self.children[winning_index]

            def create_leaves(self) -> List['MCTS_details'] :
                if len(self.remaining_location_indeces) == 0 :
                    return False
                
                next_remaining_builds = []
                next_remaining_build = []
                for j in range(len(self.remaining_builds)) :
                    next = self.remaining_builds[:]
                    next_remaining_build.append(next.pop(j))
                    next_remaining_builds.append(next)

                for i in range(len(self.remaining_location_indeces)) :
                    next_remaining_locations = self.remaining_location_indeces[:]
                    next_location = next_remaining_locations.pop(i)

                    for j in range(len(self.remaining_builds)) :
                        if can_build_type[next_location][next_remaining_build[j].value] :
                            self.children.append(MCTS_details(  self
                                                              , next_location
                                                              , next_remaining_locations
                                                              , next_remaining_build[j]
                                                              , next_remaining_builds[j]
                                                              , False)
                                                 )

                self.is_leaf = False

                return True

            def rollout(self, max_score: int) -> Tuple[int, List[Tuple[int, building_types]]]:
                attempt = self

                function_building_locations = []
                house_location_adresses = []
                building_locations = []
                flat_addresses = []
                
                def add_node(loc_ind: int, add_build: building_types) :
                    building_locations.append( (loc_ind, add_build) )
                    if add_build == building_types.HOUSE:
                        house_location_adresses.append(loc_ind)
                    elif add_build == building_types.FLATS:
                        flat_addresses.append(loc_ind)
                    else:
                        function_building_locations.append( (loc_ind, add_build) )

                while not attempt.is_top_node:
                    add_node(attempt.location_index, attempt.build)
                    attempt = attempt.parent

                random.shuffle(self.remaining_builds)
                for index in range(len(self.remaining_location_indeces)):
                    l = self.remaining_location_indeces[index]
                    b = self.remaining_builds[index]
                    count = 1
                    while not can_build_type[l][b.value] and index + count < len(self.remaining_builds):
                        new_index = index + count
                        self.remaining_builds[index], self.remaining_builds[new_index] = self.remaining_builds[new_index], self.remaining_builds[index]
                        b = self.remaining_builds[index]
                        count += 1
                    add_node(l, b)

                total_distance = 0
                for candidate_address, candidate_building in function_building_locations: #type: int, building_types
                    visit_count = VISITS_PER_BUILDING_TYPE[candidate_building.value]
                    
                    if not can_build_type[candidate_address][candidate_building.value] :
                        visit_count *= 3 #penalty for being impossible.

                    for house_address in house_location_adresses: #type: int
                        total_distance += visit_count * distances[candidate_address][house_address]
                    for flat_address in flat_addresses: #type: int
                        total_distance += visit_count * number_of_families_in_a_flat * distances[candidate_address][flat_address]

                self.add_score(total_distance)

                return total_distance, building_locations

            def add_score(self, score: int):
                self.visits += 1
                self.total += score

                if not self.is_top_node :
                    self.parent.add_score(score)

        ################################################################################################################
        def monte_carlo_tree_search(time_limit_seconds: int) -> Tuple[int, List[Tuple[int, building_types]]]:
            root = MCTS_details.get_top_node(locations_available, building_types_in_village)

            start_time = time.time()
            time_interval = time_limit_seconds / 10
            interval_count = 10
            next_report_time = start_time + time_interval
            rollout_count = 0
            reached_end_node = False

            biggest_score = 0
            building_locations = []
            lowest_score = maxsize
            max_depth = 0

            while True:
                if reached_end_node or time.time() - start_time > time_limit_seconds :
                    break

                if time.time() > next_report_time : 
                    next_report_time += time_interval
                    mins, sec = divmod(time.time() - start_time, 60)
                    print(f"MCTS - {interval_count}% done - Performed {rollout_count} roll outs; Score - {lowest_score};  Time elapsed BFS: {mins:.0f}m {sec:.0f}s")
                    interval_count += 10

                variable_c: float = max(1, biggest_score - lowest_score) * math.sqrt(2) 

                current: 'MCTS_details' = root

                while current:
                    if current.is_leaf :
                        if current.visits == 0 :
                            score, n = current.rollout(biggest_score)
                        else:
                            if current.create_leaves() :
                                current = current.children[0]
                                score, n = current.rollout(biggest_score)
                            else :
                                reached_end_node = True
                        rollout_count += 1
                        if biggest_score < score :
                            biggest_score = score
                        if lowest_score > score :
                            is_possible = True
                            for candidate_address, candidate_building in n: #type: int, building_types
                                if not can_build_type[candidate_address][candidate_building.value] :
                                    is_possible = False
                                    break
                            if is_possible :
                                lowest_score = score
                                building_locations = n
                        if max_depth < current.depth :
                            max_depth = current.depth
                        break
                    else:
                        current = current.lowest_scoring_child(variable_c, biggest_score)
            
            print(f"MCTS - Performed {rollout_count} roll outs; Score - {lowest_score};  Max depth: {max_depth}; {time_limit_seconds} seconds")

            for building_location in building_locations: #type: Tuple[int, building_types]
                print(f"Building location: {building_location[0]} -> {building_location[1].name}")

            return biggest_score, building_locations


        ################################################################################################################

        if len(locations_available) <= USE_BFS_WITH_LOCATION_COUNT :
            total_distance, building_location_types = bfs(attempt_details.get_top_node(), total_no_of_houses, locations_available[:])
        else:
            total_distance, building_location_types = monte_carlo_tree_search(MCTS_TIME_LIMIT_SECONDS)

        for index in range(len(site_roads_count)): #type: int
            if not site_roads_count :
                print(f"Building location: {index} -> NONE due to no roads.")

        return building_location_types



