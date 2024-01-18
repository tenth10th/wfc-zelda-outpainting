import itertools

import pygame
from fritter.boundaries import Cancellable
from pygame import Surface
from pygame.font import Font

# fmt: off
TILE_SOLIDITY = [
    0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0,
    0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0,
    1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0,
    1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0,
    1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0,
    1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0,
]
# fmt: on


def load_font() -> Font:
    pygame.font.init()
    return Font(pygame.font.get_default_font(), 16)


def load_tile_images() -> list[Surface]:
    tile_images = []
    for i in range(160):
        # Load overworld_tile_0.png through overworld_tile_159.png
        # From the Zelda Walking Tour: https://github.com/asweigart/nes_zelda_map_data
        img = load_image(f"./data/tiles/overworld_tile_{i}.png")
        tile_images.append(img)
    print(f"Loaded {len(tile_images)} tile images")
    return tile_images


def load_image(path: str, size: int = 30, remove_padding: int = 0) -> Surface:
    surface = pygame.image.load(path).convert_alpha()
    surface = pygame.transform.scale(
        surface, (size - remove_padding, size - remove_padding)
    )
    return surface


def parse_tile_map() -> list[list[int]]:
    int_map = []

    # Also from the Zelda Walking Tour: https://github.com/asweigart/nes_zelda_map_data
    with open("data/zelda_overworld_map.txt", "r") as file_pointer:
        for row in file_pointer:
            hex_row = row.strip().split(" ")
            int_row = [hex_to_int(hex) for hex in hex_row]
            int_map.append(int_row)

    return int_map


def hex_to_int(hex_str: str) -> int:
    return int(hex_str, 16)


def init_display(width: int = 600, height: int = 600) -> Surface:
    return pygame.display.set_mode((width, height))


def render_tileset(display: Surface, tiles: list[Surface], font: Font):
    # Render tiles to pygame surface
    # (simulating zelda_overworld_tiles.png)
    x = 0
    y = 0
    max_width = 30 * 20

    for tile in tiles:
        display.blit(tile, (x, y))
        x += 30
        if x >= max_width:
            y += 30
            x = 0

    render_message(
        display, 'Walking Tour tileset, re-rendered "in engine"', 5, 250, font
    )

    render_message(display, "(space to continue)", 5, 300, font)


def render_tiles_by_solidity(
    display: Surface, tiles: list[Surface], TILE_SOLIDITY: list[int], font: Font
):
    # Render tiles to pygame surface
    # (simulating zelda_overworld_tiles.png)
    x = 0
    y = 0
    max_width = 30 * 20

    for i, tile in enumerate(tiles):
        if TILE_SOLIDITY[i]:
            display.blit(tile, (x, y))
            x += 30
            if x >= max_width:
                y += 30
                x = 0

    render_message(display, "Solid / blocking tiles", 5, 160, font)

    y += 90
    x = 0

    for i, tile in enumerate(tiles):
        if not TILE_SOLIDITY[i]:
            display.blit(tile, (x, y))
            x += 30
            if x >= max_width:
                y += 30
                x = 0

    render_message(display, "Passable / blank tiles", 5, 340, font)

    render_message(display, "(space to continue)", 5, 380, font)


def render_map_quadrant(
    tiles: list[Surface],
    map_data: list[list[int]],
    from_x: int,
    from_y: int,
    display: Surface,
    font: Font,
):
    for y_offset, x_offset in itertools.product(range(20), range(20)):
        tile_id = map_data[from_y + y_offset][from_x + x_offset]
        tile = tiles[tile_id]
        display.blit(tile, (x_offset * 30, y_offset * 30))

    pygame.draw.rect(display, (0, 0, 0), pygame.Rect(0, 0, 390, 70))

    render_message(display, "Overworld Map Render: Scroll with arrow keys!", 5, 5, font)

    render_message(display, "(space to continue)", 5, 35, font)


def render_message(
    display: Surface,
    text: str,
    x: int,
    y: int,
    font: Font,
    r: int = 255,
    g: int = 255,
    b: int = 255,
) -> None:
    message_surface = font.render(text, 1, (r, g, b))
    display.blit(message_surface, (x, y))


from fritter.drivers.sleep import SleepDriver
from fritter.repeat import EverySecond, repeatedly
from fritter.scheduler import SimpleScheduler


def main() -> None:
    display = init_display()
    tiles = load_tile_images()
    overworld_map = parse_tile_map()
    font = load_font()
    loop = True
    x = 0
    y = 0
    max_y = len(overworld_map) - 20
    max_x = len(overworld_map[0]) - 20
    keys = set()

    mode = 1

    scheduler = SimpleScheduler(driver := SleepDriver())

    def go_up() -> None:
        nonlocal y
        y = max(y - 1, 0)

    def go_down() -> None:
        nonlocal y
        y = min(y + 1, max_y)

    def go_left() -> None:
        nonlocal x
        x = max(x - 1, 0)

    def go_right() -> None:
        nonlocal x
        x = min(x + 1, max_x)

    def do_moves(steps: int, stopper: Cancellable) -> None:
        for pressed_key in keys:
            movement[pressed_key]()

    movement = {
        pygame.K_UP: go_up,
        pygame.K_DOWN: go_down,
        pygame.K_LEFT: go_left,
        pygame.K_RIGHT: go_right,
    }

    repeatedly(scheduler, do_moves, EverySecond(1 / 60))

    while loop:
        display.fill((0, 0, 0))

        if mode == 1:
            render_tileset(display, tiles, font)
        elif mode == 2:
            render_tiles_by_solidity(display, tiles, TILE_SOLIDITY, font)
        elif mode == 3:
            render_map_quadrant(tiles, overworld_map, x, y, display, font)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    mode = 1 if mode == 3 else mode + 1
                if event.key in movement:
                    keys.add(event.key)
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    loop = False

            if event.type == pygame.KEYUP:
                if event.key in movement:
                    keys.remove(event.key)

            if event.type == pygame.QUIT:
                loop = False
        driver.block(0)
        pygame.display.flip()

    print("Exiting...")
    exit()


if __name__ == "__main__":
    main()
