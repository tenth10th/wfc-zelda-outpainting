from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from random import Random
from typing import Iterable, MutableMapping, NewType, TypeVar


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
    x: int, y: int, h: int, w: int, grid: list[list[T]]
) -> Iterable[tuple[Direction, T]]:
    for direction, (deltax, deltay) in compass:
        targetx = x + deltax
        targety = y + deltay
        if in_bounds(targetx, targety, h, w):
            yield (direction, grid[targetx][targety])


def weighted_choice(r: Random, x: Iterable[tuple[T, int]]) -> T:
    return r.choices(
        [each for each, weight in x], weights=[weight for each, weight in x]
    )[0]


@dataclass
class GeneratingTile:
    remaining: set[TileId] | None = None
    # None means 'all tiles are valid'

    def observe(
        self,
        r: Random,
        x: int,
        y: int,
        h: int,
        w: int,
        in_progress: GeneratingMap,
        trained: TrainedSet,
    ) -> None:
        if self.remaining is None:
            self.remaining = set(trained.keys())
        probabilities = {each: 1 for each in self.remaining}
        for direction, other_generating_tile in adjacents(x, y, h, w, in_progress):
            reversed = {
                Direction.north: Direction.south,
                Direction.east: Direction.west,
                Direction.south: Direction.north,
                Direction.west: Direction.east,
            }[direction]
            for remaining_tile_id in other_generating_tile.remaining or set(
                trained.keys()
            ):
                neighbors = trained[remaining_tile_id]
                id_to_chance_for_us = neighbors.possibilities[reversed]
                probabilities = {
                    tile_id: (score + id_to_chance_for_us[tile_id].chance)
                    for (tile_id, score) in probabilities.items()
                    if tile_id in id_to_chance_for_us
                }

        chosen = weighted_choice(r, probabilities.items())
        self.remaining = set([chosen])

        for direction, other_generating_tile in adjacents(x, y, h, w, in_progress):
            other_generating_tile.remaining = (
                other_generating_tile.remaining
                if other_generating_tile.remaining is not None
                else set(trained.keys())
            ) & set(trained[chosen].possibilities[direction])


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
