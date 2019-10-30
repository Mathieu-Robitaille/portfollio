import pygame as pg

from math import pi, cos, sin
from globals import TEAM_PLAYER, TEAM_ENEMY, two_d_to_one_d


class Entity:
    def __init__(self, pos, sprite, team, game):
        # This entity's position in X, Y
        self.pos = pos
        # This entity's facing angle
        self.angle = pi / 2

        # The players FOV
        self.fov = pi / 3

        # This entity's sprite (Image Utilities are not implemented yet)
        # self.sprite = iu.images[sprite]
        self.team = team

        # local variable for time between things
        self.tick = 0.0

        self.dead = False

        self.game = game

        # Used in move check by adding a bit and ensuring that value does not intersect with a wall
        self.move_speed = 1.75
        
        #
        self.health = 100

    def update(self):
        if self.health < 0:
            self.dead = True
        self.move()

    def do_damage(self, target, damagetype, amount):
        pass

    def take_damage(self, amount):
        pass

    def move(self):
        pass

    def event(self, event, timer):
        self.tick = timer

    def move_check(self, direction):
        "forwards, backwards, strafe left, strafe right"
        # This is really messy... How could I simplify this?
        if direction is 1:  # backwards
            tmp_pos = (self.pos[0] + (sin(self.angle) * (self.move_speed * 1.2) * self.tick),
                       self.pos[1] + (cos(self.angle) * (self.move_speed * 1.2) * self.tick))
            if not self.game.level.map[two_d_to_one_d(tmp_pos, self.game.level.width)].is_wall:
                self.pos = (self.pos[0] + (sin(self.angle) * self.move_speed * self.tick),
                            self.pos[1] + (cos(self.angle) * self.move_speed * self.tick))
        elif direction is 2:  # forwards
            tmp_pos = (self.pos[0] - (sin(self.angle) * (self.move_speed * 1.2) * self.tick),
                       self.pos[1] - (cos(self.angle) * (self.move_speed * 1.2) * self.tick))
            if not self.game.level.map[two_d_to_one_d(tmp_pos, self.game.level.width)].is_wall:
                self.pos = (self.pos[0] - (sin(self.angle) * self.move_speed * self.tick),
                            self.pos[1] - (cos(self.angle) * self.move_speed * self.tick))
        elif direction is 3:  # Strafe left
            tmp_pos = (self.pos[0] + (sin(self.angle - pi / 2) * (self.move_speed * 1.2) * self.tick),
                       self.pos[1] + (cos(self.angle - pi / 2) * (self.move_speed * 1.2) * self.tick))
            if not self.game.level.map[two_d_to_one_d(tmp_pos, self.game.level.width)].is_wall:
                self.pos = (self.pos[0] + (sin(self.angle - pi / 2) * self.move_speed * self.tick),
                            self.pos[1] + (cos(self.angle - pi / 2) * self.move_speed * self.tick))
        elif direction is 4:  # Strafe right
            tmp_pos = (self.pos[0] - (sin(self.angle - pi / 2) * (self.move_speed * 1.2) * self.tick),
                       self.pos[1] - (cos(self.angle - pi / 2) * (self.move_speed * 1.2) * self.tick))
            if not self.game.level.map[two_d_to_one_d(tmp_pos, self.game.level.width)].is_wall:
                self.pos = (self.pos[0] - (sin(self.angle - pi / 2) * self.move_speed * self.tick),
                            self.pos[1] - (cos(self.angle - pi / 2) * self.move_speed * self.tick))



class Enemy(Entity):
    def __init__(self, game):
        super().__init__(pos=(10.0, 10.0), sprite=None, team=TEAM_ENEMY, game=game)
        self.spotted_player = False  # ??? How are we going to handle attacking the player?

    def update(self):
        super().update()
        self.move()

    def do_damage(self, target, damage_type, amount):
        super().do_damage(target, damage_type, amount)
        pass

    def take_damage(self, amount):
        super().take_damage(amount)
        pass

    def move(self):
        super().move()


class Player(Entity):
    def __init__(self, game):
        super().__init__(pos=(3.0, 3.0), sprite=None, team=TEAM_PLAYER, game=game)

        # List for W, A, S, D, Q, E (Q, E used for strafing)
        self.wasdqe_held = [False, False, False, False, False, False]

    def update(self):
        super().update()

    def do_damage(self, target, damagetype, amount):
        super().do_damage(target, damagetype, amount)
        pass

    def take_damage(self, amount):
        super().take_damage(amount)
        pass

    def move(self):
        if self.wasdqe_held[0]:  # W
            self.move_check(1)
        if self.wasdqe_held[1]:  # A
            self.angle -= 1.0 * self.tick
        if self.wasdqe_held[2]:  # S
            self.move_check(2)
        if self.wasdqe_held[3]:  # D
            self.angle += 1.0 * self.tick
        if self.wasdqe_held[4]:  # Q
            self.move_check(3)
        if self.wasdqe_held[5]:  # E
            self.move_check(4)

    def event(self, event, timer):
        super().event(event, timer)
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
