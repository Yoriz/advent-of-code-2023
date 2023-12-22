import collections
import dataclasses
import enum
import typing

TEST_FILENAME = "day21_testdata.txt"
FILENAME = "day21_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    GARDEN_PLOT = "."
    ROCK = "#"
    STARTING_POSITION = "S"
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


possible_location_directions = tuple(LocationDirection)


@dataclasses.dataclass(slots=True)
class LocationMovements:
    current_location: Location
    steps: int = 0
    max_steps: int = 64

    def get_copy(self) -> "LocationMovements":
        return LocationMovements(self.current_location, self.steps, self.max_steps)

    def available_location_directions(
        self, map: "Map"
    ) -> tuple[LocationDirection, ...]:
        if self.steps == self.max_steps:
            return tuple()
        possible_movements: list[LocationDirection] = []
        for location_direction in possible_location_directions:
            neighbour_location = self.current_location.neighbour_location(
                location_direction
            )
            neighbour_grid_location = map.get_grid_location(neighbour_location)
            if neighbour_grid_location.type in (
                LocationType.OUT_OF_BOUNDS,
                LocationType.ROCK,
            ):
                continue

            possible_movements.append(location_direction)

        return tuple(possible_movements)

    def move(self, location_direction: LocationDirection, map: "Map") -> None:
        if location_direction not in self.available_location_directions(map):
            raise ValueError("Invalid LocationMovement")
        neighbour_location = self.current_location.neighbour_location(
            location_direction
        )
        self.current_location = neighbour_location
        self.steps += 1

        return None


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


@dataclasses.dataclass
class Map:
    grid_locations: dict[tuple[int, int], GridLocation] = dataclasses.field(
        default_factory=dict
    )
    max_x_location: int = 0
    max_y_location: int = 0
    start_location: typing.Optional[Location] = None

    def add_grid_location(self, grid_location: GridLocation) -> None:
        if grid_location.type in (
            LocationType.GARDEN_PLOT,
            LocationType.STARTING_POSITION,
        ):
            self.grid_locations[(grid_location.x, grid_location.y)] = grid_location
        self.update_max_values(grid_location.location)

        return None

    def update_max_values(self, location: Location) -> None:
        self.max_x_location = max(self.max_x_location, location.x)
        self.max_y_location = max(self.max_y_location, location.y)

    def get_grid_location(self, location: Location) -> GridLocation:
        if not self.location_in_grid(location):
            return GridLocation(location, LocationType.OUT_OF_BOUNDS)
        grid_location = self.grid_locations.get(
            (location.x, location.y), GridLocation(location, LocationType.ROCK)
        )

        return grid_location

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

    def view_seen(self, seen_locations: set[Location]) -> str:
        rows: list[str] = []
        for y_index in range(self.max_y_location + 1):
            row = ""
            for x_index in range(self.max_x_location + 1):
                location = Location(x_index, y_index)
                grid_location = self.get_grid_location(location)
                value = grid_location.type.value
                if location in seen_locations:
                    value = LocationType.SEEN.value
                row = f"{row}{value}"
            rows.append(row)
        return "\n".join(rows)


def create_map(data: typing.Iterator[str]) -> Map:
    map = Map()
    for y_index, line in enumerate(data):
        for x_index, character in enumerate(line):
            location = Location(x_index, y_index)
            match character:
                case LocationType.GARDEN_PLOT.value:
                    location_type = LocationType.GARDEN_PLOT
                case LocationType.ROCK.value:
                    location_type = LocationType.ROCK
                case LocationType.STARTING_POSITION.value:
                    location_type = LocationType.STARTING_POSITION
                    map.start_location = location
                case _:
                    raise ValueError(f"Invalid character: {character}")

            grid_location = GridLocation(location, location_type)
            map.add_grid_location(grid_location)
    return map


def discover_plots(map: Map, max_steps: int) -> int:
    start_location = map.start_location
    queue = collections.deque()
    seen_keys: set[tuple[Location, int]] = set()
    ending_plot_locations: set[Location] = set()
    if not start_location:
        raise ValueError("No start location")
    location_movements = LocationMovements(start_location, max_steps=max_steps)
    # ending_plot_locations.add(start_location)
    queue.append(location_movements)
    total_steps = 0
    while queue:
        location_movements: LocationMovements = queue.popleft()
        if not location_movements:
            raise ValueError("Exhausted the queue")
        for movement in location_movements.available_location_directions(map):
            new_location_movements = location_movements.get_copy()
            new_location_movements.move(movement, map)
            seen_key = (
                new_location_movements.current_location,
                new_location_movements.steps,
            )
            if seen_key in seen_keys:
                continue
            seen_keys.add(seen_key)
            if total_steps < new_location_movements.steps:
                total_steps = new_location_movements.steps
                print(f"{total_steps=}, {len(queue)=}")
            if new_location_movements.steps == max_steps:
                ending_plot_locations.add(new_location_movements.current_location)
            queue.append(new_location_movements)

    # print(f"{seen_locations=}")
    # print(map.view_seen(ending_plot_locations))
    return len(ending_plot_locations)


def part_one() -> int:
    data = yield_data(FILENAME)
    map = create_map(data)
    total = discover_plots(map, 64)
    return total


def part_two() -> int:
    return 0


def main():
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
