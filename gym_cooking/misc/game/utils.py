import pygame


class Color:
    BLACK = (0, 0, 0)
    FLOOR = (252, 235, 215)  # light gray
    COUNTER = (220, 170, 110)   # tan/gray
    CARPET = (153, 0, 0)  # light gray
    COUNTER_BORDER = (114, 93, 51)  # darker tan
    WALL = (230, 194, 151)
    WALL_BORDER = (32, 32, 32) #grey blackish
    DELIVERY = (96, 96, 96)  # grey
    SHELF = (204, 102, 0)


KeyToTuple = {
    # pygame.K_UP    : ( 0, -1),  #273
    # pygame.K_DOWN  : ( 0,  1),  #274
    pygame.K_UP    : ( 0, -1),  #273
    pygame.K_DOWN  : ( 0,  1),  #274
    pygame.K_RIGHT : ( 1,  0),  #275
    pygame.K_LEFT  : (-1,  0),  #276
    pygame.K_f: "FETCH",
    pygame.K_c: "CHOP",
    pygame.K_p: "PLATE",
    pygame.K_d: "DELIVER",
    pygame.K_b: "BAKE",
}
