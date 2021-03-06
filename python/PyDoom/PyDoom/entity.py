from math import pi, cos, sin

import pygame as pg
import os

from PyDoom.globals import TEAM_PLAYER, TEAM_ENEMY, two_d_to_one_d, Point, SCREEN_HEIGHT, SCREEN_WIDTH
from PyDoom.imageutilities import get_image


class Entity:
    def __init__(self, game, pos, sprite, team):
        """

        :param pos: Point object
        :param sprite:
        :param team:
        :param game:
        """
        # This entity's position in X, Y
        self.pos = pos

        # The players FOV
        # Default pi / 4
        # convert 110 deg to radians
        self.fov = pi / 3  # 110 * pi / 180

        # This entity's sprite
        self.sprite = get_image(sprite)

        self.team = team

        # local variable for time between things
        self.tick = 0.0

        self.dead = False

        self.max_health = 100

        self.game = game

        # Used in move check by adding a bit and ensuring that value does not intersect with a wall
        self.move_speed = 1.75

        self.move_buffer = 1.5

        #
        # Properties
        #
        # Entities angle
        self.__angle = 0

        #
        self.__health = self.max_health

    @property
    def angle(self):
        return self.__angle

    @angle.setter
    def angle(self, val):
        self.__angle = val % (pi * 2)

    @property
    def health(self):
        return self.__health

    @health.setter
    def health(self, val):
        if self.__health + val <= 0:
            self.die()
        elif self.__health + val > self.max_health:
            self.__health = self.max_health
        else:
            self.__health += val

    def update(self, frame_time):
        self.tick = frame_time
        if self.health < 0:
            self.dead = True
        self.move()

    def die(self):
        self.dead = True

    # We can figure out resistances and what not later on if i want
    # For right now lets just get a rough idea working then flesh it out later
    def do_damage(self, target, damagetype, amount):
        if isinstance(target, Entity):
            target.take_damage(amount)

    def take_damage(self, amount):
        self.health += -amount

    def heal(self, amount):
        self.health += amount

    def move(self):
        pass

    def event(self, event):
        pass

    def move_check(self, direction):
        "forwards, backwards, strafe left, strafe right"
        # This is really messy... How could I simplify this?
        if direction == 1:  # backwards
            tmp_pos = (self.pos.x - (sin(self.angle) * (self.move_speed * self.move_buffer + 0.5) * self.tick),
                       self.pos.y + (cos(self.angle) * (self.move_speed * self.move_buffer + 0.5) * self.tick))
            if not self.game.level.map[two_d_to_one_d(tmp_pos, self.game.level.width)].is_wall:
                self.pos.x = self.pos.x - (sin(self.angle) * self.move_speed * self.tick)
                self.pos.y = self.pos.y + (cos(self.angle) * self.move_speed * self.tick)
        elif direction == 2:  # forwards
            tmp_pos = (self.pos.x + (sin(self.angle) * (self.move_speed * self.move_buffer) * self.tick),
                       self.pos.y - (cos(self.angle) * (self.move_speed * self.move_buffer) * self.tick))
            if not self.game.level.map[two_d_to_one_d(tmp_pos, self.game.level.width)].is_wall:
                self.pos.x = self.pos.x + (sin(self.angle) * self.move_speed * self.tick)
                self.pos.y = self.pos.y - (cos(self.angle) * self.move_speed * self.tick)
        elif direction == 3:  # Strafe left
            tmp_pos = (self.pos.x - (sin(self.angle - pi / 2) * (self.move_speed * self.move_buffer) * self.tick),
                       self.pos.y - (cos(self.angle + pi / 2) * (self.move_speed * self.move_buffer) * self.tick))
            if not self.game.level.map[two_d_to_one_d(tmp_pos, self.game.level.width)].is_wall:
                self.pos.x = self.pos.x - (sin(self.angle - pi / 2) * self.move_speed * self.tick)
                self.pos.y = self.pos.y - (cos(self.angle + pi / 2) * self.move_speed * self.tick)
        elif direction == 4:  # Strafe right
            tmp_pos = (self.pos.x + (sin(self.angle - pi / 2) * (self.move_speed * self.move_buffer) * self.tick),
                       self.pos.y + (cos(self.angle + pi / 2) * (self.move_speed * self.move_buffer) * self.tick))
            if not self.game.level.map[two_d_to_one_d(tmp_pos, self.game.level.width)].is_wall:
                self.pos.x = self.pos.x + (sin(self.angle - pi / 2) * self.move_speed * self.tick)
                self.pos.y = self.pos.y + (cos(self.angle + pi / 2) * self.move_speed * self.tick)


class Enemy(Entity):
    def __init__(self, game, pos=Point(13.0, 13.0), sprite="imp.png", team=TEAM_ENEMY):
        super().__init__(game, pos=pos, sprite=sprite, team=team)
        self.spotted_player = False  # ??? How are we going to handle attacking the player?
        self.angle = pi

    def update(self, frame_time):
        super().update(frame_time)
        self.move()

    def do_damage(self, target, damage_type, amount):
        super().do_damage(target, damage_type, amount)

    def take_damage(self, amount):
        super().take_damage(amount)

    def move(self):
        super().move()


class Player(Entity):
    def __init__(self, game):
        super().__init__(game=game, pos=Point(3.0, 3.0), sprite=None, team=TEAM_PLAYER)
        self.prev_mouse_aim = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.bugged_aiming_because_pycharm = "PYCHARM_HOSTED" in os.environ

        # List for W, A, S, D, Q, E (Q, E used for strafing)
        self.wasdqe_held = [False, False, False, False, False, False]

    def update(self, frame_time):
        super().update(frame_time)

    def do_damage(self, target, damagetype, amount):
        super().do_damage(target, damagetype, amount)

    def take_damage(self, amount):
        super().take_damage(amount)

    def mouse_aim(self):
        """
        There's a difference in running this code via python in the commandline vs pycharm...
        The following is needed if we're running this from pycharm
        pos = pg.mouse.get_pos()
        diff = self.prev_mouse_aim[0] - pos[0]
        self.angle -= (0.75 * (diff / 10) * self.tick)
        pg.mouse.set_pos((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        """
        if self.bugged_aiming_because_pycharm:
            pos = pg.mouse.get_pos()
            diff = self.prev_mouse_aim[0] - pos[0]
            self.angle -= (0.75 * (diff / 10) * self.tick)
            pg.mouse.set_pos((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        else:
            diff = pg.mouse.get_rel()
            self.angle -= (0.75 * (-diff[0] / 10) * self.tick)

    def move(self):
        if self.wasdqe_held[0]:  # W
            self.move_check(1)
        if self.wasdqe_held[1]:  # A
            # self.angle -= 0.75 * self.tick
            self.move_check(3)
        if self.wasdqe_held[2]:  # S
            self.move_check(2)
        if self.wasdqe_held[3]:  # D
            # self.angle += 0.75 * self.tick
            self.move_check(4)
        # if self.wasdqe_held[4]:  # Q
        #     self.move_check(3)
        # if self.wasdqe_held[5]:  # E
        #     self.move_check(4)
        self.mouse_aim()

    def event(self, event):
        super().event(event)
        if event.type in (pg.KEYDOWN, pg.KEYUP):
            if event.key == pg.K_w:
                self.wasdqe_held[0] = not self.wasdqe_held[0]
            if event.key == pg.K_a:
                self.wasdqe_held[1] = not self.wasdqe_held[1]
            if event.key == pg.K_s:
                self.wasdqe_held[2] = not self.wasdqe_held[2]
            if event.key == pg.K_d:
                self.wasdqe_held[3] = not self.wasdqe_held[3]
            if event.key == pg.K_q:
                self.wasdqe_held[4] = not self.wasdqe_held[4]
            if event.key == pg.K_e:
                self.wasdqe_held[5] = not self.wasdqe_held[5]
