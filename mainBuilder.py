from classes.Builder import Builder
from classes.ENUMS.orientations import orientations
from classes.ENUMS.block_codes import block_codes
from classes.ENUMS.building_styles import building_styles


#Builder.build_one_of_everything(
#          location = (0, 0)
#        , ground_height = 3
#        , building_face_direction = orientations.NORTH
#        )

Builder.build_one_of_everything_variable_blocks(
          location = (0, 0)
        , ground_height = 3
        , building_face_direction = orientations.NORTH
        )

#Builder.analyze_and_create(
#    [(57, 123), (34, 123), (52, 99), (138, 124), (24, 155), (79, 115), (50, 146), (73, 169), (136, 143), (66, 189), (14, 96), (67, 83), (40, 68), (132, 179), (61, 33), (163, 137), (153, 170), (86, 141), (165, 94), (54, 166), (78, 224), (93, 204), (88, 64)]
#    , [10, 11, 7, 8, 8, 7, 7, 11, 8, 8, 9, 7, 9, 7, 12, 9, 8, 7, 9, 7, 12, 7, 7]
#    , block_codes.DARK_OAK_WOOD
#    , building_styles.CUSTOM
#    )