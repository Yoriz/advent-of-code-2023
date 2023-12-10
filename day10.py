import dataclasses
import enum
import typing

TEST_FILENAME = "day10_testdata.txt"
FILENAME = "day10_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    VETICAL_PIPE = "|"
    HORIZONTAL_PIPE = "-"
    NE_PIPE = "L"
    NW_PIPE = "J"
    SW_PIPE = "7"
    SE_PIPE = "F"
    GROUND = "."
    STARTING_POSITION = "S"
    OUT_OF_BOUNDS = "@"


PIPES = (
    LocationType.VETICAL_PIPE,
    LocationType.HORIZONTAL_PIPE,
    LocationType.NE_PIPE,
    LocationType.NW_PIPE,
    LocationType.SW_PIPE,
    LocationType.SE_PIPE,
)


@dataclasses.dataclass(frozen=True)
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


LOCATION_CONNECTIONS = (
    (LocationDirection.UP, LocationDirection.DOWN),
    (LocationDirection.LEFT, LocationDirection.RIGHT),
)

PIPE_LOCATION_DIRECTIONS: dict[LocationType, tuple[LocationDirection, ...]] = {
    LocationType.VETICAL_PIPE: (LocationDirection.UP, LocationDirection.DOWN),
    LocationType.HORIZONTAL_PIPE: (LocationDirection.LEFT, LocationDirection.RIGHT),
    LocationType.NE_PIPE: (LocationDirection.UP, LocationDirection.RIGHT),
    LocationType.NW_PIPE: (LocationDirection.UP, LocationDirection.LEFT),
    LocationType.SW_PIPE: (LocationDirection.DOWN, LocationDirection.LEFT),
    LocationType.SE_PIPE: (LocationDirection.DOWN, LocationDirection.RIGHT),
}


@dataclasses.dataclass
class GridLocation:
    location: Location
    value: str

    @property
    def type(self) -> LocationType:
        match self.value:
            case LocationType.VETICAL_PIPE.value:
                return LocationType.VETICAL_PIPE
            case LocationType.HORIZONTAL_PIPE.value:
                return LocationType.HORIZONTAL_PIPE
            case LocationType.NE_PIPE.value:
                return LocationType.NE_PIPE
            case LocationType.NW_PIPE.value:
                return LocationType.NW_PIPE
            case LocationType.SW_PIPE.value:
                return LocationType.SW_PIPE
            case LocationType.SE_PIPE.value:
                return LocationType.SE_PIPE
            case LocationType.GROUND.value:
                return LocationType.GROUND
            case LocationType.STARTING_POSITION.value:
                return LocationType.STARTING_POSITION
            case LocationType.OUT_OF_BOUNDS.value:
                return LocationType.OUT_OF_BOUNDS
            case _:
                raise ValueError(f"Invalid type: {self.value}")


Grid = list[list[GridLocation]]


@dataclasses.dataclass
class PipeMaze:
    grid: Grid = dataclasses.field(default_factory=list)
    starting_grid_location: GridLocation | None = None

    def get_neighbour_grid_location(
        self, grid_location: GridLocation, location_direction: LocationDirection
    ) -> GridLocation:
        neighbour_location = grid_location.location.neighbour_location(
            location_direction
        )
        if not self.location_in_grid(neighbour_location):
            return GridLocation(neighbour_location, LocationType.OUT_OF_BOUNDS.value)
        neighbour_grid_location = self.grid[neighbour_location.y][neighbour_location.x]
        return neighbour_grid_location

    def possible_starting_location_directions(self) -> list[LocationDirection]:
        location_directions: list[LocationDirection] = []
        if not self.starting_grid_location:
            raise ValueError("PipeMaze has no starting grid location")
        for location_direction in (
            LocationDirection.UP,
            LocationDirection.RIGHT,
            LocationDirection.DOWN,
            LocationDirection.LEFT,
        ):
            neighbour_grid_location = self.get_neighbour_grid_location(
                self.starting_grid_location, location_direction
            )
            if neighbour_grid_location.type not in PIPES:
                continue
            pipe_location_directions = PIPE_LOCATION_DIRECTIONS[
                neighbour_grid_location.type
            ]
            for location_connection in LOCATION_CONNECTIONS:
                if (
                    location_direction == location_connection[0]
                    and location_connection[1] in pipe_location_directions
                    or location_direction == location_connection[1]
                    and location_connection[0] in pipe_location_directions
                ):
                    location_directions.append(location_direction)
        return location_directions

    def pipe_move_location_direction(
        self,
        grid_location: GridLocation,
        previous_location_direction: LocationDirection,
    ) -> LocationDirection:
        pipe_location_directions = PIPE_LOCATION_DIRECTIONS[grid_location.type]
        blocked_location_direction = None
        for location_connection in LOCATION_CONNECTIONS:
            if previous_location_direction == location_connection[0]:
                blocked_location_direction = location_connection[1]
            elif previous_location_direction == location_connection[1]:
                blocked_location_direction = location_connection[0]
        for pipe_location_direction in pipe_location_directions:
            if pipe_location_direction == blocked_location_direction:
                continue
            return pipe_location_direction

        raise ValueError("No location direction found")

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

    def __str__(self) -> str:
        lines: list[str] = []
        for grid_location_row in self.grid:
            line_str = ""
            for grid_location in grid_location_row:
                line_str = f"{line_str}{grid_location.value}"
            lines.append(line_str)
        if self.starting_grid_location:
            lines.append(
                f"X: {self.starting_grid_location.location.x}, Y: {self.starting_grid_location.location.y}"
            )
        return "\n".join(lines)


def create_grid_locations(y_index: int, line: str, pipe_maze: PipeMaze):
    grid_locations: list[GridLocation] = []
    for x_index, character in enumerate(line):
        location = Location(x_index, y_index)
        grid_location = GridLocation(location, character)
        if grid_location.type == LocationType.STARTING_POSITION:
            pipe_maze.starting_grid_location = grid_location
        grid_locations.append(grid_location)
    return grid_locations


def create_pipe_maze(data: typing.Iterator[str]) -> PipeMaze:
    pipe_maze = PipeMaze()
    for y_index, line in enumerate(data):
        grid_locations = create_grid_locations(y_index, line, pipe_maze)
        pipe_maze.grid.append(grid_locations)
    return pipe_maze


def part_one(pipe_maze: PipeMaze) -> int:
    starting_grid_location = pipe_maze.starting_grid_location
    if not starting_grid_location:
        raise ValueError("No starting grid location")
    steps = 1

    (
        direction1_location_direction,
        direction2_location_direction,
    ) = pipe_maze.possible_starting_location_directions()
    direction1_grid_location = pipe_maze.get_neighbour_grid_location(
        starting_grid_location, direction1_location_direction
    )
    direction2_grid_location = pipe_maze.get_neighbour_grid_location(
        starting_grid_location, direction2_location_direction
    )
    print(f"Step: {steps} direction1: {direction1_grid_location}")
    print(f"Step: {steps} direction2: {direction2_grid_location}")
    while True:
        direction1_location_direction = pipe_maze.pipe_move_location_direction(
            direction1_grid_location, direction1_location_direction
        )
        direction1_grid_location = pipe_maze.get_neighbour_grid_location(
            direction1_grid_location, direction1_location_direction
        )
        direction2_location_direction = pipe_maze.pipe_move_location_direction(
            direction2_grid_location, direction2_location_direction
        )
        direction2_grid_location = pipe_maze.get_neighbour_grid_location(
            direction2_grid_location, direction2_location_direction
        )
        steps += 1
        print(f"Step: {steps} direction1: {direction1_grid_location}")
        print(f"Step: {steps} direction2: {direction2_grid_location}")

        if direction1_grid_location == direction2_grid_location:
            break

    return steps


def part_two() -> int:
    return 0


def main():
    data = yield_data(FILENAME)
    pipe_maze = create_pipe_maze(data)
    print(f"Part one: {part_one(pipe_maze)}")
    # print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
