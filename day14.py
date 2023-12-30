import dataclasses
import enum
import typing

TEST_FILENAME = "day14_testdata.txt"
FILENAME = "day14_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    ROUND_ROCK = "O"
    CUBE_ROCK = "#"
    EMPTY_SPACE = "."
    OUT_OF_BOUNDS = "@"

    @classmethod
    def convertor(cls, string: str) -> "LocationType":
        for location_type in LocationType:
            if location_type.value == string:
                return location_type
        raise ValueError("Invalid LocationType string")


@dataclasses.dataclass(slots=True, frozen=True, order=True)
class Location:
    x: int
    y: int


@dataclasses.dataclass(slots=True, frozen=True)
class GridLocation:
    location: Location
    type: LocationType

    @property
    def value(self) -> str:
        return self.type.value


@dataclasses.dataclass(slots=True)
class Platform:
    grid_locations: dict[Location, GridLocation] = dataclasses.field(
        default_factory=dict
    )
    max_x_location: int = 0
    max_y_location: int = 0

    def tilt_north(self) -> None:
        new_grid_locations: list[GridLocation] = []
        for x_index in range(self.max_x_location + 1):
            fixed_y_index = -1
            for y_index in range(self.max_y_location + 1):
                current_location = Location(x_index, y_index)
                grid_location = self.get_grid_location(current_location)

                match grid_location.type:
                    case LocationType.CUBE_ROCK:
                        fixed_y_index = current_location.y

                    case LocationType.ROUND_ROCK:
                        fixed_y_index += 1
                        new_location = Location(current_location.x, fixed_y_index)
                        if new_location == current_location:
                            continue
                        new_grid_location = GridLocation(
                            new_location, grid_location.type
                        )
                        new_grid_locations.append(new_grid_location)
                        self.remove_grid_location(current_location)

        for grid_location in new_grid_locations:
            self.add_grid_location(grid_location)

    def tilt_south(self) -> None:
        new_grid_locations: list[GridLocation] = []
        for x_index in range(self.max_x_location + 1):
            fixed_y_index = self.max_y_location + 1
            for y_index in range(self.max_y_location, -1, -1):
                current_location = Location(x_index, y_index)
                grid_location = self.get_grid_location(current_location)

                match grid_location.type:
                    case LocationType.CUBE_ROCK:
                        fixed_y_index = current_location.y

                    case LocationType.ROUND_ROCK:
                        fixed_y_index -= 1
                        new_location = Location(current_location.x, fixed_y_index)
                        if new_location == current_location:
                            continue
                        new_grid_location = GridLocation(
                            new_location, grid_location.type
                        )
                        new_grid_locations.append(new_grid_location)
                        self.remove_grid_location(current_location)

        for grid_location in new_grid_locations:
            self.add_grid_location(grid_location)

    def tilt_west(self) -> None:
        new_grid_locations: list[GridLocation] = []
        for y_index in range(self.max_y_location + 1):
            fixed_x_index = -1
            for x_index in range(self.max_x_location + 1):
                current_location = Location(x_index, y_index)
                grid_location = self.get_grid_location(current_location)

                match grid_location.type:
                    case LocationType.CUBE_ROCK:
                        fixed_x_index = current_location.x

                    case LocationType.ROUND_ROCK:
                        fixed_x_index += 1
                        new_location = Location(fixed_x_index, current_location.y)
                        if new_location == current_location:
                            continue
                        new_grid_location = GridLocation(
                            new_location, grid_location.type
                        )
                        new_grid_locations.append(new_grid_location)
                        self.remove_grid_location(current_location)

        for grid_location in new_grid_locations:
            self.add_grid_location(grid_location)

    def tilt_east(self) -> None:
        new_grid_locations: list[GridLocation] = []
        for y_index in range(self.max_y_location + 1):
            fixed_x_index = self.max_x_location + 1
            for x_index in range(self.max_x_location, -1, -1):
                current_location = Location(x_index, y_index)
                grid_location = self.get_grid_location(current_location)

                match grid_location.type:
                    case LocationType.CUBE_ROCK:
                        fixed_x_index = current_location.x

                    case LocationType.ROUND_ROCK:
                        fixed_x_index -= 1
                        new_location = Location(fixed_x_index, current_location.y)
                        if new_location == current_location:
                            continue
                        new_grid_location = GridLocation(
                            new_location, grid_location.type
                        )
                        new_grid_locations.append(new_grid_location)
                        self.remove_grid_location(current_location)

        for grid_location in new_grid_locations:
            self.add_grid_location(grid_location)

    def total_load_of_north_support(self) -> int:
        total = 0
        rock_load = self.max_y_location + 1
        for y_index in range(self.max_y_location + 1):
            for x_index in range(self.max_x_location + 1):
                grid_location = self.get_grid_location(Location(x_index, y_index))
                if grid_location.type == LocationType.ROUND_ROCK:
                    total += rock_load
            rock_load -= 1

        return total

    def cycle(self) -> None:
        self.tilt_north()
        self.tilt_west()
        self.tilt_south()
        self.tilt_east()

    def add_grid_location(self, grid_location: GridLocation) -> None:
        match grid_location.type:
            case LocationType.ROUND_ROCK | LocationType.CUBE_ROCK:
                location = grid_location.location
                self.grid_locations[location] = grid_location
        self.update_max_values(grid_location.location)

        return None

    def remove_grid_location(self, location: Location) -> GridLocation:
        if not self.location_in_grid(location):
            return GridLocation(location, LocationType.OUT_OF_BOUNDS)
        return self.grid_locations.pop(
            location, GridLocation(location, LocationType.EMPTY_SPACE)
        )

    def update_max_values(self, location: Location) -> None:
        self.max_x_location = max(self.max_x_location, location.x)
        self.max_y_location = max(self.max_y_location, location.y)

    def get_grid_location(self, location: Location) -> GridLocation:
        if not self.location_in_grid(location):
            return GridLocation(location, LocationType.OUT_OF_BOUNDS)
        return self.grid_locations.get(
            location,
            GridLocation(location, LocationType.EMPTY_SPACE),
        )

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

    def __hash__(self) -> int:
        return hash(frozenset(self.grid_locations.items()))


def create_platform(data: typing.Iterator[str]) -> Platform:
    platform = Platform()
    for y_index, line in enumerate(data):
        for x_index, character in enumerate(line):
            location = Location(x_index, y_index)
            grid_location = GridLocation(location, LocationType.convertor(character))
            platform.add_grid_location(grid_location)
    return platform


def part_one() -> int:
    data = yield_data(FILENAME)
    platform = create_platform(data)
    platform.tilt_north()
    total = platform.total_load_of_north_support()

    return total


def part_two() -> int:
    data = yield_data(FILENAME)
    platform = create_platform(data)
    seen_states: set[int] = set()
    seen_index: list[int] = []
    seen_results: list[int] = []
    result = 0
    for cycle_number in range(1000000000):
        platform.cycle()
        total_load = platform.total_load_of_north_support()
        # print(f"{cycle_number=} {total_load=}")
        platform_hash = hash(platform)
        if platform_hash in seen_states:
            # print(f"At {cycle_number=} seen state before")
            first_seen_index = seen_index.index(platform_hash)
            cycle_length = cycle_number - first_seen_index
            result_index = (
                (1000000000 - first_seen_index) % cycle_length + first_seen_index - 1
            )
            result = seen_results[result_index]
            break

        seen_states.add(platform_hash)
        seen_index.append(platform_hash)
        seen_results.append(total_load)

    return result


def main():
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
