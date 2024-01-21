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
    """
    A L{PossibleNeighbors} represents the possible neighbors of the tile
    identified by C{id}, in each direction.
    """

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


def in_bounds(targetx: int, targety: int, w: int, h: int) -> bool:
    return (targetx >= 0) and (targetx < w) and (targety >= 0) and (targety < h)


T = TypeVar("T")


def adjacents(
    x: int, y: int, w: int, h: int, grid: list[list[T]]
) -> Iterable[tuple[Direction, T]]:
    for direction, (deltax, deltay) in compass:
        targetx = x + deltax
        targety = y + deltay
        if in_bounds(targetx, targety, w, h):
            yield (direction, grid[targety][targetx])


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
        w: int,
        h: int,
        in_progress: GeneratingMap,
        trained: TrainedSet,
    ) -> TileId:
        if self.remaining is None:
            self.remaining = set(trained.keys())
        if len(self.remaining) == 1:
            return next(iter(self.remaining))
        probabilities = {each: 1 for each in self.remaining}
        for direction, other_generating_tile in adjacents(x, y, w, h, in_progress):
            reversed = {
                Direction.north: Direction.south,
                Direction.east: Direction.west,
                Direction.south: Direction.north,
                Direction.west: Direction.east,
            }[direction]
            options_for_other_tile = other_generating_tile.remaining or set(
                trained.keys()
            )
            unseen = set(probabilities.keys())
            for other_tile_option in options_for_other_tile:
                for possible_tile, possible_chance in (
                    trained[other_tile_option].possibilities[reversed].items()
                ):
                    if possible_tile in probabilities:
                        probabilities[possible_tile] += possible_chance.chance
                        if possible_tile in unseen:
                            unseen.remove(possible_tile)
            for still_unseen in unseen:
                del probabilities[still_unseen]

        if not probabilities:
            return TileId(99)

        chosen = weighted_choice(r, probabilities.items())
        self.remaining = set([chosen])

        for direction, other_generating_tile in adjacents(x, y, w, h, in_progress):
            other_generating_tile.remaining = (
                other_generating_tile.remaining
                if other_generating_tile.remaining is not None
                else set(trained.keys())
            ) & set(trained[chosen].possibilities[direction])
        return chosen


GeneratingMap = list[list[GeneratingTile]]
GeneratedMap = list[list[TileId]]
TrainedSet = MutableMapping[TileId, PossibleNeighbors]


class IdToTileMap(defaultdict):
    def __missing__(self, key: TileId) -> PossibleNeighbors:
        result = self[key] = PossibleNeighbors(key)
        return result


def train_on_map(training: list[list[TileId]]) -> TrainedSet:
    assert training, "training data"
    width = len(training[0])
    height = len(training)
    id_to_tile: defaultdict[TileId, PossibleNeighbors] = IdToTileMap()
    for y, row in enumerate(training):
        assert len(row) == width, "uniform widths required"
        for x, cell in enumerate(row):
            for direction, adjacent in adjacents(x, y, width, height, training):
                id_to_tile[cell].possibilities[direction][adjacent].chance += 1
    return id_to_tile


@dataclass
class MapGenerator:
    width: int
    height: int
    output: GeneratedMap
    trained: TrainedSet
    progress: GeneratingMap
    ungenerated: list[tuple[int, int]]
    random: Random

    @classmethod
    def new(
        cls,
        random: Random,
        output: GeneratedMap,
        trained: TrainedSet,
        progress: GeneratingMap,
    ) -> MapGenerator:
        width = len(output[0])
        height = len(output)
        ungenerated = [
            (x, height - (y + 1)) for y in range(height) for x in range(width)
        ]
        # random.shuffle(ungenerated)
        return MapGenerator(
            width, height, output, trained, progress, ungenerated, random
        )

    def step(self) -> None:
        if not self.ungenerated:
            return
        x, y = self.ungenerated.pop()
        self.output[y][x] = self.progress[y][x].observe(
            self.random, x, y, self.width, self.height, self.progress, self.trained
        )
