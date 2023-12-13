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

    # def neighbour_location(self, location_direction: "LocationDirection") -> "Location":
    #     other_location: "Location" = location_direction.value
    #     return Location(self.x + other_location.x, self.y + other_location.y)


# @enum.unique
# class LocationDirection(enum.Enum):
#     UP = Location(0, -1)
#     UP_RIGHT = Location(1, -1)
#     RIGHT = Location(1, 0)
#     DOWN_RIGHT = Location(1, 1)
#     DOWN = Location(0, 1)
#     DOWN_LEFT = Location(-1, 1)
#     LEFT = Location(-1, 0)
#     UP_LEFT = Location(-1, -1)


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

    # def get_neighbour_grid_location(
    #     self, grid_location: GridLocation, location_direction: LocationDirection
    # ) -> GridLocation:
    #     neighbour_location = grid_location.location.neighbour_location(
    #         location_direction
    #     )
    #     if not self.location_in_grid(neighbour_location):
    #         return GridLocation(neighbour_location, LocationType.OUT_OF_BOUNDS.value)
    #     neighbour_grid_location = self.grid_locations[neighbour_location.y][
    #         neighbour_location.x
    #     ]
    #     return neighbour_grid_location

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

    # def location_in_grid(self, location: Location) -> bool:
    #     return all(
    #         (
    #             location.x > -1,
    #             location.x < self.max_x_location + 1,
    #             location.y > -1,
    #             location.y < self.max_y_location + 1,
    #         )
    #     )

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
    return 0


def main():
    print(f"Part one: {part_one()}")
    # print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
