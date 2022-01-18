from csv import reader
from sys import maxsize
from typing import Tuple, List
import random
import time
from constants import MAX_HEIGHT, MINECRAFT_USERNAME
from classes.ENUMS.orientations import orientations
from classes.ENUMS.block_codes import block_codes
from classes.ENUMS.variable_blocks import variable_blocks
from classes.ENUMS.block_codes import water_block_codes
from classes.ENUMS.building_types import building_types
from classes.ENUMS.building_styles import building_styles
from classes.Timer import Timer
from vendor.gdmc_http_client.interfaceUtils import (
    placeBlockBatched,
    sendBlocks,
    runCommand,
)
from vendor.gdmc_http_client.worldLoader import WorldSlice
from constants import (
    BLOCK_BATCH_SIZE,
    MAX_BUILDING_RADIUS,
    GRID_WIDTH,
    NUMBER_OF_FAMILIES_IN_A_FLAT,
    DRIVE_LENGTH,
    BUILDING_MARGIN,
)
from classes.Road_Builder import create_roads
from classes.Bool_map import bool_map
from classes.Building_site import building_site
from classes.Building import building
from classes.Buildings import buildings
from classes.misc_functions import draw_sign


class Builder:
    """Builds Buildings!"""

    sites = []

    def __init__(self):
        pass

    def create(
        self,
        xCenter: int,
        zCenter: int,
        orientation: orientations,
        building: building,
        variable_block_type: block_codes = block_codes.UNKNOWN,
        requiredWidth: int = -1,
        requiredDepth: int = -1,
        world_slice: WorldSlice = None,
    ) -> bool:
        # Buidings are to be built with dynamic sizes.  To accomplish this from fixed size building maps, some rows
        # and columns are repeated.  The repeated rows and columns are defined in repeaterXs and repeaterZs
        # Must be ordered.

        if building is None:
            runCommand("tell @a 'No building provided.  Possibly area too small.'")
            print("No building provided.")
            return False, None

        site = building_site(
            building, xCenter, zCenter, orientation, requiredWidth, requiredDepth
        )

        chopped = (
            []
        )  # Need to track because chopping trees instruction is delayed before commit

        def findHeight(x: int, z: int) -> Tuple[int, int]:
            wX, wZ = x - world_slice.rect[0], z - world_slice.rect[1]
            if 0 <= wX < world_slice.rect[2] and 0 <= wZ < world_slice.rect[3]:
                return (
                    world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][wX][wZ],
                    world_slice.heightmaps["MOTION_BLOCKING"][wX][wZ],
                )
            else:
                return MAX_HEIGHT, MAX_HEIGHT

        def findHeightInRegion(
            x1: int, z1: int, x2: int, z2: int
        ):  # -> tuple[int, int, bool]:
            chopped = []
            maxY = -maxsize
            minY = maxsize

            smallX, bigX = min(x1, x2) - 1, max(x1, x2) + 1

            for x in range(smallX, bigX + 1):  # type: int
                if x - smallX % 20 == 0:
                    print(
                        "Heights {:.0f}% found.".format(
                            100 * (x - smallX) / (bigX - smallX)
                        )
                    )

                for z in range(min(z1, z2) - 1, max(z1, z2) + 2):  # type: int
                    yFloor, yObjects = findHeight(x, z)

                    # Check for tree stumps.
                    while True:
                        block1 = world_slice.getBlockAt((x, yFloor, z))
                        block2 = world_slice.getBlockAt((x, yFloor - 1, z))
                        if block1[-4] == "_log":
                            yFloor -= 1
                        elif block2[-4] == "_log":
                            yFloor -= 2
                        elif (
                            block1 in water_block_codes.list()
                            or block2 in water_block_codes.list()
                        ):
                            return (MAX_HEIGHT, MAX_HEIGHT, True)
                        else:
                            break

                    if yFloor != yObjects:
                        for yLumberjack in range(yFloor, yObjects + 1):
                            placeBlockBatched(
                                x,
                                yLumberjack,
                                z,
                                block_codes.AIR.value,
                                BLOCK_BATCH_SIZE,
                            )

                    maxY = max(maxY, yFloor)
                    minY = min(minY, yFloor)
            sendBlocks()
            return (minY - 1, maxY - 1, False)

        def buildFoundationsInRegion(x1: int, z1: int, x2: int, z2: int, floorY):
            smallX, bigX = min(x1, x2), max(x1, x2)
            smallZ, bigZ = min(z1, z2), max(z1, z2)

            midX, midZ = smallX + (bigX - smallX) // 2, smallZ + (bigZ - smallZ) // 2
            midY = findHeight(midX, midZ)[0]
            foundation_material = world_slice.getBlockAt((midX, midY - 1, midZ))

            for x in range(smallX, bigX + 1):
                if x - smallX % 20 == 0:
                    print(
                        "Foundations {:.0f}% built.".format(
                            100 * (x - smallX) / (bigX - smallX)
                        )
                    )
                for z in range(smallZ, bigZ + 1):  # type: int
                    for y in range(findHeight(x, z)[0], floorY + 1):  # type: int
                        placeBlockBatched(
                            x, y, z, foundation_material, BLOCK_BATCH_SIZE
                        )
            sendBlocks()

        # xFactor, xIndex and xZero (and the z versions) are used to rotate
        # the buidling and place the required corner on the selected box.
        # xFactor affects if columns (x is constant) are drawn left to right or right to left from the map
        # xIndex affects if the x is assigned the buidlings original "width" dimension, or the "depth" dimension
        # xZero is the address of the first column (x is constant)

        print(f"Attempting {site.get_description()}")

        # http://localhost:9000/chunks?x=4&z=0&dx=2&dz=2
        if world_slice is None:
            world_slice = WorldSlice(site.area_expanded)

        # Check for hills on proposed building site.  Build foundations if a little hilly, or error out if too hilly

        yMin, yOffset, isOverWater = findHeightInRegion(
            site.coords[0], site.coords[1], site.coords[2], site.coords[3]
        )
        site.set_altitude(yOffset)

        if isOverWater:
            runCommand("tell @a 'You can't build on water!'")
            print("Can't build over water.")
            return False

        if yMin != yOffset:
            buildFoundationsInRegion(
                site.coords[0], site.coords[1], site.coords[2], site.coords[3], yOffset
            )

        print("Foundations complete.")

        # xRepeatCount[x] defines how many times column x (ie column where x is constant) in the building map will be
        # repeated (for dynamic sizes of buildings)
        # xRepeatedAlready[x] defines how many columns have been repeated before column x - ie the shift in x to allow for
        # the extra rows already appeared.
        pointer = 0
        accum = 0
        xRepeatedAlready = [0] * site.raw_x_length
        xRepeatCount = [0] * site.raw_x_length
        for x in range(site.raw_x_length):  # type: int
            xRepeatedAlready[x] = accum
            for p in range(pointer, len(site.repeaterXs)):  # type: int
                if site.repeaterXs[p] == x:
                    accum += 1
                    xRepeatCount[x] += 1
                    pointer += 1
                elif site.repeaterXs[p] > x:
                    break

        # zRepeatCount[z]  - see description for xRepeatCount[x]
        # zRepeatedAlready[z]  - see description for xRepeatedAlready[x]
        pointer = 0
        accum = 0
        zRepeatedAlready = [0] * site.raw_z_length
        zRepeatCount = [0] * site.raw_z_length
        for z in range(site.raw_z_length):  # type: int
            zRepeatedAlready[z] = accum
            for p in range(pointer, len(site.repeaterZs)):  # type: int
                if site.repeaterZs[p] == z:
                    accum += 1
                    zRepeatCount[z] += 1
                    pointer += 1
                elif site.repeaterZs[p] > z:
                    break

        # draws a block at xyz.  The position is shifted if the building is rotated to face n, w or e
        def buildBlockRotated(blockType: str, x: int, y: int, z: int):
            xRotated, yRotated, zRotated = site.map_coords_to_site_coords(x, y, z)
            placeBlockBatched(xRotated, yRotated, zRotated, blockType, BLOCK_BATCH_SIZE)

        print("Starting Build.")

        change_bricks = (
            variable_block_type != block_codes.UNKNOWN
            and len(building.variable_block) > 0
        )

        # Read building map and draw the blocks
        with open(building.filePath()) as csvfile:
            buildingReader = reader(csvfile, delimiter=",", quotechar='"')

            for block in buildingReader:  # type: List[int,int,int,int,int,str]
                blockType = block[5]  # (int(block[3]), int(block[4]))
                x = int(block[site.building_map_x_index])
                y = int(block[1])
                z = int(block[site.building_map_z_index])

                if change_bricks and blockType in building.variable_block:
                    blockType = variable_block_type.value

                xShifted = x + xRepeatedAlready[x]
                zShifted = z + zRepeatedAlready[z]

                buildBlockRotated(blockType, xShifted, y, zShifted)

                # Repeat block if x is a repeated column
                for xRepeat in range(1, xRepeatCount[x] + 1):  # type: int
                    buildBlockRotated(blockType, xShifted + xRepeat, y, zShifted)

                    # Add in diagonals if both x and z are repeated
                    for zRepeat in range(1, zRepeatCount[z] + 1):  # type: int
                        buildBlockRotated(
                            blockType, xShifted + xRepeat, y, zShifted + zRepeat
                        )

                # Repeat block if z is a repeated row
                for zRepeat in range(1, zRepeatCount[z] + 1):  # type: int
                    buildBlockRotated(blockType, xShifted, y, zShifted + zRepeat)

        sign_y, sign_tree_height = findHeight(
            site.sign_location[0], site.sign_location[1]
        )
        draw_sign(
            site.sign_location[0],
            sign_y,
            site.sign_location[1],
            orientation,
            building.type.name,
        )

        sendBlocks()

        self.sites.append(site)

        print(f"Built: {site.get_description()}")

        return True

    def create_adjacent_to_last(
        self,
        buildOnWhichSide: orientations,
        gapBetweenBuildings: Tuple[int, building_site],
        orientation: orientations,
        building: building,
        variable_block_type: block_codes = block_codes.UNKNOWN,
        requiredWidth: int = -1,
        requiredDepth: int = -1,
    ) -> bool:

        if not self.sites:
            return False

        x_center, z_center = self.sites[-1].calc_adjacent_location(
            buildOnWhichSide,
            gapBetweenBuildings,
            orientation,
            building,
            requiredWidth,
            requiredDepth,
        )

        return self.create(
            x_center,
            z_center,
            orientation,
            building,
            variable_block_type,
            requiredWidth,
            requiredDepth,
        )

    def last_site(self) -> building_site:
        if self.sites:
            return self.sites[-1]
        else:
            return None

    def create_village(
        self,
        locations: List[Tuple[int, int]],
        building_location_types: List[Tuple[int, building_types]],
        facing_directions: List[orientations],
        building_radii: List[int],
        variable_block_type: block_codes,
        building_style: building_styles = building_styles.UNKNOWN,
        world_slice: WorldSlice = None,
    ):
        building_maps = buildings()

        for (
            building_location_type
        ) in building_location_types:  # type: Tuple[int, building_types]

            location_index: int = building_location_type[0]
            building_type: building_types = building_location_type[1]
            diameter: int = building_radii[location_index] * 2
            facing_direction: orientations = facing_directions[location_index]

            structure: building = building_maps.getBiggestByTypeStyleAndSize(
                building_type, building_style, diameter, diameter, True
            )

            if structure is not None:

                # move building to front of buiding site
                building_location: Tuple[int, int] = locations[location_index]
                distance_to_move = (diameter - structure.depth) // 2
                if distance_to_move > 0:
                    building_location = building_site.move_location(
                        building_location, facing_direction, distance_to_move
                    )

                self.create(
                    building_location[0],
                    building_location[1],
                    facing_direction,
                    structure,
                    variable_block_type,
                    world_slice=world_slice,
                )

    @classmethod
    @Timer(text="Analyze and created ran in {:.2f} seconds")
    def analyze_and_create(
        cls,
        locations: List[int],
        building_radii: List[int],
        variable_block_type: block_codes,
        building_style: building_styles = building_styles.UNKNOWN,
    ):

        builder = cls()

        areas, world_map, world_slice = bool_map.create(
            locations, building_radii, BUILDING_MARGIN
        )

        # Find required coordinates
        facing_directions, door_locations, roads = building_site.get_locations(
            locations, building_radii, world_map, DRIVE_LENGTH
        )

        # A* search from every door location to every other door location
        distances = create_roads(
            roads, GRID_WIDTH, door_locations, world_map, world_slice
        )

        # bfs search for which building type in which location
        building_location_types = building_site.calc_building_types(
            distances, building_radii, NUMBER_OF_FAMILIES_IN_A_FLAT, building_style
        )

        # Build the buildings
        builder.create_village(
            locations,
            building_location_types,
            facing_directions,
            building_radii,
            variable_block_type,
            building_style,
            world_slice,
        )

    @classmethod
    def build_one_of_everything(
        cls,
        location: Tuple[int, int],
        ground_height: int,
        building_face_direction: orientations,
    ):
        tp_string = (
            "tp "
            + MINECRAFT_USERNAME
            + " "
            + str(location[0])
            + " 100 "
            + str(location[1])
        )
        runCommand(tp_string)

        current_location = location
        max_diameter = MAX_BUILDING_RADIUS * 2
        builds: buildings = buildings()
        build_on_which_side = (
            orientations.SOUTH,
            orientations.WEST,
            orientations.NORTH,
            orientations.EAST,
        )[
            building_face_direction.value
        ]  # wnes
        sign_on_which_side = (
            orientations.NORTH,
            orientations.EAST,
            orientations.SOUTH,
            orientations.WEST,
        )[
            building_face_direction.value
        ]  # wnes
        move_back_direction = (
            orientations.EAST,
            orientations.SOUTH,
            orientations.WEST,
            orientations.NORTH,
        )[
            building_face_direction.value
        ]  # wnes

        row_number = 0

        menu = f"Max building size:{max_diameter}x{max_diameter}\n\n"

        for building_style in building_styles:  # type: building_styles
            if building_style == building_styles.UNKNOWN:  # type: building_styles
                continue

            row_number += 1
            menu = (
                menu
                + f"Row {row_number}: building_styles.{building_style.name.upper()}\n"
            )

            for building_type in building_types:  # type: building_types
                if building_type == building_types.UNKNOWN:
                    continue

                menu = (
                    menu + f"    building_types.{building_type.name.upper().upper()}:\n"
                )

                all_buildings = builds.getByTypeStyleAndSize(
                    building_type, building_style, max_diameter, max_diameter
                )

                if not all_buildings:
                    menu = menu + f"        None found in this size/style/type.\n"
                    continue

                builder: "Builder" = cls()

                all_buildings.sort(key=lambda x: x.area())

                is_first = True

                for building in all_buildings:  # type: building
                    if is_first:
                        builder.create(
                            current_location[0],
                            current_location[1],
                            building_face_direction,
                            building,
                        )
                        is_first = False
                    else:
                        builder.create_adjacent_to_last(
                            build_on_which_side, 5, building_face_direction, building
                        )

                    menu = (
                        menu
                        + f"        {building.id: <4}: {building.name} - {building.width}x{building.depth}\n"
                    )

                    sign_location = building_site.move_location(
                        builder.last_site().sign_location, sign_on_which_side, 2
                    )
                    draw_sign(
                        sign_location[0],
                        ground_height + 1,
                        sign_location[1],
                        building_face_direction,
                        building.name,
                        building_style.name,
                        building_type.name,
                        f"{building.width}x{building.depth} ID:{building.id}",
                    )

                sign_location = building_site.move_location(
                    current_location, sign_on_which_side, MAX_BUILDING_RADIUS
                )
                draw_sign(
                    sign_location[0],
                    ground_height + 1,
                    sign_location[1],
                    building_face_direction,
                    building_style.name,
                    building_type.name,
                )

                current_location = building_site.move_location(
                    current_location, move_back_direction, max_diameter
                )

        print(menu)

    @classmethod
    def build_one_of_everything_variable_blocks(
        cls,
        location: Tuple[int, int],
        ground_height: int,
        building_face_direction: orientations,
    ):

        tp_string = (
            "tp "
            + MINECRAFT_USERNAME
            + " "
            + str(location[0])
            + " 100 "
            + str(location[1])
        )
        runCommand(tp_string)

        current_location = location
        max_diameter = MAX_BUILDING_RADIUS * 2
        builds: buildings = buildings()
        build_on_which_side = (
            orientations.SOUTH,
            orientations.WEST,
            orientations.NORTH,
            orientations.EAST,
        )[
            building_face_direction.value
        ]  # wnes
        sign_on_which_side = (
            orientations.NORTH,
            orientations.EAST,
            orientations.SOUTH,
            orientations.WEST,
        )[
            building_face_direction.value
        ]  # wnes
        move_back_direction = (
            orientations.EAST,
            orientations.SOUTH,
            orientations.WEST,
            orientations.NORTH,
        )[
            building_face_direction.value
        ]  # wnes

        row_number = 0

        menu = f"Max building size:{max_diameter}x{max_diameter}\n\n"

        for building_type in building_types:  # type: building_types
            if building_type == building_types.UNKNOWN:
                continue

            menu = menu + f"building_type.{building_type.name.upper()}\n"

            all_buildings = builds.getByTypeStyleAndSize(
                building_type, building_styles.CUSTOM, max_diameter, max_diameter
            )
            all_buildings.sort(key=lambda x: x.area())

            if not all_buildings:
                menu = menu + f"        None found in this size/type.\n"
                continue

            for build in all_buildings:  # type: building

                menu = (
                    menu
                    + f"        Row {row_number}: {build.id: <4}: {build.name} - {build.width}x{build.depth}\n"
                )
                row_number += 1

                builder: "Builder" = cls()

                builder.create(
                    current_location[0],
                    current_location[1],
                    building_face_direction,
                    build,
                )
                menu = menu + f"            Block: none - original:\n"
                sign_location = building_site.move_location(
                    builder.last_site().sign_location, sign_on_which_side, 2
                )
                draw_sign(
                    sign_location[0],
                    ground_height + 1,
                    sign_location[1],
                    building_face_direction,
                    build.name,
                    "Orginal",
                    building_type.name,
                    f"{build.width}x{build.depth} ID:{build.id}",
                )

                for variable_block in variable_blocks:  # type: variable_blocks

                    builder.create_adjacent_to_last(
                        build_on_which_side,
                        5,
                        building_face_direction,
                        build,
                        variable_block.value,
                    )
                    menu = menu + f"            Block: {variable_block.value.value}:\n"

                    sign_location = building_site.move_location(
                        builder.last_site().sign_location, sign_on_which_side, 2
                    )
                    draw_sign(
                        sign_location[0],
                        ground_height + 1,
                        sign_location[1],
                        building_face_direction,
                        build.name,
                        variable_block.value.value.replace("minecraft:", ""),
                        building_type.name,
                        f"{build.width}x{build.depth} ID:{build.id}",
                    )

                sign_location = building_site.move_location(
                    current_location, sign_on_which_side, MAX_BUILDING_RADIUS
                )
                draw_sign(
                    sign_location[0],
                    ground_height + 1,
                    sign_location[1],
                    building_face_direction,
                    build.name,
                    building_type.name,
                    build.variable_block[0].replace("minecraft:", "")
                    if len(build.variable_block) > 0
                    else "",
                    build.variable_block[1].replace("minecraft:", "")
                    if len(build.variable_block) > 1
                    else "",
                )

                current_location = building_site.move_location(
                    current_location, move_back_direction, max_diameter
                )

        print(menu)
