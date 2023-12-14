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
        match self.value:
            case LocationType.ROUND_ROCK.value:
                return LocationType.ROUND_ROCK
            case LocationType.CUBE_ROCK.value:
                return LocationType.CUBE_ROCK
            case LocationType.EMPTY_SPACE.value:
                return LocationType.EMPTY_SPACE
            case LocationType.OUT_OF_BOUNDS.value:
                return LocationType.OUT_OF_BOUNDS
            case _:
                raise ValueError(f"Invalid type: {self.value}")

    @property
    def x(self) -> int:
        return self.location.x

    @x.setter
    def x(self, value) -> None:
        self.location.x = value

    @property
    def y(self) -> int:
        return self.location.y

    @y.setter
    def y(self, value) -> None:
        self.location.y = value


@dataclasses.dataclass
class Platform:
    grid_locations: dict[tuple[int, int], GridLocation] = dataclasses.field(
        default_factory=dict
    )
    max_x_location: int = 0
    max_y_location: int = 0

    def add_grid_location(self, grid_location: GridLocation) -> None:
        match grid_location.type:
            case LocationType.ROUND_ROCK | LocationType.CUBE_ROCK:
                self.grid_locations[(grid_location.x, grid_location.y)] = grid_location
        self.update_max_values(grid_location.location)

        return None

    def update_max_values(self, location: Location) -> None:
        self.max_x_location = max(self.max_x_location, location.x)
        self.max_y_location = max(self.max_y_location, location.y)

    def get_grid_location(self, location: Location) -> GridLocation:
        if not self.location_in_grid(location):
            return GridLocation(location, LocationType.OUT_OF_BOUNDS.value)
        return self.grid_locations.get(
            (location.x, location.y),
            GridLocation(location, LocationType.EMPTY_SPACE.value),
        )

    def tilt_north(self) -> None:
        for x_index in range(self.max_x_location + 1):
            fixed_y_index = -1
            for y_index in range(self.max_y_location + 1):
                grid_location = self.get_grid_location(Location(x_index, y_index))
                match grid_location.type:
                    case LocationType.CUBE_ROCK:
                        fixed_y_index = grid_location.y
                    case LocationType.ROUND_ROCK:
                        del self.grid_locations[(grid_location.x, grid_location.y)]
                        fixed_y_index += 1
                        grid_location.y = fixed_y_index
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


def create_platform(data: typing.Iterator[str]) -> Platform:
    platform = Platform()
    for y_index, line in enumerate(data):
        for x_index, character in enumerate(line):
            location = Location(x_index, y_index)
            grid_location = GridLocation(location, character)
            platform.add_grid_location(grid_location)
    return platform


def part_one() -> int:
    data = yield_data(FILENAME)
    platform = create_platform(data)
    platform.tilt_north()
    total = platform.total_load_of_north_support()
    return total


def part_two() -> int:
    return 0


def main():
    print(f"Part one: {part_one()}")
    # print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
