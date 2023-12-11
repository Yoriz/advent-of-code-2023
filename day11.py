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


@dataclasses.dataclass(frozen=True)
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
        empty_rows: list[int] = []
        for y_index in range(self.max_y_location + 1):
            galaxy_found = False
            for x_index in range(self.max_x_location + 1):
                location = Location(x_index, y_index)
                grid_location = self.get_grid_location(location)
                if grid_location.type == LocationType.GALAXY:
                    galaxy_found = True
            if not galaxy_found:
                empty_rows.append(y_index)

        return empty_rows

    def find_empty_columns(self) -> list[int]:
        empty_columns: list[int] = []
        for x_index in range(self.max_x_location + 1):
            galaxy_found = False
            for y_index in range(self.max_y_location + 1):
                location = Location(x_index, y_index)
                grid_location = self.get_grid_location(location)
                if grid_location.type == LocationType.GALAXY:
                    galaxy_found = True
            if not galaxy_found:
                empty_columns.append(x_index)

        return empty_columns

    def insert_empty_row(self, after_row_y: int) -> None:
        for y_index in range(self.max_y_location, after_row_y, -1):
            for x_index in range(self.max_x_location + 1):
                location = Location(x_index, y_index)
                grid_location = self.get_grid_location(location)
                if grid_location.type == LocationType.GALAXY:
                    list_index = self.galaxy_locations.index(location)
                    new_location = Location(location.x, location.y + 1)
                    # print(f"Current: {location}, New: {new_location}")
                    self.galaxy_locations[list_index] = new_location
        self.max_y_location += 1

        return None

    def insert_empty_column(self, after_column_x: int) -> None:
        for x_index in range(self.max_x_location, after_column_x, -1):
            for y_index in range(self.max_y_location + 1):
                location = Location(x_index, y_index)
                grid_location = self.get_grid_location(location)
                if grid_location.type == LocationType.GALAXY:
                    list_index = self.galaxy_locations.index(location)
                    new_location = Location(location.x + 1, location.y)
                    # print(f"Current: {location}, New: {new_location}")
                    self.galaxy_locations[list_index] = new_location
        self.max_x_location += 1

        return None

    def expand_galaxy(self) -> None:
        empty_rows = self.find_empty_rows()
        for row in reversed(empty_rows):
            self.insert_empty_row(row)
        empty_columns = self.find_empty_columns()
        for column in reversed(empty_columns):
            self.insert_empty_column(column)

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


def part_one(image: Image) -> int:
    total = 0
    image.expand_galaxy()
    for galaxy1, galaxy2 in itertools.combinations(image.galaxy_locations, 2):
        distance_between = galaxy1.distance_between(galaxy2)
        # galaxy1_index = image.galaxy_locations.index(galaxy1) + 1
        # galaxy2_index = image.galaxy_locations.index(galaxy2) + 1
        # print(f"Between galaxy {galaxy1_index} {galaxy1} and galaxy {galaxy2_index} {galaxy2}: {distance_between}")
        total += distance_between
    return total


def part_two() -> int:
    return 0


def main():
    data = yield_data(FILENAME)
    image = create_image(data)
    print(f"Part one: {part_one(image)}")
    # print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
