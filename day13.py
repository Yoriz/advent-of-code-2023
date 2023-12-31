import copy
import dataclasses
import enum
import typing

TEST_FILENAME = "day13_testdata.txt"
FILENAME = "day13_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    ROCK = "#"
    ASH = "."
    OUT_OF_BOUNDS = "@"


class ReflectionOrientation(enum.Enum):
    VERTICAL = "|"
    HORIZONTAL = "-"


@dataclasses.dataclass
class Location:
    x: int
    y: int


@dataclasses.dataclass
class GridLocation:
    location: Location
    value: str

    @property
    def type(self) -> LocationType:
        match self.value:
            case LocationType.ROCK.value:
                return LocationType.ROCK
            case LocationType.ASH.value:
                return LocationType.ASH
            case LocationType.OUT_OF_BOUNDS.value:
                return LocationType.OUT_OF_BOUNDS
            case _:
                raise ValueError(f"Invalid type: {self.value}")


@dataclasses.dataclass
class Grid:
    grid_locations: list[list[GridLocation]] = dataclasses.field(default_factory=list)

    def yield_row(self, y_index) -> typing.Iterator[GridLocation]:
        for x_index in range(self.max_x_location + 1):
            yield self.grid_locations[y_index][x_index]

    def yield_column(self, x_index) -> typing.Iterator[GridLocation]:
        for y_index in range(self.max_y_location + 1):
            yield self.grid_locations[y_index][x_index]

    def check_for_line_of_reflection(self, index: int, vertical: bool = True) -> bool:
        if vertical:
            maximum = self.max_x_location
            command = self.yield_column
        else:
            maximum = self.max_y_location
            command = self.yield_row
        if index < 0 or index > maximum - 1:
            raise ValueError("Index out of range")
        for index1, index2 in zip(range(index, -1, -1), range(index + 1, maximum + 1)):
            for loc1, loc2 in zip(command(index1), command(index2)):
                if loc1.value != loc2.value:
                    return False

        return True

    def get_vertical_left_columns_of_reflection(self) -> list[int]:
        columns: list[int] = []
        for index in range(0, self.max_x_location):
            reflection = self.check_for_line_of_reflection(index)
            if reflection:
                columns.append(index + 1)

        return columns

    def get_horizontal_above_rows_of_reflection(self) -> list[int]:
        rows: list[int] = []
        for index in range(0, self.max_y_location):
            reflection = self.check_for_line_of_reflection(index, False)
            if reflection:
                rows.append(index + 1)

        return rows

    def yield_smudge_grids(self) -> typing.Iterator[typing.Self]:
        for y_index in range(self.max_y_location + 1):
            for x_index in range(self.max_x_location + 1):
                grid_copy = copy.deepcopy(self)
                grid_location = grid_copy.grid_locations[y_index][x_index]
                old_value = grid_location.value
                new_value = (
                    LocationType.ROCK.value
                    if grid_location.type == LocationType.ASH
                    else LocationType.ASH.value
                )
                grid_copy.grid_locations[y_index][x_index].value = new_value
                yield grid_copy

    @property
    def max_x_location(self) -> int:
        return len(self.grid_locations[0]) - 1

    @property
    def max_y_location(self) -> int:
        return len(self.grid_locations) - 1

    def __str__(self) -> str:
        lines: list[str] = []
        for grid_location_row in self.grid_locations:
            line_str = ""
            for grid_location in grid_location_row:
                line_str = f"{line_str}{grid_location.value}"
            lines.append(line_str)
        return "\n".join(lines)


def create_grid_locations(y_index: int, line: str, grid: Grid):
    grid_locations: list[GridLocation] = []
    for x_index, character in enumerate(line):
        location = Location(x_index, y_index)
        grid_location = GridLocation(location, character)
        grid_locations.append(grid_location)
    return grid_locations


def create_grids(data: typing.Iterator[str]) -> list[Grid]:
    grids: list[Grid] = []
    grid = Grid()
    for y_index, line in enumerate(data):
        if not line:
            grids.append(grid)
            grid = Grid()
            continue
        grid_locations = create_grid_locations(y_index, line, grid)
        grid.grid_locations.append(grid_locations)
    grids.append(grid)
    return grids


def part_one() -> int:
    data = yield_data(FILENAME)
    grids = create_grids(data)
    total = 0
    for grid in grids:
        vertical_reflections = grid.get_vertical_left_columns_of_reflection()
        horizonal_reflections = grid.get_horizontal_above_rows_of_reflection()
        for vertical_reflection in vertical_reflections:
            total += vertical_reflection
        for horizonal_reflection in horizonal_reflections:
            total += horizonal_reflection * 100

    return total


def part_two() -> int:
    data = yield_data(FILENAME)
    grids = create_grids(data)
    total = 0
    for grid in grids:
        vertical_reflections = grid.get_vertical_left_columns_of_reflection()
        horizonal_reflections = grid.get_horizontal_above_rows_of_reflection()
        found_new = False
        for smudge_grid in grid.yield_smudge_grids():
            smudge_vertical_reflections = (
                smudge_grid.get_vertical_left_columns_of_reflection()
            )
            smudge_horizonal_reflections = (
                smudge_grid.get_horizontal_above_rows_of_reflection()
            )
            for vertical_reflection in smudge_vertical_reflections:
                if vertical_reflection not in vertical_reflections:
                    total += vertical_reflection
                    found_new = True
            for horizonal_reflection in smudge_horizonal_reflections:
                if horizonal_reflection not in horizonal_reflections:
                    total += horizonal_reflection * 100
                    found_new = True
            if found_new:
                break

    return total


def main():
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
