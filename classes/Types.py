from typing import Tuple


Tile = Tuple[int, int, int, int]  # x_index, y_index, z_index, cube_type
GridLocation = Tuple[int, int, int]  # Grid locations are x_index, z_index, y_index
TileMap = Tuple[Tile, Tile]
