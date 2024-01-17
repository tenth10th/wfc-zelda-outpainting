import itertools
import pygame
from pygame import Surface


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
    surface = pygame.transform.scale(surface, (size - remove_padding, size - remove_padding))
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


def render_tileset(display: Surface, tiles: list[Surface]):
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


def render_map_quadrant(tiles: list[Surface], map_data: list[list[int]], from_x: int, from_y: int, display: Surface):
    for y_offset, x_offset in itertools.product(range(20), range(20)):
        tile_id = map_data[from_y + y_offset][from_x + x_offset]
        tile = tiles[tile_id]
        display.blit(tile, (x_offset * 30, y_offset * 30))


def main() -> None:
    display = init_display()
    tiles = load_tile_images()
    overworld_map = parse_tile_map()
    loop = True
    x = 0
    y = 0
    max_y = len(overworld_map)-20
    max_x = len(overworld_map[0])-20

    while loop:
        display.fill((0, 0, 0))

        #render_tileset(display, tiles)
        render_map_quadrant(tiles, overworld_map, x, y, display)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                loop = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    y = max(y-1, 0)
                if event.key == pygame.K_DOWN:
                    y = min(y+1, max_y)
                if event.key == pygame.K_LEFT:
                    x = max(x-1, 0)
                if event.key == pygame.K_RIGHT:
                    x = min(x+1, max_x)

                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    loop = False

        pygame.display.flip()


    print("Exiting...")
    exit()


if __name__ == '__main__':
    main()
