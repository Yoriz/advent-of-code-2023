import collections
import dataclasses
import enum
import typing

TEST_FILENAME = "day23_testdata.txt"
FILENAME = "day23_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    PATH = "."
    FOREST = "#"
    SLOPE_UP = "^"
    SLOPE_RIGHT = ">"
    SLOPE_DOWN = "v"
    SLOPE_LEFT = "<"
    OUT_OF_BOUNDS = "@"
    SEEN = "O"


@dataclasses.dataclass(slots=True, frozen=True)
class Location:
    x: int
    y: int

    def neighbour_location(self, location_direction: "LocationDirection") -> "Location":
        other_location: "Location" = location_direction.value
        return Location(self.x + other_location.x, self.y + other_location.y)

    def distance(self, other: "Location") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)


@enum.unique
class LocationDirection(enum.Enum):
    UP = Location(0, -1)
    RIGHT = Location(1, 0)
    DOWN = Location(0, 1)
    LEFT = Location(-1, 0)


LOCATION_TYPE_DIRECTIONS: dict[LocationType, tuple[LocationDirection, ...]] = {
    LocationType.PATH: (
        LocationDirection.UP,
        LocationDirection.RIGHT,
        LocationDirection.DOWN,
        LocationDirection.LEFT,
    ),
    LocationType.SLOPE_UP: (LocationDirection.UP,),
    LocationType.SLOPE_RIGHT: (LocationDirection.RIGHT,),
    LocationType.SLOPE_DOWN: (LocationDirection.DOWN,),
    LocationType.SLOPE_LEFT: (LocationDirection.LEFT,),
}

UNACCESSIBLE_LOCATION_TYPES: tuple[LocationType, ...] = (
    LocationType.FOREST,
    LocationType.OUT_OF_BOUNDS,
)


@dataclasses.dataclass(slots=True, frozen=True)
class GridLocation:
    location: Location
    type: LocationType

    @property
    def x(self) -> int:
        return self.location.x

    @property
    def y(self) -> int:
        return self.location.y

    def is_accessible(self, from_location_direction: LocationDirection) -> bool:
        match self.type:
            case LocationType.FOREST | LocationType.OUT_OF_BOUNDS:
                return False
            case LocationType.SLOPE_UP if from_location_direction == LocationDirection.DOWN:
                return False
            case LocationType.SLOPE_RIGHT if from_location_direction == LocationDirection.LEFT:
                return False
            case LocationType.SLOPE_DOWN if from_location_direction == LocationDirection.UP:
                return False
            case LocationType.SLOPE_LEFT if from_location_direction == LocationDirection.RIGHT:
                return False

            case _:
                return True

    @property
    def location_directions(self) -> tuple[LocationDirection, ...]:
        type_location_directions = LOCATION_TYPE_DIRECTIONS.get(self.type, tuple())
        return type_location_directions


@dataclasses.dataclass(slots=True)
class Grid:
    grid_locations: dict[tuple[int, int], GridLocation] = dataclasses.field(
        default_factory=dict
    )
    max_x_location: int = 0
    max_y_location: int = 0
    start_grid_location: typing.Optional[GridLocation] = None
    end_grid_location: typing.Optional[GridLocation] = None

    def add_grid_location(self, grid_location: GridLocation) -> None:
        if grid_location.type != LocationType.FOREST:
            self.grid_locations[(grid_location.x, grid_location.y)] = grid_location
        self.update_max_values(grid_location.location)

        return None

    def update_max_values(self, location: Location) -> None:
        self.max_x_location = max(self.max_x_location, location.x)
        self.max_y_location = max(self.max_y_location, location.y)

    def update_start_location(self) -> None:
        Y_INDEX = 0
        for x_index in range(self.max_x_location + 1):
            grid_location = self.get_grid_location(Location(x_index, Y_INDEX))
            if grid_location.type == LocationType.PATH:
                self.start_grid_location = grid_location
                return None

        return None

    def update_end_location(self) -> None:
        Y_INDEX = self.max_y_location
        for x_index in range(self.max_x_location + 1):
            grid_location = self.get_grid_location(Location(x_index, Y_INDEX))
            if grid_location.type == LocationType.PATH:
                self.end_grid_location = grid_location
                return None

        return None

    def get_grid_location(self, location: Location) -> GridLocation:
        if not self.location_in_grid(location):
            return GridLocation(location, LocationType.OUT_OF_BOUNDS)

        grid_location = self.grid_locations.get(
            (location.x, location.y), GridLocation(location, LocationType.FOREST)
        )

        return grid_location

    def neighbour_grid_location(
        self, grid_location: GridLocation, location_direction: LocationDirection
    ) -> GridLocation:
        location = grid_location.location
        neighbour_location = location.neighbour_location(location_direction)
        grid_location = self.get_grid_location(neighbour_location)

        return grid_location

    def neighbour_grid_locations(
        self,
        grid_location: GridLocation,
        location_directions: typing.Sequence[LocationDirection],
    ) -> tuple[GridLocation, ...]:
        neighbour_grid_locations: list[GridLocation] = []
        for location_direction in location_directions:
            neighbour_grid_location = self.neighbour_grid_location(
                grid_location, location_direction
            )
            neighbour_grid_locations.append(neighbour_grid_location)

        return tuple(neighbour_grid_locations)

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
                row = f"{row}{grid_location.type.value}"
            rows.append(row)
        return "\n".join(rows)

    def __hash__(self) -> int:
        return hash(frozenset(self.grid_locations.items()))


def create_grid(data: typing.Iterator[str], infinate: bool = False) -> Grid:
    map = Grid()
    for y_index, line in enumerate(data):
        for x_index, character in enumerate(line):
            location = Location(x_index, y_index)
            for location_type in LocationType:
                if location_type.value == character:
                    grid_location = GridLocation(location, location_type)
                    map.add_grid_location(grid_location)
                    continue
    return map


@dataclasses.dataclass(slots=True)
class Path:
    current_grid_location: GridLocation
    grid: Grid = dataclasses.field(repr=False)
    history: set[GridLocation] = dataclasses.field(default_factory=set)

    def copy(self) -> "Path":
        path_copy = Path(self.current_grid_location, self.grid, self.history.copy())
        return path_copy

    @property
    def accessible_location_directions(self) -> tuple[LocationDirection, ...]:
        location_directions: list[LocationDirection] = []
        for location_direction in self.current_grid_location.location_directions:
            neighbour_grid_location = self.grid.neighbour_grid_location(
                self.current_grid_location, location_direction
            )
            if not neighbour_grid_location.is_accessible(location_direction):
                continue
            location_directions.append(location_direction)

        return tuple(location_directions)

    def move(self, location_direction: LocationDirection) -> None:
        if location_direction not in self.accessible_location_directions:
            raise ValueError("Invalid location_direction")
        grid_location = self.grid.neighbour_grid_location(
            self.current_grid_location, location_direction
        )
        self.current_grid_location = grid_location
        self.history.add(self.current_grid_location)

    @property
    def steps(self) -> int:
        return len(self.history)

    def __hash__(self) -> int:
        return hash(
            frozenset((self.current_grid_location, self.grid, tuple(self.history)))
        )


def find_longest_path(grid: Grid) -> int:
    longest: int = 0
    queue: collections.deque[Path] = collections.deque()
    if not grid.start_grid_location:
        raise ValueError("N0 start location")
    grid_location = grid.start_grid_location
    path = Path(grid_location, grid)
    queue.append(path)
    count = 0
    while queue:
        count += 1
        path = queue.pop()
        if count % 1000 == 0:
            print(
                f"{count} {len(queue)=} {path.current_grid_location.location} {longest}"
            )
        # if count == 2000:
        #     print(f"Stoped current que size: {len(queue)}")
        #     break
        for location_direction in path.accessible_location_directions:
            if (
                grid.neighbour_grid_location(
                    path.current_grid_location, location_direction
                )
                in path.history
            ):
                continue

            path_copy = path.copy()
            path_copy.move(location_direction)
            queue.append(path_copy)
            longest = max(longest, path_copy.steps)

    return longest


def part_one() -> int:
    data = yield_data(FILENAME)
    grid = create_grid(data)
    grid.update_start_location()
    grid.update_end_location()
    longest = find_longest_path(grid)
    return longest


def part_two() -> int:
    return 0


def main():
    print(f"Part one: {part_one()}")
    # print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
