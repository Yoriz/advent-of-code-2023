import dataclasses
import typing
import enum

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
class PartNumber:
    value: int
    start_location: Location


@dataclasses.dataclass
class PartNumberBuilder:
    start_location: typing.Optional[Location] = None
    number: str = ""

    def add_number_part(self, character: str, location: Location):
        self.number = f"{self.number}{character}"
        if not self.start_location:
            self.start_location = location

    def get_part_number(self) -> PartNumber:
        if not self.start_location:
            raise ValueError("Cannot create a PartNumber without a Location")
        partnumber = PartNumber(int(self.number), self.start_location)
        return partnumber

    def reset(self):
        self.start_location = None
        self.number = ""


Grid = list[list[GridLocation]]


@dataclasses.dataclass
class Schematic:
    grid: Grid = dataclasses.field(default_factory=list)
    part_numbers: list[PartNumber] = dataclasses.field(default_factory=list)
    part_number_builder: PartNumberBuilder = dataclasses.field(
        default_factory=PartNumberBuilder
    )

    def add_charecter(self, character: str, location: Location) -> None:
        if character.isdigit():
            self.part_number_builder.add_number_part(character, location)
            return
        if self.part_number_builder.number:
            self.add_builder_number()

    def add_builder_number(self) -> None:
        part_number = self.part_number_builder.get_part_number()
        self.part_numbers.append(part_number)
        self.part_number_builder.reset()


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


def part_one():
    return


def part_two():
    return


def main():
    data = yield_data(TEST_FILENAME)
    schematic = create_schematic(data)
    print(schematic.part_numbers)
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")

""" Current output
[PartNumber(
    value=467, start_location=Location(x=0, y=0)),
    PartNumber(value=114, start_location=Location(x=5, y=0)),
    PartNumber(value=35, start_location=Location(x=2, y=2)),
    PartNumber(value=633, start_location=Location(x=6, y=2)),
    PartNumber(value=617, start_location=Location(x=0, y=4)),
    PartNumber(value=58, start_location=Location(x=7, y=5)),
    PartNumber(value=592, start_location=Location(x=2, y=6)),
    PartNumber(value=755, start_location=Location(x=6, y=7)),
    PartNumber(value=664, start_location=Location(x=1, y=9)),
    PartNumber(value=598, start_location=Location(x=5, y=9))]
Part one: None
Part two: None
"""


if __name__ == "__main__":
    main()
