import dataclasses
import enum
import typing

TEST_FILENAME = "day3_testdata.txt"
FILENAME = "day3_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


DIGITS = "0123456789"
BLANK = "."
symbols = ""


class LocationType(enum.Enum):
    DIGIT = 0
    SYMBOL = 1
    BLANK = 3
    OUT_OF_BOUNDS = 4


@dataclasses.dataclass
class Location:
    x: int
    y: int

    def neighbour_location(self, location_direction: "LocationDirection") -> "Location":
        other_location: "Location" = location_direction.value
        return Location(self.x + other_location.x, self.y + other_location.y)


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
        if self.value == BLANK:
            return LocationType.BLANK
        elif self.value in DIGITS:
            return LocationType.DIGIT
        return LocationType.SYMBOL


@dataclasses.dataclass
class Number:
    value: int
    start_location: Location

    def length(self) -> int:
        return len(str(self.value))

    def neighbour_locations(self) -> list[Location]:
        current_location = self.start_location
        locations: list[Location] = []

        for location in (
            LocationDirection.DOWN_LEFT,
            LocationDirection.LEFT,
            LocationDirection.UP_LEFT,
        ):
            locations.append(current_location.neighbour_location(location))

        for _ in range(self.length() - 1):
            current_location = current_location.neighbour_location(
                LocationDirection.RIGHT
            )
            for location in (LocationDirection.UP_LEFT, LocationDirection.DOWN_LEFT):
                locations.append(current_location.neighbour_location(location))

        for location in (
            LocationDirection.UP,
            LocationDirection.UP_RIGHT,
            LocationDirection.RIGHT,
            LocationDirection.DOWN_RIGHT,
            LocationDirection.DOWN,
        ):
            locations.append(current_location.neighbour_location(location))

        return locations


@dataclasses.dataclass
class NumberBuilder:
    start_location: typing.Optional[Location] = None
    number: str = ""

    def add_number_part(self, character: str, location: Location):
        self.number = f"{self.number}{character}"
        if not self.start_location:
            self.start_location = location

    def get_number(self) -> Number:
        if not self.start_location:
            raise ValueError("Cannot create a Number without a Location")
        number = Number(int(self.number), self.start_location)
        return number

    def reset(self):
        self.start_location = None
        self.number = ""


Grid = list[list[GridLocation]]


@dataclasses.dataclass
class Schematic:
    grid: Grid = dataclasses.field(default_factory=list)
    numbers: list[Number] = dataclasses.field(default_factory=list)
    number_builder: NumberBuilder = dataclasses.field(default_factory=NumberBuilder)

    def add_charecter(self, character: str, location: Location) -> None:
        if character.isdigit():
            self.number_builder.add_number_part(character, location)
            return
        if self.number_builder.number:
            self.add_builder_number()

    def add_builder_number(self) -> None:
        part_number = self.number_builder.get_number()
        self.numbers.append(part_number)
        self.number_builder.reset()

    def is_number_a_partnumber(self, number: Number) -> bool:
        for location in number.neighbour_locations():
            if not self.location_in_grid(location):
                continue
            grid_location = self.grid[location.y][location.x]
            if grid_location.type == LocationType.SYMBOL:
                return True
        return False

    def part_number_sum(self) -> int:
        total = 0
        for number in self.numbers:
            if self.is_number_a_partnumber(number):
                total += number.value

        return total

    def location_in_grid(self, location: Location) -> bool:
        return all(
            (
                location.x > -1,
                location.x < self.max_x_location + 1,
                location.y > -1,
                location.y < self.max_y_location + 1,
            )
        )

    @property
    def max_x_location(self) -> int:
        return len(self.grid[0]) - 1

    @property
    def max_y_location(self) -> int:
        return len(self.grid) - 1


def create_grid_locations(y_index: int, line: str, schematic: Schematic):
    grid_locations: list[GridLocation] = []
    for x_index, character in enumerate(line):
        location = Location(x_index, y_index)
        grid_location = GridLocation(location, character)
        schematic.add_charecter(character, location)
        grid_locations.append(grid_location)
    return grid_locations


def create_schematic(data: typing.Iterator[str]) -> Schematic:
    schematic = Schematic()
    for y_index, line in enumerate(data):
        grid_locations = create_grid_locations(y_index, line, schematic)
        schematic.grid.append(grid_locations)
    return schematic


def part_one(schematic: Schematic) -> int:
    return schematic.part_number_sum()


def part_two():
    return


def main():
    data = yield_data(FILENAME)
    schematic = create_schematic(data)

    print(f"Part one: {part_one(schematic)}")
    # print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
