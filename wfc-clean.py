import pygame
import random
import copy
import json
from itertools import product
from functools import partial
from collections import defaultdict
import string
import time

pygame.init()

# global variables
width = 600
height = 600
rez = 30

DIRS = ["up", "down", "left", "right"]

display = pygame.display.set_mode((width, height))

# 0 - 9, then a - f
hex_digits = string.digits + string.ascii_lowercase[0:6]

# all two digit hex numbers as lowercase strings, e.g. "0f"
# (to match the Zelda Walking Tour map)
hex_numbers = ["".join(digits) for digits in product(hex_digits, hex_digits)]

font = pygame.font.Font("./data/poppins_font/Poppins-Light.ttf", 16)

def parse_hex_map():
    with open("data/zelda_overworld_map.txt", "r") as file_pointer:
        hex_rows = [row.strip().split(" ") for row in file_pointer]
    # for row in raw_rows:
    #     print(row)
    return hex_rows

"""
Start with a set of Graphical Tiles, and an empty Map...

Each Tile has a constrained set of possible "neighbors" in different cardinal directions
(based on existing training data, e.g. the NES Zelda overworld)



"""
