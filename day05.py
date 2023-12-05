import dataclasses
import typing

TEST_FILENAME = "day5_testdata.txt"
FILENAME = "day5_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


@dataclasses.dataclass
class MapRange:
    destination_range_start: int
    source_range_start: int
    range_length: int

    def in_source_range(self, value: int) -> bool:
        return (
            value >= self.source_range_start
            and value <= self.source_range_start + self.range_length - 1
        )
        return False

    def conversion(self, value: int) -> int:
        if not self.in_source_range(value):
            raise ValueError("Value is not in source range")
        difference = self.source_range_start - self.destination_range_start
        return value - difference


@dataclasses.dataclass
class ConversionMap:
    map_ranges: list[MapRange] = dataclasses.field(default_factory=list)

    def add_map_range(
        self, destination_range_start: int, source_range_start: int, range_length: int
    ):
        map_range = MapRange(destination_range_start, source_range_start, range_length)
        self.map_ranges.append(map_range)

    def convert(self, value: int) -> int:
        for map_range in self.map_ranges:
            if not map_range.in_source_range(value):
                continue
            return map_range.conversion(value)
        return value


@dataclasses.dataclass
class Almanac:
    seeds: list[int] = dataclasses.field(default_factory=list)
    seed_to_soil_map: ConversionMap = dataclasses.field(default_factory=ConversionMap)
    soil_to_fertilizer_map: ConversionMap = dataclasses.field(
        default_factory=ConversionMap
    )
    fertilizer_to_water_map: ConversionMap = dataclasses.field(
        default_factory=ConversionMap
    )
    water_to_light_map: ConversionMap = dataclasses.field(default_factory=ConversionMap)
    light_to_temperature_map: ConversionMap = dataclasses.field(
        default_factory=ConversionMap
    )
    temperature_to_humidity_map: ConversionMap = dataclasses.field(
        default_factory=ConversionMap
    )
    humidity_to_location_map: ConversionMap = dataclasses.field(
        default_factory=ConversionMap
    )

    def convert_seeds_to_locations(self) -> list[int]:
        locations: list[int] = []
        for seed in self.seeds:
            soil = self.seed_to_soil_map.convert(seed)
            fertilizer = self.soil_to_fertilizer_map.convert(soil)
            water = self.fertilizer_to_water_map.convert(fertilizer)
            light = self.water_to_light_map.convert(water)
            temperature = self.light_to_temperature_map.convert(light)
            humidity = self.temperature_to_humidity_map.convert(temperature)
            location = self.humidity_to_location_map.convert(humidity)
            (
                f"Seed {seed}, soil {soil}, fertilizer {fertilizer}, water {water}, light {light}, temperature {temperature}, humidity {humidity}, location {location}"
            )
            locations.append(location)
        return locations

    def get_map(self, map_name: str) -> ConversionMap:
        return {
            "seed-to-soil map:": self.seed_to_soil_map,
            "soil-to-fertilizer map:": self.soil_to_fertilizer_map,
            "fertilizer-to-water map:": self.fertilizer_to_water_map,
            "water-to-light map:": self.water_to_light_map,
            "light-to-temperature map:": self.light_to_temperature_map,
            "temperature-to-humidity map:": self.temperature_to_humidity_map,
            "humidity-to-location map:": self.humidity_to_location_map,
        }[map_name]


def create_almanac(data: typing.Iterator[str]) -> Almanac:
    almanac = Almanac()
    section = ""
    for line in data:
        if line.startswith("seeds"):
            _, numbers = line.split(":")
            seeds = numbers.strip().split(" ")
            for seed in seeds:
                almanac.seeds.append(int(seed))
            continue
        if line == "":
            section = ""
            continue
        if line in (
            "seed-to-soil map:",
            "soil-to-fertilizer map:",
            "fertilizer-to-water map:",
            "water-to-light map:",
            "light-to-temperature map:",
            "temperature-to-humidity map:",
            "humidity-to-location map:",
        ):
            section = line
            continue
        destination_range_start, source_range_start, range_length = line.strip().split(
            " "
        )
        map = almanac.get_map(section)
        map.add_map_range(
            int(destination_range_start), int(source_range_start), int(range_length)
        )

    return almanac


def part_one(almanac: Almanac) -> int:
    locations = almanac.convert_seeds_to_locations()
    return min(locations)


def part_two():
    return 0


def main():
    data = yield_data(FILENAME)
    almanac = create_almanac(data)
    (f"Part one: {part_one(almanac)}")
    # (f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
