import dataclasses
import typing

TEST_FILENAME = "day6_testdata.txt"
FILENAME = "day6_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


@dataclasses.dataclass
class Race:
    time: int = 0
    record_distance: int = 0

    def calculate_distance(self, hold_time: int) -> int:
        if hold_time >= self.time or hold_time <= 0:
            return 0
        return (self.time - hold_time) * hold_time

    def is_distance_new_record(self, distance: int) -> bool:
        return distance > self.record_distance

    def number_of_ways_to_beat_record(self) -> int:
        number_of_ways = 0
        middle = self.time // 2
        # print(middle)
        for time in range(middle, 0, -1):
            new_distance = self.calculate_distance(time)
            if self.is_distance_new_record(new_distance):
                number_of_ways += 1
            else:
                break

        for time in range(middle + 1, self.time + 1):
            new_distance = self.calculate_distance(time)
            if self.is_distance_new_record(new_distance):
                number_of_ways += 1
            else:
                break

        return number_of_ways


def create_races(data: typing.Iterator) -> list[Race]:
    races: list[Race] = []
    time_line = next(data)
    times = [int(time) for time in time_line.split(":")[1].split(" ") if time != ""]
    distance_line = next(data)
    distances = [
        int(distance)
        for distance in distance_line.split(":")[1].split(" ")
        if distance != ""
    ]
    for time, distance in zip(times, distances):
        race = Race(time, distance)
        races.append(race)
    return races


def part_one(races: list[Race]) -> int:
    result = 0
    for race in races:
        number_of_ways = race.number_of_ways_to_beat_record()
        if not result:
            result = number_of_ways
        else:
            result *= number_of_ways
    return result


def part_two(races: list[Race]) -> int:
    time = ""
    record_distance = ""
    for race in races:
        time = f"{time}{race.time}"
        record_distance = f"{record_distance}{race.record_distance}"

    race = Race(int(time), int(record_distance))
    return race.number_of_ways_to_beat_record()


def main():
    data = yield_data(FILENAME)
    races = create_races(data)
    print(f"Part one: {part_one(races)}")
    print(f"Part two: {part_two(races)}")


if __name__ == "__main__":
    main()
