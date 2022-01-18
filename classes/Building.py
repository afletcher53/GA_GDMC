from classes.ENUMS.building_types import building_types
from classes.ENUMS.building_styles import building_styles
from typing import Tuple, List

class building(object):
    name = ""
    fileName = ""
    width = 0
    depth = 0
    height = 0

    type = building_types.UNKNOWN
    style = building_styles.UNKNOWN

    id = -1

    maxWidth = 0
    maxDepth = 0
    repeatableXs = []
    repeatableZs = []

    def __init__(self
                 , name: str
                 , fileName: str
                 , width: int
                 , depth: int
                 , height: int
                 , type: int
                 , style: int
                 , variable_block: str
                 , id: int
                 , maxWidth: int
                 , maxDepth: int
                 , repeatableXs: str
                 , repeatableZs: str):
        self.name: str = name
        self.fileName: str = fileName
        self.width: int = width
        self.depth: int = depth
        self.height: int = height
        self.id: int = id
        self.type: building_types = building_types(type)
        self.style: building_styles = building_styles(style)
        self.variable_block: List[str] = variable_block.split(',') if variable_block is not None else []
        self.maxWidth: int = maxWidth
        self.maxDepth: int = maxDepth
        self.repeatableXs: List[str] = list(map(int, repeatableXs.split(',')))
        self.repeatableZs: List[str] = list(map(int, repeatableZs.split(',')))

    def longest_side(self):
        return max(self.width, self.depth)

    def area(self):
        return self.width * self.depth

    def filePath(self) -> str :
        return 'data/building_maps/' + self.fileName

    def getRepeaters(self, requiredWidth: int, requiredDepth: int) -> Tuple[List[int], List[int]]:
        if self.maxWidth > self.width :
            requiredWidth = min(self.maxWidth, requiredWidth)
        if self.maxDepth > self.depth :
            requiredDepth = min(self.maxDepth, requiredDepth)

        moreX = max(requiredWidth - self.width, 0)
        moreZ = max(requiredDepth - self.depth, 0)

        def create(extraCount: int, available: List[int]) -> List[int]:
            reps = []

            if extraCount > 0 and available :
                for n in range[extraCount]:
                    reps.append(available[n % len(available)])
                reps.sort()

            return reps

        repX = create(moreX, self.repeatableXs)
        repZ = create(moreZ, self.repeatableZs)

        return repX, repZ

    @classmethod
    def from_json(cls, data: dict):
        return cls(**data)
