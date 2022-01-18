from classes.ENUMS.block_codes import block_codes


class Tile:
    def __init__(self, x: int, y: int, z: int, material: block_codes, manhattan_distance_to_water: int):
        self.x = x
        self.y = y
        self.z = z
        self.material = material
        self.manhattan_distance_to_water = manhattan_distance_to_water

    def draw_tile(self, show_z_index: bool):
        if self.material == block_codes.WATER.value:
            return "~~~"
        elif self.material == block_codes.FENCE.value:
            return "###"
        elif self.material == block_codes.HOUSE:
            return "^^^"
        elif self.material == block_codes.PROPOSED:
            return "&&&"

        else:
            if show_z_index:
                if self.z > 99:
                    return " **"  # ** for a value above 100 to ensure formatting stays correct
                else:
                    return " {}".format(self.z)
            else:
                return " . "
