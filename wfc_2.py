from __future__ import annotations
from typing import NewType, Iterable, MutableMapping, TypeVar

from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict


class Direction(Enum):
    north = auto()
    east = auto()
    south = auto()
    west = auto()


TileId = NewType("TileId", int)


@dataclass
class TileChance:
    chance: int


@dataclass
class PossibleNeighbors:
    id: TileId
    possibilities: MutableMapping[
        Direction, MutableMapping[TileId, TileChance]
    ] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(lambda: TileChance(0)))
    )


compass = (
    (Direction.north, (0, 1)),
    (Direction.east, (1, 0)),
    (Direction.south, (0, -1)),
    (Direction.west, (-1, 0)),
)


def in_bounds(targetx: int, targety: int, h: int, w: int) -> bool:
    return (targetx >= 0) and (targetx < w) and (targety >= 0) and (targety < h)

T = TypeVar("T")
def adjacents(
    x: int, y: int, h: int, w: int, training: list[list[T]]
) -> Iterable[tuple[Direction, T]]:
    for direction, (deltax, deltay) in compass:
        targetx = x + deltax
        targety = y + deltay
        if in_bounds(targetx, targety, h, w):
            yield (direction, training[targetx][targety])

@dataclass
class GeneratingTile:
    remaining: set[TileId] = field(default_factory=set)

    def refine(self, x: int, y: int, in_progress: GeneratingMap) -> None:
        pass

GeneratingMap = list[list[GeneratingTile]]
TrainedSet = MutableMapping[TileId, PossibleNeighbors]

class IdToTileMap(defaultdict):
    def __missing__(self, key: TileId) -> PossibleNeighbors:
        return PossibleNeighbors(key)


def train_on_map(training: list[list[TileId]]) -> TrainedSet:
    assert training, "training data"
    height = len(training)
    width = len(training[0])
    id_to_tile: defaultdict[TileId, PossibleNeighbors] = IdToTileMap()
    for x, row in enumerate(training):
        assert len(row) == width, "uniform widths required"
        for y, cell in enumerate(row):
            for direction, adjacent in adjacents(x, y, height, width, training):
                id_to_tile[cell].possibilities[direction][adjacent].chance += 1
    return id_to_tile
