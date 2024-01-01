import dataclasses
import enum
import itertools
import typing
import operator


TEST_FILENAME = "day18_testdata.txt"
FILENAME = "day18_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    TRENCH = "#"
    INTERIOR_TRENCH = "O"
    GROUND_LEVEL = "."
    # OUT_OF_BOUNDS = enum.auto()


@dataclasses.dataclass(slots=True, frozen=True)
class Location:
    x: int
    y: int

    def neighbour_location(
        self, location_direction: "LocationDirection", length: int = 1
    ) -> "Location":
        other: "Location" = location_direction.value
        return Location(self.x + (other.x * length), self.y + (other.y * length))


@enum.unique
class LocationDirection(enum.Enum):
    UP = Location(0, -1)
    RIGHT = Location(1, 0)
    DOWN = Location(0, 1)
    LEFT = Location(-1, 0)

    @classmethod
    def convertor(cls, string: str) -> "LocationDirection":
        convertion = {
            location_direction.name[0]: location_direction
            for location_direction in LocationDirection
        }
        return convertion[string]


@enum.unique
class GridCornerType(enum.Enum):
    RIGHT_UP = (LocationDirection.RIGHT, LocationDirection.UP)
    RIGHT_DOWN = (LocationDirection.RIGHT, LocationDirection.DOWN)
    LEFT_UP = (LocationDirection.LEFT, LocationDirection.UP)
    LEFT_DOWN = (LocationDirection.LEFT, LocationDirection.DOWN)
    NOT_CORNER = ()

    @classmethod
    def possible_type(
        cls, current_location: Location, grid: "Grid"
    ) -> "GridCornerType":
        for grid_corner_type in GridCornerType:
            if grid_corner_type == GridCornerType.NOT_CORNER:
                continue
            matches: list[bool] = []
            for location_direction in grid_corner_type.value:
                location = current_location.neighbour_location(location_direction)
                grid_location = grid.get_grid_location(location)
                matches.append(grid_location.type == LocationType.TRENCH)
            if all(matches):
                return grid_corner_type

        return GridCornerType.NOT_CORNER


@dataclasses.dataclass(slots=True, frozen=True)
class GridLocation:
    location: Location
    type: LocationType

    @property
    def value(self) -> str:
        return self.type.value


@dataclasses.dataclass(slots=True, frozen=True)
class Trench:
    start_location: Location
    location_direction: LocationDirection
    length: int

    def x_inside(self, x: int) -> bool:
        return self.min_x <= x <= self.max_x

    def y_inside(self, y: int) -> bool:
        return self.min_y <= y <= self.max_y

    def is_location_in_trench(self, location: Location) -> bool:
        return all((self.x_inside(location.x), self.y_inside(location.y)))

    @property
    def end_location(self) -> Location:
        neighbour_location = self.start_location.neighbour_location(
            self.location_direction, self.length - 1
        )
        return neighbour_location

    @property
    def min_x(self) -> int:
        return min(self.start_location.x, self.end_location.x)

    @property
    def min_y(self) -> int:
        return min(self.start_location.y, self.end_location.y)

    @property
    def max_x(self) -> int:
        return max(self.start_location.x, self.end_location.x)

    @property
    def max_y(self) -> int:
        return max(self.start_location.y, self.end_location.y)

    @property
    def is_horizontal(self) -> bool:
        return self.location_direction in (
            LocationDirection.LEFT,
            LocationDirection.RIGHT,
        )

    @property
    def is_vertical(self) -> bool:
        return self.location_direction in (LocationDirection.UP, LocationDirection.DOWN)


@dataclasses.dataclass
class Grid:
    trenches: list[Trench] = dataclasses.field(default_factory=list)
    interior_trenches: list[Trench] = dataclasses.field(default_factory=list)
    min_x_location: int = 0
    min_y_location: int = 0
    max_x_location: int = 0
    max_y_location: int = 0

    def add_trench(self, trench: Trench) -> None:
        self.trenches.append(trench)
        self.update_min_max_x_y(trench)
        return None

    def update_min_max_x_y(self, trench: Trench) -> None:
        self.min_x_location = min(self.min_x_location, trench.min_x)
        self.min_y_location = min(self.min_y_location, trench.min_y)
        self.max_x_location = max(self.max_x_location, trench.max_x)
        self.max_y_location = max(self.max_y_location, trench.max_y)

    def get_grid_location(self, location: Location) -> GridLocation:
        for trench in self.trenches:
            if trench.is_location_in_trench(location):
                return GridLocation(location, LocationType.TRENCH)

        for interior_trench in self.interior_trenches:
            if interior_trench.is_location_in_trench(location):
                return GridLocation(location, LocationType.INTERIOR_TRENCH)

        return GridLocation(location, LocationType.GROUND_LEVEL)

    def get_row_horizontal_trenches(self, y: int) -> list[Trench]:
        trenches = [trench for trench in self.trenches if trench.y_inside(y)]
        trenches.sort(key=operator.attrgetter("min_x"))
        row_trenches: list[Trench] = []
        first_trench = trenches[0]
        new_trench_x_start = first_trench.min_x
        new_trench_length = first_trench.max_x - first_trench.min_x + 1
        for trench in trenches[1:]:
            if new_trench_x_start + new_trench_length == trench.min_x:
                new_trench_length += trench.max_x - trench.min_x + 1
            else:
                location = Location(new_trench_x_start, y)
                new_trench = Trench(
                    location, LocationDirection.RIGHT, new_trench_length
                )
                row_trenches.append(new_trench)
                new_trench_x_start = trench.min_x
                new_trench_length = trench.max_x - trench.min_x + 1

        location = Location(new_trench_x_start, y)
        new_trench = Trench(location, LocationDirection.RIGHT, new_trench_length)
        row_trenches.append(new_trench)
        return row_trenches

    def fill_interior_trenches_row(self, y: int) -> None:
        inside_trench = False
        trenches = self.get_row_horizontal_trenches(y)
        for trench, other in itertools.pairwise(trenches):
            trench_start_corner, trench_end_corner = self.trench_possible_corner_types(
                trench
            )
            match (trench_start_corner, trench_end_corner):
                case (GridCornerType.NOT_CORNER, GridCornerType.NOT_CORNER):
                    inside_trench = not inside_trench
                case (GridCornerType.RIGHT_UP, GridCornerType.LEFT_DOWN):
                    inside_trench = not inside_trench
                case (GridCornerType.RIGHT_DOWN, GridCornerType.LEFT_UP):
                    inside_trench = not inside_trench
            if inside_trench:
                location = Location(trench.max_x + 1, y)
                length = other.min_x - trench.max_x - 1
                interior_trench = Trench(location, LocationDirection.RIGHT, length)
                self.interior_trenches.append(interior_trench)

        return None

    def fill_all_interior_trenches(self) -> None:
        for y in range(self.min_y_location, self.max_y_location + 1):
            print(f"Filling trench row: {y} - {self.max_y_location}")
            self.fill_interior_trenches_row(y)

        return None

    def trench_possible_corner_types(
        self, trench
    ) -> tuple[GridCornerType, GridCornerType]:
        trench_start_location = trench.start_location
        trench_start_corner = GridCornerType.possible_type(trench_start_location, self)
        trench_end_location = trench.end_location
        trench_end_corner = GridCornerType.possible_type(trench_end_location, self)
        return trench_start_corner, trench_end_corner

    @property
    def trench_cubic_meters(self) -> int:
        total = 0
        for trench in self.trenches:
            total += trench.length

        for interior_trenche in self.interior_trenches:
            total += interior_trenche.length

        return total

    def __str__(self) -> str:
        rows: list[str] = []
        for y_index in range(self.max_y_location + 1):
            row = ""
            for x_index in range(self.max_x_location + 1):
                location = Location(x_index, y_index)
                grid_location = self.get_grid_location(location)
                row = f"{row}{grid_location.value}"
            rows.append(row)
        return "\n".join(rows)


def create_grid(data: typing.Iterator) -> Grid:
    grid = Grid()
    start_location = Location(0, 0)
    for line in data:
        direction_str, length_str, _ = line.split(" ")
        location_direction = LocationDirection.convertor(direction_str)
        length = int(length_str)
        start_location = start_location.neighbour_location(location_direction)
        trench = Trench(start_location, location_direction, length)
        grid.add_trench(trench)
        start_location = trench.end_location

    return grid


def part_one() -> int:
    data = yield_data(FILENAME)
    grid = create_grid(data)
    grid.fill_all_interior_trenches()
    total = grid.trench_cubic_meters
    # print(grid)

    return total


def part_two() -> int:
    return 0


def main():
    # data = yield_data(FILENAME)
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
