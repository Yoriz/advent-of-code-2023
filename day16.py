import dataclasses
import enum
import typing

TEST_FILENAME = "day16_testdata.txt"
FILENAME = "day16_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    MIRROR_LEANING_FORWARD = "/"
    MIRROR_LEANING_BACKWARDS = "\\"
    SPLITTER_VERTICAL = "|"
    SPLITTER_HORIZONTAL = "-"
    EMPTY_SPACE = "."
    OUT_OF_BOUNDS = "@"


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
    RIGHT = Location(1, 0)
    DOWN = Location(0, 1)
    LEFT = Location(-1, 0)


class GridLocationProtocol(typing.Protocol):
    location: Location

    @property
    def value(self) -> str:
        ...

    @property
    def type(self) -> LocationType:
        ...

    @property
    def x(self) -> int:
        ...

    @property
    def y(self) -> int:
        ...

    @property
    def entrance_directions(self) -> tuple[LocationDirection, ...]:
        ...

    def entrance_to_exit_directions(
        self, entrance_direction: LocationDirection
    ) -> tuple[LocationDirection, ...]:
        ...


@dataclasses.dataclass
class OutOfBoundsGridLocation:
    location: Location

    @property
    def value(self) -> str:
        return self.type.value

    @property
    def type(self) -> LocationType:
        return LocationType.OUT_OF_BOUNDS

    @property
    def x(self) -> int:
        return self.location.x

    @property
    def y(self) -> int:
        return self.location.y

    @property
    def entrance_directions(self) -> tuple[LocationDirection, ...]:
        return tuple()

    def entrance_to_exit_directions(
        self, entrance_direction: LocationDirection
    ) -> tuple[LocationDirection, ...]:
        return tuple()


@dataclasses.dataclass
class EmptySpaceGridLocation:
    location: Location

    @property
    def value(self) -> str:
        return self.type.value

    @property
    def type(self) -> LocationType:
        return LocationType.EMPTY_SPACE

    @property
    def x(self) -> int:
        return self.location.x

    @property
    def y(self) -> int:
        return self.location.y

    @property
    def entrance_directions(self) -> tuple[LocationDirection, ...]:
        return (
            LocationDirection.UP,
            LocationDirection.RIGHT,
            LocationDirection.DOWN,
            LocationDirection.LEFT,
        )

    def entrance_to_exit_directions(
        self, entrance_direction: LocationDirection
    ) -> tuple[LocationDirection, ...]:
        return (entrance_direction,)


@dataclasses.dataclass
class MirrorLeaningForwardGridLocation:
    location: Location

    @property
    def value(self) -> str:
        return self.type.value

    @property
    def type(self) -> LocationType:
        return LocationType.MIRROR_LEANING_FORWARD

    @property
    def x(self) -> int:
        return self.location.x

    @property
    def y(self) -> int:
        return self.location.y

    @property
    def entrance_directions(self) -> tuple[LocationDirection, ...]:
        return (
            LocationDirection.UP,
            LocationDirection.RIGHT,
            LocationDirection.DOWN,
            LocationDirection.LEFT,
        )

    def entrance_to_exit_directions(
        self, entrance_direction: LocationDirection
    ) -> tuple[LocationDirection, ...]:
        match entrance_direction:
            case LocationDirection.UP:
                return (LocationDirection.RIGHT,)
            case LocationDirection.RIGHT:
                return (LocationDirection.UP,)
            case LocationDirection.DOWN:
                return (LocationDirection.LEFT,)
            case LocationDirection.LEFT:
                return (LocationDirection.DOWN,)
            case _:
                raise ValueError(f"Invalid type: {entrance_direction}")


@dataclasses.dataclass
class MirrorLeaningBackwardGridLocation:
    location: Location

    @property
    def value(self) -> str:
        return self.type.value

    @property
    def type(self) -> LocationType:
        return LocationType.MIRROR_LEANING_BACKWARDS

    @property
    def x(self) -> int:
        return self.location.x

    @property
    def y(self) -> int:
        return self.location.y

    @property
    def entrance_directions(self) -> tuple[LocationDirection, ...]:
        return (
            LocationDirection.UP,
            LocationDirection.RIGHT,
            LocationDirection.DOWN,
            LocationDirection.LEFT,
        )

    def entrance_to_exit_directions(
        self, entrance_direction: LocationDirection
    ) -> tuple[LocationDirection, ...]:
        match entrance_direction:
            case LocationDirection.UP:
                return (LocationDirection.LEFT,)
            case LocationDirection.RIGHT:
                return (LocationDirection.DOWN,)
            case LocationDirection.DOWN:
                return (LocationDirection.RIGHT,)
            case LocationDirection.LEFT:
                return (LocationDirection.UP,)
            case _:
                raise ValueError(f"Invalid type: {entrance_direction}")


@dataclasses.dataclass
class SplitterVeticalGridLocation:
    location: Location

    @property
    def value(self) -> str:
        return self.type.value

    @property
    def type(self) -> LocationType:
        return LocationType.SPLITTER_VERTICAL

    @property
    def x(self) -> int:
        return self.location.x

    @property
    def y(self) -> int:
        return self.location.y

    @property
    def entrance_directions(self) -> tuple[LocationDirection, ...]:
        return (
            LocationDirection.UP,
            LocationDirection.RIGHT,
            LocationDirection.DOWN,
            LocationDirection.LEFT,
        )

    def entrance_to_exit_directions(
        self, entrance_direction: LocationDirection
    ) -> tuple[LocationDirection, ...]:
        match entrance_direction:
            case LocationDirection.UP:
                return (LocationDirection.UP,)
            case LocationDirection.RIGHT:
                return (LocationDirection.UP, LocationDirection.DOWN)
            case LocationDirection.DOWN:
                return (LocationDirection.DOWN,)
            case LocationDirection.LEFT:
                return (LocationDirection.UP, LocationDirection.DOWN)
            case _:
                raise ValueError(f"Invalid type: {entrance_direction}")


@dataclasses.dataclass
class SplitterHorizontalGridLocation:
    location: Location

    @property
    def value(self) -> str:
        return self.type.value

    @property
    def type(self) -> LocationType:
        return LocationType.SPLITTER_HORIZONTAL

    @property
    def x(self) -> int:
        return self.location.x

    @property
    def y(self) -> int:
        return self.location.y

    @property
    def entrance_directions(self) -> tuple[LocationDirection, ...]:
        return (
            LocationDirection.UP,
            LocationDirection.RIGHT,
            LocationDirection.DOWN,
            LocationDirection.LEFT,
        )

    def entrance_to_exit_directions(
        self, entrance_direction: LocationDirection
    ) -> tuple[LocationDirection, ...]:
        match entrance_direction:
            case LocationDirection.UP:
                return (LocationDirection.RIGHT, LocationDirection.LEFT)
            case LocationDirection.RIGHT:
                return (LocationDirection.RIGHT,)
            case LocationDirection.DOWN:
                return (LocationDirection.RIGHT, LocationDirection.LEFT)
            case LocationDirection.LEFT:
                return (LocationDirection.LEFT,)
            case _:
                raise ValueError(f"Invalid type: {entrance_direction}")


def grid_location_creator(character: str) -> typing.Type[GridLocationProtocol]:
    grid_location = {
        "/": MirrorLeaningForwardGridLocation,
        "\\": MirrorLeaningBackwardGridLocation,
        "|": SplitterVeticalGridLocation,
        "-": SplitterHorizontalGridLocation,
        ".": EmptySpaceGridLocation,
    }.get(character)
    if not grid_location:
        raise ValueError(f"No matching GridLocation for character: {character}")
    return grid_location


# @dataclasses.dataclass(frozen=True)
@dataclasses.dataclass
class LightBeam:
    location: Location
    travelled_direction: LocationDirection

    def get_exit_light_beams(self, contraption: "Contraption") -> list["LightBeam"]:
        exit_light_beams: list[LightBeam] = []
        grid_location = contraption.get_grid_location(self.location)
        for exit_direction in grid_location.entrance_to_exit_directions(
            self.travelled_direction
        ):
            neighbour_location = self.location.neighbour_location(exit_direction)
            exit_light_beam = LightBeam(neighbour_location, exit_direction)
            exit_light_beams.append(exit_light_beam)

        return exit_light_beams

    def __hash__(self) -> int:
        return hash((self.location.x, self.location.y, self.travelled_direction))


@dataclasses.dataclass
class Contraption:
    light_beams: list[LightBeam] = dataclasses.field(default_factory=list)
    grid_locations: dict[tuple[int, int], GridLocationProtocol] = dataclasses.field(
        default_factory=dict
    )
    energised_locations: list[Location] = dataclasses.field(default_factory=list)
    light_beam_moves: set[LightBeam] = dataclasses.field(default_factory=set)
    max_x_location: int = 0
    max_y_location: int = 0

    def add_grid_location(self, grid_location: GridLocationProtocol) -> None:
        match grid_location.type:
            case (
                LocationType.MIRROR_LEANING_FORWARD
                | LocationType.MIRROR_LEANING_BACKWARDS
                | LocationType.SPLITTER_VERTICAL
                | LocationType.SPLITTER_HORIZONTAL
            ):
                self.grid_locations[(grid_location.x, grid_location.y)] = grid_location
        self.update_max_values(grid_location.location)

        return None

    def update_max_values(self, location: Location) -> None:
        self.max_x_location = max(self.max_x_location, location.x)
        self.max_y_location = max(self.max_y_location, location.y)

    def get_grid_location(self, location: Location) -> GridLocationProtocol:
        if not self.location_in_grid(location):
            return OutOfBoundsGridLocation(location)
        return self.grid_locations.get(
            (location.x, location.y), EmptySpaceGridLocation(location)
        )

    def get_neighbour_grid_location(
        self, grid_location: GridLocationProtocol, location_direction: LocationDirection
    ) -> GridLocationProtocol:
        neighbour_location = grid_location.location.neighbour_location(
            location_direction
        )
        neighbour_grid_location = self.grid_locations[
            (neighbour_location.y, neighbour_location.x)
        ]
        return neighbour_grid_location

    def move_light_beams(self) -> None:
        new_light_beams: list[LightBeam] = []
        for light_beam in self.light_beams:
            for exit_light_beam in light_beam.get_exit_light_beams(self):
                grid_location = self.get_grid_location(exit_light_beam.location)
                if (
                    exit_light_beam.travelled_direction
                    in grid_location.entrance_directions
                ):
                    if exit_light_beam in self.light_beam_moves:
                        continue
                    new_light_beams.append(exit_light_beam)
                    self.light_beam_moves.add(exit_light_beam)
                    if not exit_light_beam.location in self.energised_locations:
                        self.energised_locations.append(exit_light_beam.location)
        self.light_beams = new_light_beams

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

    def energized_output(self) -> str:
        rows: list[str] = []
        for y_index in range(self.max_y_location + 1):
            row = ""
            for x_index in range(self.max_x_location + 1):
                location = Location(x_index, y_index)
                grid_location_value = (
                    "#" if location in self.energised_locations else "."
                )
                row = f"{row}{grid_location_value}"
            rows.append(row)
        return "\n".join(rows)

    @property
    def energised_locations_total(self) -> int:
        return len(self.energised_locations)


def create_contraption(data: typing.Iterator[str]) -> Contraption:
    contraption = Contraption()
    for y_index, line in enumerate(data):
        for x_index, character in enumerate(line):
            location = Location(x_index, y_index)
            grid_location_class = grid_location_creator(character)
            grid_location = grid_location_class(location)
            contraption.add_grid_location(grid_location)
    return contraption


def part_one() -> int:
    data = yield_data(FILENAME)
    contraption = create_contraption(data)
    light_beam = LightBeam(Location(0, 0), LocationDirection.RIGHT)
    contraption.light_beams.append(light_beam)
    contraption.energised_locations.append(light_beam.location)
    while True:
        contraption.move_light_beams()
        if not contraption.light_beams:
            break

    total = contraption.energised_locations_total
    return total


def part_two() -> int:
    return 0


def main():
    print(f"Part one: {part_one()}")
    # print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
