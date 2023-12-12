import dataclasses
import enum
import itertools
import typing

TEST_FILENAME = "day11_testdata.txt"
FILENAME = "day11_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    GALAXY = "#"
    EMPTY_SPACE = "."
    OUT_OF_BOUNDS = "@"


@dataclasses.dataclass
class Location:
    x: int
    y: int

    def neighbour_location(self, location_direction: "LocationDirection") -> "Location":
        other_location: "Location" = location_direction.value
        return Location(self.x + other_location.x, self.y + other_location.y)

    def distance_between(self, other_location: "Location") -> int:
        return abs(self.x - other_location.x) + abs(self.y - other_location.y)


@enum.unique
class LocationDirection(enum.Enum):
    UP = Location(0, -1)
    UP_RIGHT = Location(1, -1)
    RIGHT = Location(1, 0)
    DOWN_RIGHT = Location(1, 1)
    DOWN = Location(0, 1)
    DOWN_LEFT = Location(-1, 1)
    LEFT = Location(-1, 0)
    UP_LEFT = Location(-1, -1)


@dataclasses.dataclass
class GridLocation:
    location: Location
    value: str

    @property
    def type(self) -> LocationType:
        match self.value:
            case LocationType.GALAXY.value:
                return LocationType.GALAXY
            case LocationType.EMPTY_SPACE.value:
                return LocationType.EMPTY_SPACE
            case LocationType.OUT_OF_BOUNDS.value:
                return LocationType.OUT_OF_BOUNDS
            case _:
                raise ValueError(f"Invalid type: {self.value}")


@dataclasses.dataclass
class Image:
    galaxy_locations: list[Location] = dataclasses.field(default_factory=list)
    max_x_location: int = 0
    max_y_location: int = 0

    def add_grid_location(self, grid_location: GridLocation) -> None:
        match grid_location.type:
            case LocationType.GALAXY:
                self.galaxy_locations.append(grid_location.location)
        self.update_max_values(grid_location.location)

        return None

    def update_max_values(self, location: Location) -> None:
        self.max_x_location = max(self.max_x_location, location.x)
        self.max_y_location = max(self.max_y_location, location.y)

        return None

    def get_grid_location(self, location: Location) -> GridLocation:
        if not self.location_in_grid(location):
            return GridLocation(location, LocationType.OUT_OF_BOUNDS.value)
        if location in self.galaxy_locations:
            return GridLocation(location, LocationType.GALAXY.value)
        return GridLocation(location, LocationType.EMPTY_SPACE.value)

    def find_empty_rows(self) -> list[int]:
        rows_with_galaxys = {location.y for location in self.galaxy_locations}
        empty_rows = []
        for y_index in range(self.max_y_location + 1):
            if y_index not in rows_with_galaxys:
                empty_rows.append(y_index)

        return empty_rows

    def find_empty_columns(self) -> list[int]:
        columns_with_galaxys = {location.x for location in self.galaxy_locations}
        empty_columns = []
        for x_index in range(self.max_x_location + 1):
            if x_index not in columns_with_galaxys:
                empty_columns.append(x_index)

        return empty_columns

    def insert_empty_row(self, after_row_y: int, amount: int = 1) -> None:
        for location in self.galaxy_locations:
            if location.y > after_row_y:
                location.y += amount

        return None

    def insert_empty_column(self, after_column_x: int, amount: int = 1) -> None:
        for location in self.galaxy_locations:
            if location.x > after_column_x:
                location.x += amount

        return None

    def expand_galaxy(self, amount: int = 1) -> None:
        empty_rows = self.find_empty_rows()
        empty_columns = self.find_empty_columns()
        for row in reversed(empty_rows):
            self.insert_empty_row(row, amount)
        for column in reversed(empty_columns):
            self.insert_empty_column(column, amount)

        return None

    def location_in_grid(self, location: Location) -> bool:
        return all(
            (
                location.x > -1,
                location.x < self.max_x_location + 1,
                location.y > -1,
                location.y < self.max_y_location + 1,
            )
        )

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


def create_image(data: typing.Iterator[str]) -> Image:
    image = Image()
    for y_index, line in enumerate(data):
        for x_index, character in enumerate(line):
            location = Location(x_index, y_index)
            grid_location = GridLocation(location, character)
            image.add_grid_location(grid_location)
    return image


def part_one() -> int:
    data = yield_data(FILENAME)
    image = create_image(data)
    total = 0
    image.expand_galaxy()
    for galaxy1, galaxy2 in itertools.combinations(image.galaxy_locations, 2):
        distance_between = galaxy1.distance_between(galaxy2)
        total += distance_between
    return total


def part_two() -> int:
    data = yield_data(FILENAME)
    image = create_image(data)
    total = 0
    image.expand_galaxy(999999)
    for galaxy1, galaxy2 in itertools.combinations(image.galaxy_locations, 2):
        distance_between = galaxy1.distance_between(galaxy2)
        total += distance_between
    return total


def main():
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
