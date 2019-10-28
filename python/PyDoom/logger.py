import pygame as pg
from globals import SCREEN_WIDTH, LEVEL_HEIGHT, LEVEL_WIDTH, LEVEL_CELL_SPACING
def log(*msg):
    print(msg)

def on_screen_log(msg, surface):
    font = pg.font.Font('freesansbold.ttf', 16)
    text = font.render(msg, True, pg.Color("Red"))
    text_rect = text.get_rect()
    text_rect.y = (LEVEL_HEIGHT + 1) * LEVEL_CELL_SPACING
    text_rect.left = SCREEN_WIDTH - (LEVEL_WIDTH * LEVEL_CELL_SPACING)
    surface.blit(text, text_rect)
