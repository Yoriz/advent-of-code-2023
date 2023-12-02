import dataclasses
import operator
from collections import Counter
from typing import Iterator

TEST_FILENAME = "day2_testdata.txt"
FILENAME = "day2_data.txt"


def yield_data(filename: str) -> Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


@dataclasses.dataclass
class Cubes:
    cube_counts: Counter = dataclasses.field(default_factory=Counter)

    def has_cube_qtys(self, other_cubes: "Cubes") -> bool:
        for name, qty in other_cubes.cube_counts.items():
            if not self.cube_counts[name] <= qty:
                return False
        return True

    def power(self) -> int:
        multiply_by = 1
        for value in self.cube_counts.values():
            multiply_by = operator.mul(multiply_by, value)
        return multiply_by


@dataclasses.dataclass
class Bag:
    cubes: list[Cubes] = dataclasses.field(default_factory=list)

    def maximum_cubes(self) -> Cubes:
        cube_counter = Counter()
        for cubes in self.cubes:
            for name, qty in cubes.cube_counts.items():
                cube_counter[name] = max((qty, cube_counter[name]))

        return Cubes(Counter(cube_counter))

    def has_cube_qtys(self, cubes: Cubes) -> bool:
        maximum_cubes = self.maximum_cubes()
        return maximum_cubes.has_cube_qtys(cubes)


@dataclasses.dataclass
class Game:
    id: int
    bag: Bag

    def game_possible(self, cubes: Cubes) -> bool:
        return self.bag.has_cube_qtys(cubes)


@dataclasses.dataclass
class GameRecords:
    games: list[Game] = dataclasses.field(default_factory=list)


def split_game_records_str(game_record_str: str) -> tuple[str, str]:
    game_id_str, cube_sets_str = game_record_str.split(":")
    return game_id_str, cube_sets_str


def game_id_str_to_number(game_id_str: str) -> int:
    return int(game_id_str[5:])


def cube_set_str_to_cube_dict(cube_set_str: str) -> dict:
    cubes = {}
    for cube_str in cube_set_str.split(","):
        qty, name = cube_str.strip().split(" ")
        cubes[name] = int(qty)

    return cubes


def game_records_str_to_bag(cube_sets_str: str) -> Bag:
    bag = Bag()
    for cube_set_str in cube_sets_str.split(";"):
        cube_dict = cube_set_str_to_cube_dict(cube_set_str.strip())
        cubes = Cubes(Counter(cube_dict))
        bag.cubes.append(cubes)

    return bag


def create_game_records(data: Iterator[str]) -> GameRecords:
    game_records = GameRecords()
    for game_records_str in data:
        game_id_str, cube_sets_str = split_game_records_str(game_records_str)
        game_id = game_id_str_to_number(game_id_str)
        bag = game_records_str_to_bag(cube_sets_str)
        game = Game(game_id, bag)
        game_records.games.append(game)

    return game_records


def part_one():
    data = yield_data(FILENAME)
    game_records = create_game_records(data)
    cubes = Cubes(Counter({"red": 12, "green": 13, "blue": 14}))
    id_sum = 0
    for game in game_records.games:
        if game.game_possible(cubes):
            id_sum += game.id

    return id_sum


def part_two():
    data = yield_data(FILENAME)
    game_records = create_game_records(data)
    power_total = 0
    for game in game_records.games:
        maximum_cubes = game.bag.maximum_cubes()
        power = maximum_cubes.power()
        power_total += power
    return power_total


def main():
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
