import dataclasses
import enum
import queue
import typing

TEST_FILENAME = "day17_testdata.txt"
FILENAME = "day17_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    CITY_BLOCK = enum.auto()
    OUT_OF_BOUNDS = enum.auto()


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


class LocationMovement(enum.Enum):
    FORWARD = enum.auto()
    LEFT_90_DEG = enum.auto()
    RIGHT_90_DEG = enum.auto()


MOVEMENTS: dict[LocationDirection, dict[LocationMovement, LocationDirection]] = {
    LocationDirection.UP: {
        LocationMovement.FORWARD: LocationDirection.UP,
        LocationMovement.LEFT_90_DEG: LocationDirection.LEFT,
        LocationMovement.RIGHT_90_DEG: LocationDirection.RIGHT,
    },
    LocationDirection.RIGHT: {
        LocationMovement.FORWARD: LocationDirection.RIGHT,
        LocationMovement.LEFT_90_DEG: LocationDirection.UP,
        LocationMovement.RIGHT_90_DEG: LocationDirection.DOWN,
    },
    LocationDirection.DOWN: {
        LocationMovement.FORWARD: LocationDirection.DOWN,
        LocationMovement.LEFT_90_DEG: LocationDirection.RIGHT,
        LocationMovement.RIGHT_90_DEG: LocationDirection.LEFT,
    },
    LocationDirection.LEFT: {
        LocationMovement.FORWARD: LocationDirection.LEFT,
        LocationMovement.LEFT_90_DEG: LocationDirection.DOWN,
        LocationMovement.RIGHT_90_DEG: LocationDirection.UP,
    },
}


@dataclasses.dataclass(slots=True)
class LocationMovements:
    facing_direction: LocationDirection
    current_location: Location
    current_heat_loss: int = 0
    facing_direction_count: int = 0
    history: list[Location] = dataclasses.field(default_factory=list)
    heat_loss_total: int = 0
    ultra_crucibal: bool = False

    def get_copy(self) -> "LocationMovements":
        return LocationMovements(
            self.facing_direction,
            self.current_location,
            self.current_heat_loss,
            self.facing_direction_count,
            self.history.copy(),
            self.heat_loss_total,
            self.ultra_crucibal,
        )

    def available_movements(self, map: "Map") -> tuple[LocationMovement, ...]:
        max_forward = 3 if not self.ultra_crucibal else 10
        if self.ultra_crucibal and self.facing_direction_count < 4:
            movements = []
        else:
            movements = [LocationMovement.LEFT_90_DEG, LocationMovement.RIGHT_90_DEG]
        if self.facing_direction_count < max_forward:
            movements.append(LocationMovement.FORWARD)
        possible_movements: list[LocationMovement] = []
        for movement in movements:
            location_direction = MOVEMENTS[self.facing_direction][movement]
            neighbour_location = self.current_location.neighbour_location(
                location_direction
            )
            neighbour_grid_location = map.get_grid_location(neighbour_location)

            # if (neighbour_grid_location.type == LocationType.OUT_OF_BOUNDS) or (
            #     neighbour_location in self.history
            # ):
            #     continue
            if neighbour_grid_location.type == LocationType.OUT_OF_BOUNDS:
                continue

            possible_movements.append(movement)

        return tuple(possible_movements)

    def move(self, location_movement: LocationMovement, map: "Map") -> None:
        if location_movement not in self.available_movements(map):
            raise ValueError("Invalid LocationMovement")

        location_direction = MOVEMENTS[self.facing_direction][location_movement]

        if location_direction == self.facing_direction:
            self.facing_direction_count += 1
        else:
            self.facing_direction_count = 1

        self.facing_direction = location_direction
        neighbour_location = self.current_location.neighbour_location(
            location_direction
        )
        self.current_location = neighbour_location
        self.history.append(self.current_location)
        grid_location = map.get_grid_location(self.current_location)
        self.current_heat_loss = grid_location.value
        self.heat_loss_total += self.current_heat_loss

        return None

    def map_show_visited(self, map: "Map") -> str:
        rows: list[str] = []
        for y_index in range(map.max_y_location + 1):
            row = ""
            for x_index in range(map.max_x_location + 1):
                location = Location(x_index, y_index)
                grid_location = map.get_grid_location(location)
                value = grid_location.value if not location in self.history else "."
                row = f"{row}{value}"
            rows.append(row)
        return "\n".join(rows)

    def seen_key(self) -> tuple[int, int, LocationDirection, int]:
        return (
            self.current_location.x,
            self.current_location.y,
            self.facing_direction,
            self.facing_direction_count,
        )


@dataclasses.dataclass(slots=True, frozen=True)
class GridLocation:
    location: Location
    value: int
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

    def add_grid_location(self, grid_location: GridLocation) -> None:
        self.grid_locations[(grid_location.x, grid_location.y)] = grid_location
        self.update_max_values(grid_location.location)

        return None

    def update_max_values(self, location: Location) -> None:
        self.max_x_location = max(self.max_x_location, location.x)
        self.max_y_location = max(self.max_y_location, location.y)

    def get_grid_location(self, location: Location) -> GridLocation:
        if not self.location_in_grid(location):
            return GridLocation(location, 0, LocationType.OUT_OF_BOUNDS)
        grid_location = self.grid_locations.get((location.x, location.y))
        if not grid_location:
            raise ValueError("GridLocation not found")

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
                row = f"{row}{grid_location.value}"
            rows.append(row)
        return "\n".join(rows)


def create_map(data: typing.Iterator[str]) -> Map:
    map = Map()
    for y_index, line in enumerate(data):
        for x_index, character in enumerate(line):
            location = Location(x_index, y_index)
            number = int(character)
            grid_location = GridLocation(location, number, LocationType.CITY_BLOCK)
            map.add_grid_location(grid_location)
    return map


@dataclasses.dataclass(order=True)
class PrioritizedLocationMovement:
    priority: tuple[int, int]
    location_movements: LocationMovements = dataclasses.field(compare=False)


def create_prioritized_location_movement(
    target_location: Location, location_movements: LocationMovements, map: Map
) -> PrioritizedLocationMovement:
    distance = location_movements.current_location.distance(target_location)
    heat_loss_total = location_movements.heat_loss_total
    # prioritized_location_movement = PrioritizedLocationMovement(
    #     (distance, heat_loss), location_movements
    # ) # finds target quick at index 23

    prioritized_location_movement = PrioritizedLocationMovement(
        (heat_loss_total, 0), location_movements
    )  # doesnt not find target in a good time

    # prioritized_location_movement = PrioritizedLocationMovement(
    #     (distance, distance * heat_loss), location_movements
    # )
    return prioritized_location_movement


def find_minimal_heat_loss_path(map: Map, ultra_crucibal: bool = False) -> int:
    minimal = float("inf")
    best = None
    seen_keys: set[tuple[int, int, LocationDirection, int]] = set()
    priority_queue: queue.PriorityQueue[
        PrioritizedLocationMovement
    ] = queue.PriorityQueue()
    target_location = Location(map.max_x_location, map.max_y_location)
    location_movements = LocationMovements(
        LocationDirection.RIGHT, Location(0, 0), ultra_crucibal=ultra_crucibal
    )
    prioritized_location_movement = create_prioritized_location_movement(
        target_location, location_movements, map
    )
    priority_queue.put(prioritized_location_movement)
    for index in range(1000000):
        if index % 100000 == 0:
            print(f"{index=}")
        if priority_queue.empty():
            print("Priority queue empty")
            break
        location_movements = priority_queue.get(False).location_movements
        for movement in location_movements.available_movements(map):
            new_location_movements = location_movements.get_copy()

            new_location_movements.move(movement, map)
            if new_location_movements.seen_key() in seen_keys:
                continue
            if new_location_movements.current_location == target_location:
                if ultra_crucibal and new_location_movements.facing_direction_count < 4:
                    continue
                minimal = new_location_movements.heat_loss_total
                print(f"Found target at {index}, Heat loss total: {minimal}")
                return minimal
                # # print(new_location_movements.map_show_visited(map))
                # if new_location_movements.heat_loss_total < minimal:
                #     minimal = new_location_movements.heat_loss_total
                #     best = new_location_movements
                #     continue
            seen_keys.add(new_location_movements.seen_key())
            prioritized_location_movement = create_prioritized_location_movement(
                target_location, new_location_movements, map
            )
            priority_queue.put(prioritized_location_movement)

    if not best:
        print("target not found")
    # else:
    #     print(best.map_show_visited(map))

    return minimal


def part_one() -> int:
    data = yield_data(FILENAME)
    map = create_map(data)
    result = find_minimal_heat_loss_path(map)
    return result


def part_two() -> int:
    data = yield_data(FILENAME)
    map = create_map(data)
    result = find_minimal_heat_loss_path(map, True)
    return result


def main():
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
