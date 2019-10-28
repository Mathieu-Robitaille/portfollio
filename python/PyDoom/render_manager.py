from math import cos, sin, pi, fabs, sqrt
from timeit import default_timer as timer

import pygame as pg
import logger
from globals import *


def points_in_circum(offset=0, radius=100, n=100):
    """
    Returns a list of (x, y) points offset from 0, 0 based on self.pos
    These coordinates are the circumference of a circle

    ARGS:
    @ param r = Radius in pixels
    @ param n = number of divisions, meaning the frequency of points along the circumfrence.

    RETURNS:
        List of (x, y) points
    """
    return [((cos(2 * pi / n * x) * radius + offset),
             (sin(2 * pi / n * x) * radius + offset))
            for x in range(0, n + 1)]


def draw_level(g, s):
    # localise these vars as it's more clear plus python accesses local variables faster
    # Expand player position for clarity
    player_pos_x = g.player.pos[0]
    player_pos_y = g.player.pos[1]
    player_angle = g.player.angle
    player_fov = g.player.fov
    cast_list = []


    """
    NEW PLAN!
    Instead of needlessly iterating over each pixel and messing with calculating each pixel's distance
    Why not just get the distance to each wall, then draw gradients between those wall points????
    
    """

    for i in range(int(SCREEN_WIDTH)):
        # Get the angle we want to cast to
        ray_angle = (player_angle - player_fov / 2.0) + float(i) / float(SCREEN_WIDTH) * player_fov

        # The line representing where the cast is evaluating
        player_line = ((player_pos_x, player_pos_y),
                       (player_pos_x + sin(ray_angle) * 100, player_pos_y + cos(ray_angle) * 100))

        distances = [30]
        walls = [0]

        for wall in g.level.walls[1:]:
            test = line_intersection(Line(*player_line), Line(*wall))
            if not test:
                continue
            distance = distance_to_point((player_pos_x, player_pos_y), test)
            distances.append(distance)
            walls.append(wall)


        # The distance we've found to the wall we're looking at
        distance_to_wall = min(distances)
        target_wall = walls[distances.index(distance_to_wall)]

        # Calculate the top of the walls based off the screen
        ceiling = (SCREEN_HEIGHT / 2.0) - SCREEN_HEIGHT / distance_to_wall

        # Calc the floor
        floor = SCREEN_HEIGHT - ceiling

        # Force the color value in between 0-255
        val = (255 / distance_to_wall if 255 / distance_to_wall > 0 else 0) % 255

        cast_list.append([ceiling, floor, i, val, target_wall])

    draw_screen(s, cast_list)
    draw_sprites(s, cast_list)
    draw_minimap(s, g, cast_list)


def draw_screen(s, c):
    # Draw each cast as a vertical line to be matched up with the next cast for
    # smoooooth walls

    # Draw the sky
    pg.draw.rect(s, (135, 206, 235),
                 (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT / 2))

    # Draw the floor so its prettier
    pg.draw.rect(s, (0, 64, 0),
                 (0, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT / 2))

    for i in range(len(c)):
        try:
            if i + 1 >= len(c):
                continue  # finish the wall

            if c[i][0] is 0 and c[i][1] is 0:
                continue  # I'm super good at coding

            # The X offsets of the current vertical line and the subsequent line
            x1 = c[i][2]
            x2 = c[i + 1][2]
            val = c[i][3]
            color = (val, val, val)

            coordinates = [(x1, c[i][0]),  # Ceiling of current cell
                           (x1, c[i + 1][0]),  # Ceiling of next cell
                           (x2, c[i][1]),  # Floor of current cell
                           (x2, c[i + 1][1])]  # Floor of next cell
            pg.draw.polygon(s, color, coordinates, 0)
        except IndexError as e:  # e here incase I want to use it later,
            logger.log("you done it now boy")


def draw_sprites(s, c):
    pass


def draw_minimap(s, g, c):
    pg.draw.rect(s, pg.Color("Black"),
                 (SCREEN_WIDTH - (LEVEL_WIDTH * LEVEL_CELL_SPACING),
                  0,
                  LEVEL_WIDTH * LEVEL_CELL_SPACING,
                  LEVEL_HEIGHT * LEVEL_CELL_SPACING))

    # Translate the current player's position to the mini map structure
    player_pos = (int(SCREEN_WIDTH - (g.player.pos[0] * LEVEL_CELL_SPACING)),
                  int(g.player.pos[1] * LEVEL_CELL_SPACING))

    # Draw the player fov
    player_left_aim = (player_pos[0] - 20 * sin(g.player.angle - g.player.fov / 2),
                       player_pos[1] + 20 * cos(g.player.angle - g.player.fov / 2))
    player_right_aim = (player_pos[0] - 20 * sin(g.player.angle + g.player.fov / 2),
                        player_pos[1] + 20 * cos(g.player.angle + g.player.fov / 2))
    pg.draw.line(s, pg.Color("Red"), player_pos, player_left_aim)
    pg.draw.line(s, pg.Color("Red"), player_pos, player_right_aim)

    # Player
    pg.draw.circle(s, pg.Color("red"), player_pos, 1)
    for wall in g.level.walls:
        start = (int(SCREEN_WIDTH - (wall[0][0] * LEVEL_CELL_SPACING)),
                 int(wall[0][1] * LEVEL_CELL_SPACING))
        end = (int(SCREEN_WIDTH - (wall[1][0] * LEVEL_CELL_SPACING)),
               int(wall[1][1] * LEVEL_CELL_SPACING))
        pg.draw.line(s, pg.Color("Green"), start, end)
    for cast in c:
        try:
            ls = cast[4][0]
            le = cast[4][1]
            ls = (int(SCREEN_WIDTH - (ls[0] * LEVEL_CELL_SPACING)),
                  int(ls[1] * LEVEL_CELL_SPACING))
            le = (int(SCREEN_WIDTH - (le[0] * LEVEL_CELL_SPACING)),
                  int(le[1] * LEVEL_CELL_SPACING))
            pg.draw.line(s, pg.Color("Red"), ls, le)
        except IndexError:
            logger.log("index error")
        except TypeError as e:
            logger.log("Type error")


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "x: {0}, y: {1}".format(self.x, self.y)


class Line:
    def __init__(self, p1, p2):
        self.p1 = Point(*p1)
        self.p2 = Point(*p2)


def line_intersection(l1, l2):
    d = (l2.p2.y - l2.p1.y) * (l1.p2.x - l1.p1.x)\
        - \
            (l2.p2.x - l2.p1.x) * (l1.p2.y - l1.p1.y)
    if d == 0:
        return False

    n_a = (l2.p2.x - l2.p1.x) * (l1.p1.y - l2.p1.y)\
        - \
          (l2.p2.y - l2.p1.y) * (l1.p1.x - l2.p1.x)
    n_b = (l1.p2.x - l1.p1.x) * (l1.p1.y - l2.p1.y)\
        - \
          (l1.p2.y - l1.p1.y) * (l1.p1.x - l2.p1.x)

    ua = n_a / d
    ub = n_b / d

    if 0 <= ua <= 1 and 0 <= ub <= 1:
        x = l1.p1.x + (ua * (l1.p2.x - l1.p1.x))
        y = l1.p1.x + (ua * (l1.p2.y - l1.p1.y))
        return x, y
    else:
        return False


def distance_to_point(a, b):
    """
    A simple point to point distance measure tool
    :param a: x, y coords of point a
    :param b: x, y coords of point a
    :return: float: distance between a and b
    """
    return sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)


