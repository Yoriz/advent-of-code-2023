import dataclasses
import enum
import itertools
import typing

TEST_FILENAME = "day5_testdata.txt"
FILENAME = "day5_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class NumberRangeSplitType(enum.Enum):
    IS_BEFORE = enum.auto()
    IS_AFTER = enum.auto()
    OVERLAPS_BEFORE = enum.auto()
    OVERLAPS_AFTER = enum.auto()
    OVERLAPS_INSIDE = enum.auto()
    OVERLAPS_ALL = enum.auto()


@dataclasses.dataclass(slots=True, frozen=True)
class NumberRangeSplit:
    split_type: NumberRangeSplitType
    number_range: "NumberRange"


@dataclasses.dataclass(slots=True, frozen=True, order=True)
class NumberRange:
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError("end number must be equal to or greater than start")

        return None

    @classmethod
    def from_range_length(cls: type[typing.Self], start: int, length: int):
        if length < 1:
            raise ValueError("Length must be a postive of 1 or more")
        end = start + length - 1

        return cls(start, end)

    def number_in_range(self, number: int) -> bool:
        return number >= self.start and number <= self.end

    def is_before(self, other: "NumberRange") -> bool:
        return self.end < other.start

    def is_after(self, other: "NumberRange") -> bool:
        return self.start > other.end

    def overlaps_before(self, other: "NumberRange") -> bool:
        return all(
            (
                self.start < other.start,
                self.end >= other.start,
                self.end <= other.end,
            )
        )

    def overlaps_after(self, other: "NumberRange") -> bool:
        return all(
            (
                self.start >= other.start,
                self.start <= other.end,
                self.end > other.end,
            )
        )

    def overlaps_inside(self, other: "NumberRange") -> bool:
        return all((self.start >= other.start, self.end <= other.end))

    def overlaps_all(self, other: "NumberRange") -> bool:
        return all((self.start < other.start, self.end > other.end))

    def overlaps(self, other: "NumberRange") -> bool:
        return any(
            (
                self.overlaps_before(other),
                self.overlaps_after(other),
                self.overlaps_inside(other),
                self.overlaps_all(other),
            )
        )

    def split_type(self, other: "NumberRange") -> NumberRangeSplitType:
        if self.is_before(other):
            return NumberRangeSplitType.IS_BEFORE
        elif self.is_after(other):
            return NumberRangeSplitType.IS_AFTER
        elif self.overlaps_before(other):
            return NumberRangeSplitType.OVERLAPS_BEFORE
        elif self.overlaps_after(other):
            return NumberRangeSplitType.OVERLAPS_AFTER
        elif self.overlaps_inside(other):
            return NumberRangeSplitType.OVERLAPS_INSIDE
        elif self.overlaps_all(other):
            return NumberRangeSplitType.OVERLAPS_ALL
        else:
            raise ValueError("Unaccounted for relationship")

    def split_overlapping(self, other: "NumberRange") -> list[NumberRangeSplit]:
        number_range_splits: list[NumberRangeSplit] = []
        split_type = self.split_type(other)
        match split_type:
            case NumberRangeSplitType.IS_BEFORE:
                number_range_splits.append(
                    NumberRangeSplit(
                        NumberRangeSplitType.IS_BEFORE,
                        NumberRange(self.start, self.end),
                    )
                )
            case NumberRangeSplitType.IS_AFTER:
                number_range_splits.append(
                    NumberRangeSplit(
                        NumberRangeSplitType.IS_AFTER,
                        NumberRange(self.start, self.end),
                    )
                )
            case NumberRangeSplitType.OVERLAPS_BEFORE:
                split_number = min(self.end, other.start)
                number_range_splits.append(
                    NumberRangeSplit(
                        NumberRangeSplitType.OVERLAPS_BEFORE,
                        NumberRange(self.start, split_number - 1),
                    )
                )
                number_range_splits.append(
                    NumberRangeSplit(
                        NumberRangeSplitType.OVERLAPS_INSIDE,
                        NumberRange(split_number, self.end),
                    )
                )
            case NumberRangeSplitType.OVERLAPS_AFTER:
                split_number = max(self.start, other.end) + 1
                number_range_splits.append(
                    NumberRangeSplit(
                        NumberRangeSplitType.OVERLAPS_INSIDE,
                        NumberRange(self.start, split_number - 1),
                    )
                )
                number_range_splits.append(
                    NumberRangeSplit(
                        NumberRangeSplitType.OVERLAPS_AFTER,
                        NumberRange(split_number, self.end),
                    )
                )
            case NumberRangeSplitType.OVERLAPS_INSIDE:
                number_range_splits.append(
                    NumberRangeSplit(
                        NumberRangeSplitType.OVERLAPS_INSIDE,
                        NumberRange(self.start, self.end),
                    )
                )
            case NumberRangeSplitType.OVERLAPS_ALL:
                split_before_number = min(self.end, other.start)
                split_after_number = max(self.start, other.end) + 1
                number_range_splits.append(
                    NumberRangeSplit(
                        NumberRangeSplitType.OVERLAPS_BEFORE,
                        NumberRange(self.start, split_before_number - 1),
                    )
                )
                number_range_splits.append(
                    NumberRangeSplit(
                        NumberRangeSplitType.OVERLAPS_INSIDE,
                        NumberRange(split_before_number, split_after_number - 1),
                    )
                )
                number_range_splits.append(
                    NumberRangeSplit(
                        NumberRangeSplitType.OVERLAPS_AFTER,
                        NumberRange(split_after_number, self.end),
                    )
                )

        return number_range_splits

    @classmethod
    def merge_ranges(cls, ranges: list["NumberRange"]) -> list["NumberRange"]:
        if not ranges:
            return []

        sorted_ranges = sorted(ranges, key=lambda x: x.start)
        merged_ranges = [sorted_ranges[0]]
        for current_range in sorted_ranges:
            previous_range = merged_ranges[-1]
            if current_range.start - 1 <= previous_range.end:
                new_previous_end = max(previous_range.end, current_range.end)
                merged_ranges[-1] = NumberRange(previous_range.start, new_previous_end)
            elif current_range.start - 1 > previous_range.end:
                merged_ranges.append(current_range)

        return merged_ranges

    def shifted_number_range(self, amount: int) -> "NumberRange":
        return NumberRange(self.start + amount, self.end + amount)


@dataclasses.dataclass(slots=True, frozen=True)
class ConvertedNumberRangeResult:
    converted: list[NumberRange] = dataclasses.field(default_factory=list)
    not_converted: list[NumberRange] = dataclasses.field(default_factory=list)

    def add_converted(self, number_range: NumberRange) -> None:
        self.converted.append(number_range)

        return None

    def add_not_converted(self, number_range: NumberRange) -> None:
        self.not_converted.append(number_range)

        return None


@dataclasses.dataclass(slots=True, frozen=True)
class MapRange:
    destination_range_start: int
    source_range_start: int
    range_length: int

    @property
    def differance(self) -> int:
        return self.destination_range_start - self.source_range_start

    def convert_number_range(
        self, number_range: NumberRange
    ) -> ConvertedNumberRangeResult:
        converted_number_range_result = ConvertedNumberRangeResult()
        source_number_range = NumberRange.from_range_length(
            self.source_range_start, self.range_length
        )
        number_range_splits = number_range.split_overlapping(source_number_range)
        for number_range_split in number_range_splits:
            current_number_range = number_range_split.number_range
            current_split_type = number_range_split.split_type
            if current_split_type == NumberRangeSplitType.OVERLAPS_INSIDE:
                shifted_number_range = current_number_range.shifted_number_range(
                    self.differance
                )
                converted_number_range_result.add_converted(shifted_number_range)
                continue
            converted_number_range_result.add_not_converted(current_number_range)

        return converted_number_range_result


@dataclasses.dataclass(slots=True)
class ConversionMap:
    map_ranges: list[MapRange] = dataclasses.field(default_factory=list)

    def add_map_range(self, map_range: MapRange):
        self.map_ranges.append(map_range)

    def convert_number_ranges(
        self, number_ranges: list[NumberRange]
    ) -> list[NumberRange]:
        new_converted_number_ranges: list[NumberRange] = []
        not_converted_number_ranges: list[NumberRange] = []
        for map_range in self.map_ranges:
            not_converted_number_ranges = []
            for number_range in number_ranges:
                converted_number_ranges = map_range.convert_number_range(number_range)

                for converted_number_range in converted_number_ranges.converted:
                    new_converted_number_ranges.append(converted_number_range)

                for not_converted_number_range in converted_number_ranges.not_converted:
                    not_converted_number_ranges.append(not_converted_number_range)

            number_ranges = not_converted_number_ranges

        new_converted_number_ranges.extend(not_converted_number_ranges)

        return NumberRange.merge_ranges(new_converted_number_ranges)
        return new_converted_number_ranges


@dataclasses.dataclass(slots=True)
class Almanac:
    seeds: list[int] = dataclasses.field(default_factory=list)
    seed_to_soil_map: ConversionMap = dataclasses.field(default_factory=ConversionMap)
    conversion_maps: dict[str, ConversionMap] = dataclasses.field(
        default_factory=dict, init=False
    )

    def __post_init__(self) -> None:
        self.conversion_maps["seed-to-soil map:"] = ConversionMap()
        self.conversion_maps["soil-to-fertilizer map:"] = ConversionMap()
        self.conversion_maps["fertilizer-to-water map:"] = ConversionMap()
        self.conversion_maps["water-to-light map:"] = ConversionMap()
        self.conversion_maps["light-to-temperature map:"] = ConversionMap()
        self.conversion_maps["temperature-to-humidity map:"] = ConversionMap()
        self.conversion_maps["humidity-to-location map:"] = ConversionMap()

    def convert_seed_number_ranges_to_location_number_ranges(
        self, seed_number_range: list[NumberRange], print_: bool = False
    ) -> list[NumberRange]:
        soil_number_ranges = self.conversion_maps[
            "seed-to-soil map:"
        ].convert_number_ranges(seed_number_range)

        fertilizer_number_ranges = self.conversion_maps[
            "soil-to-fertilizer map:"
        ].convert_number_ranges(soil_number_ranges)

        water_number_ranges = self.conversion_maps[
            "fertilizer-to-water map:"
        ].convert_number_ranges(fertilizer_number_ranges)

        light_number_ranges = self.conversion_maps[
            "water-to-light map:"
        ].convert_number_ranges(water_number_ranges)

        temperature_number_ranges = self.conversion_maps[
            "light-to-temperature map:"
        ].convert_number_ranges(light_number_ranges)

        humidity_number_ranges = self.conversion_maps[
            "temperature-to-humidity map:"
        ].convert_number_ranges(temperature_number_ranges)

        location_number_ranges = self.conversion_maps[
            "humidity-to-location map:"
        ].convert_number_ranges(humidity_number_ranges)

        if print_:
            print(
                f"Seed {seed_number_range}, soil {soil_number_ranges}, fertilizer {fertilizer_number_ranges}, water {water_number_ranges}, light {light_number_ranges}, temperature {temperature_number_ranges}, humidity {humidity_number_ranges}, location {location_number_ranges}"
            )

        return location_number_ranges


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
        # print(f"{section} {line}")
        destination_range_start, source_range_start, range_length = line.strip().split(
            " "
        )
        map = almanac.conversion_maps[section]
        map_range = MapRange(
            int(destination_range_start), int(source_range_start), int(range_length)
        )
        map.add_map_range(map_range)

    return almanac


def part_one(almanac: Almanac) -> int:
    seed_number_ranges: list[NumberRange] = []
    for seed_number in almanac.seeds:
        seed_number_ranges.append(NumberRange(seed_number, seed_number))
    seed_number_ranges = almanac.convert_seed_number_ranges_to_location_number_ranges(
        seed_number_ranges
    )
    print(seed_number_ranges)
    minimum_seed_number_range = seed_number_ranges[0]
    return minimum_seed_number_range.start


def part_two(almanac: Almanac) -> int:
    seed_number_ranges: list[NumberRange] = []
    for start, length in itertools.batched(almanac.seeds, n=2):
        seed_number_ranges.append(NumberRange.from_range_length(start, length))
    seed_number_ranges = almanac.convert_seed_number_ranges_to_location_number_ranges(
        seed_number_ranges
    )
    minimum_seed_number_range = seed_number_ranges[0]
    return minimum_seed_number_range.start


def main():
    data = yield_data(FILENAME)
    almanac = create_almanac(data)
    print(f"Part one: {part_one(almanac)}")
    print(f"Part two: {part_two(almanac)}")
    pass


if __name__ == "__main__":
    main()
