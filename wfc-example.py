import pygame
import random
import copy
import json
from itertools import product
from functools import partial
from collections import defaultdict
import string
import time

# Borrowed / Adapted From this example:
# https://dev.to/kavinbharathi/the-fascinating-wave-function-collapse-algorithm-4nc3

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


# main game function
def main():
    tile_images = load_tile_images()

    hexes = hex_numbers[0 : len(tile_images) + 1]

    print(f"{len(hexes)} hexes:", hexes)

    hexes_to_images = dict(zip(hexes, tile_images))
    # print(hex_tile_map)

    hex_map = parse_hex_map()

    tile_options = get_tile_options(hex_map)

    hexes_to_tiles = dict()

    grid_options = []

    for this_hex, this_image in hexes_to_images.items():
        tile = Tile(this_hex, this_image)
        grid_options.append(tile)
        hexes_to_tiles[this_hex] = tile

    tile_option_keys = list(tile_options.keys())
    tile_option_keys.sort()

    print(f"{len(tile_option_keys)} Tile Options:", tile_option_keys)

    for this_hex, this_tile in hexes_to_tiles.items():
        options = tile_options.get(this_hex)
        # print(f"{this_hex} {this_tile}")

        if not options:
            continue

        tile_rules = dict()
        has_data = False
        for direction, hexes in options.items():
            directional_tiles = [(hexes_to_tiles[hex], hexes[hex]) for hex in hexes]
            tile_rules[direction] = directional_tiles
            if directional_tiles:
                has_data = True
        #print(f"{this_hex}: set_rules({tile_rules})")

        if has_data:
            this_tile.set_rules(tile_rules)

    # wave grid
    wave_grid = Grid(width, height, rez, grid_options)
    wave_grid.initiate()

    # game loop
    loop = True
    hover_toggle = False

    while loop:
        display.fill((0, 0, 0))
        # event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    hover_toggle = not hover_toggle

                if event.key == pygame.K_q:
                    loop = False
                    exit()

        # grid draw function
        wave_grid.draw(display)

        # grid collapse method to run the algorithm
        wave_grid.collapse()

        # mouse position and hover debug
        if hover_toggle:
            mos_pos = pygame.mouse.get_pos()
            hover(mos_pos, rez, wave_grid)

        # update the display
        pygame.display.flip()


def hover(mouse_pos, rez, grid):
    mx, my = mouse_pos
    x = mx // rez
    y = my // rez
    cell = grid.grid[y][x]

    # cell information
    cell_entropy = cell.entropy()
    cell_collpased = cell.collapsed
    cell_options = [d for d in DIRS if hasattr(cell.options, d)]

    # hover box
    pygame.draw.rect(display, (20, 20, 20), (mouse_pos[0], mouse_pos[1], 200, 100))

    # hover text/info
    disp_msg(f"entropy  : {cell_entropy}", mx + 10, my + 10)
    disp_msg(f"collapsed : {cell_collpased}", mx + 10, my + 30)
    disp_msg(f"options   : {cell_options}", mx + 10, my + 50)
    disp_msg(f"hex       : {cell.hex}", mx + 10, my + 70)


def disp_msg(text, x, y):
    msg = font.render(str(text), 1, (255, 255, 255))
    display.blit(msg, (x, y))


def load_tile_images():
    # loading tile images
    tile_images = []
    for i in range(157):
        # load tetris tile
        img = load_image(f"./data/tiles/overworld_tile_{i}.png", rez)
        tile_images.append(img)
    print(f"Loaded {len(tile_images)} tile images")
    return tile_images


# function for loading images with given resolution/size
def load_image(path, rez_, padding=0):
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, (rez_ - padding, rez_ - padding))
    return img


def load_overworld_tiles_from_sheet():
    """
    Load the individual tiles from overworldtiles.png
    (Also export to individual tile files)
    """
    overworld_tile_sheet = pygame.image.load("data/zelda_overworld_tiles.png")

    overworld_tiles = []

    i = 0
    for top in range(0, 8 * 17, 17):
        for left in range(0, 20 * 17, 17):
            tileSurf = pygame.Surface((16, 16))
            tileSurf.blit(overworld_tile_sheet, (0, 0), (left + 1, top + 1, 16, 16))
            pygame.image.save(tileSurf, f"data/tiles/overworld_tile_{i}.png")
            overworld_tiles.append(tileSurf)
            i += 1

    return overworld_tiles


class Cell:
    def __init__(self, x, y, rez, options):
        self.x = x
        self.y = y
        self.rez = rez
        self.options = options
        self.hex = ""
        self.collapsed = False

    def __repr__(self):
        return f"Cell(X{self.x}, Y{self.y}, options={self.options})"

    # method for drawing the cell
    def draw(self, win):
        if len(self.options) == 1:
            self.options[0].draw(win, self.y * self.rez, self.x * self.rez)
            self.hex = self.options[0].hex

    # return the entropy/the length of options
    def entropy(self):
        return len(self.options)

    # update the collapsed variable
    def update(self):
        self.collapsed = bool(self.entropy() == 1)

    # observe the cell/collapse the cell
    def observe(self):
        try:
            self.options = [random.choice(self.options)]
            self.collapsed = True
        except Exception as e:
            print("ignoring exception:", e)
            return


class Tile:
    def __init__(self, hex, img):
        self.hex = hex
        self.img = img
        self.index = -1
        self.up = []
        self.right = []
        self.down = []
        self.left = []
        #print(f"(Creating Tile: {self.hex})")

    def __repr__(self):
        return f"Tile({self.hex})"

    # draw a single tile
    def draw(self, win, x, y):
        win.blit(self.img, (x, y))

    # set the rules for each tile
    def set_rules(self, directional_options):
        for direction, options in directional_options.items():
            this_direction = getattr(self, direction)
            this_direction += options
        # print(
        #     f"{self.hex} - up: {len(self.up)}, down: {len(self.down)}, left: {len(self.left)}, right: {len(self.right)}"
        # )


class Grid:
    def __init__(self, width, height, rez, options):
        self.width = width
        self.height = height
        self.rez = rez
        self.w = self.width // self.rez
        self.h = self.height // self.rez
        self.grid = []
        self.options = options

    # draw each cell in the grid
    def draw(self, win):
        for row in self.grid:
            for cell in row:
                cell.draw(win)

    # initiate each spot in the grid with a cell object
    def initiate(self):
        for i in range(self.w):
            self.grid.append([])
            for j in range(self.h):
                cell = Cell(i, j, self.rez, self.options)
                self.grid[i].append(cell)
                # print(f"Created Cell: {cell}")

    # arbitrarily pick a cell using [entropy heuristic]
    def heuristic_pick(self):
        # shallow copy of a grid
        grid_copy = [i for row in self.grid for i in row]
        grid_copy.sort(key=lambda x: x.entropy())

        filtered_grid = list(filter(lambda x: x.entropy() > 1, grid_copy))
        if filtered_grid == []:
            return None

        least_entropy_cell = filtered_grid[0]
        filtered_grid = list(
            filter(lambda x: x.entropy() == least_entropy_cell.entropy(), filtered_grid)
        )

        # return a pick if filtered copy i s not empty
        pick = random.choice(filtered_grid)
        return pick

    # [WAVE FUNCTION COLLAPSE] algorithm
    def collapse(self):
        # pick a random cell using entropy heuristic
        pick = self.heuristic_pick()
        if pick:
            self.grid[pick.x][pick.y].options
            self.grid[pick.x][pick.y].observe()
        else:
            return

        # shallow copy of the gris
        next_grid = copy.copy(self.grid)

        # update the entropy values and superpositions of each cell in the grid
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j].collapsed:
                    next_grid[i][j] = self.grid[i][j]

                else:
                    # cumulative_valid_options will hold the options that will satisfy the "down", "right", "up", "left"
                    # conditions of each cell in the grid. The cumulative_valid_options is computed by,

                    cumulative_valid_options = self.options
                    # check above cell
                    cell_above = self.grid[(i - 1) % self.w][j]
                    valid_options = []  # holds the valid options for the current cell to fit with the above cell
                    # print("cell_above options:", cell_above.options)
                    for option in cell_above.options:
                        valid_options.extend(option.down)
                    cumulative_valid_options = [
                        option
                        for option in cumulative_valid_options
                        if option in valid_options
                    ]

                    # check right cell
                    cell_right = self.grid[i][(j + 1) % self.h]
                    valid_options = []  # holds the valid options for the current cell to fit with the right cell
                    for option in cell_right.options:
                        valid_options.extend(option.left)
                    cumulative_valid_options = [
                        option
                        for option in cumulative_valid_options
                        if option in valid_options
                    ]

                    # check down cell
                    cell_down = self.grid[(i + 1) % self.w][j]
                    valid_options = []  # holds the valid options for the current cell to fit with the down cell
                    for option in cell_down.options:
                        valid_options.extend(option.up)
                    cumulative_valid_options = [
                        option
                        for option in cumulative_valid_options
                        if option in valid_options
                    ]

                    # check left cell
                    cell_left = self.grid[i][(j - 1) % self.h]
                    valid_options = []  # holds the valid options for the current cell to fit with the left cell
                    for option in cell_left.options:
                        valid_options.extend(option.right)
                    cumulative_valid_options = [
                        option
                        for option in cumulative_valid_options
                        if option in valid_options
                    ]

                    # finally assign the cumulative_valid_options options to be the current cells valid options
                    next_grid[i][j].options = cumulative_valid_options
                    next_grid[i][j].update()

        # re-assign the grid value after cell evaluation
        self.grid = copy.copy(next_grid)


def parse_hex_map():
    with open("data/zelda_overworld_map.txt", "r") as file_pointer:
        hex_rows = [row.strip().split(" ") for row in file_pointer]
    # for row in raw_rows:
    #     print(row)
    return hex_rows


def get_tile_options(hex_map):
    tile_options = defaultdict(partial(defaultdict, partial(defaultdict, int)))
    all_hexes = set()
    total_neighbors = 0
    for row_index, row in enumerate(hex_map):
        for column_index, hex in enumerate(row):
            all_hexes.add(hex)
            neighbors = get_neighbors(hex_map, row_index, column_index)
            # print(f"row {row_index}, column {column_index}: {hex}: neighbors:", json.dumps(neighbors, indent=4))
            for direction, other_hexes in neighbors.items():
                for other_hex, times_appearing in other_hexes.items():
                    total_neighbors += 1
                    tile_options[hex][direction][other_hex] += 1
    all_hexes = list(all_hexes)
    all_hexes.sort()
    # print("all_hexes:", all_hexes)
    # print(json.dumps(tile_options, indent=4))
    print(f"Mapped {total_neighbors:,} adjacencies for {len(tile_options)} tiles...")
    return tile_options


def get_neighbors(hex_map, row_index, column_index):
    neighbors = defaultdict(partial(defaultdict, int))

    directional_offsets = (
        ("up", -1, 0),
        ("down", 1, 0),
        ("left", 0, -1),
        ("right", 0, 1),
    )

    max_row = len(hex_map) - 1
    max_column = len(hex_map[0]) - 1

    # print("max_row:", max_row)
    # print("max_column:", max_column)

    for direction, row_offset, column_offset in directional_offsets:
        row = row_index + row_offset
        column = column_index + column_offset

        if row not in range(0, max_row):
            continue

        if column not in range(0, max_column):
            continue

        # print(f"> checking row {row}, column {column}")

        neighbor_hex = hex_map[row][column]
        neighbors[direction][neighbor_hex] += 1

    return neighbors


if __name__ == "__main__":
    main()

    # load_overworld_tiles_from_sheet()
    # parse_hex_map()
