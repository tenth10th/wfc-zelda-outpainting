from wfc_render import hex_to_int, load_tile_images, init_display
from pytest import fixture


@fixture(scope="module")
def display():
    yield init_display()


def test_hex_to_int():
    assert hex_to_int("00") == 0
    assert hex_to_int("80") == 128
    assert hex_to_int("ff") == 255


def test_load_tile_images(display):
    images = load_tile_images()
    assert len(images) == 160