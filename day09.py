import dataclasses
import typing

TEST_FILENAME = "day9_testdata.txt"
FILENAME = "day9_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


@dataclasses.dataclass
class Sequence:
    values: list[int] = dataclasses.field(default_factory=list)
    values_history: list[list[int]] = dataclasses.field(default_factory=list)

    def create_next_values_history(self) -> None:
        if self.values_history:
            values = self.values_history[-1]
        else:
            values = self.values
        first_value = values[0]
        new_values: list[int] = []
        for second_value in values[1:]:
            new_values.append(second_value - first_value)
            first_value = second_value
        self.values_history.append(new_values)

    def last_value_history_is_all_zeros(self) -> bool:
        last_values_history = self.values_history[-1]
        for value in last_values_history:
            if value != 0:
                return False
        return True

    def create_all_values_history(self) -> None:
        loops = 1
        while True:
            self.create_next_values_history()
            if self.last_value_history_is_all_zeros():
                break
            loops += 1
            if loops // 1000 == 1:
                print(f"<create_all_values_history> reached {loops} loops")

    def extrapolate_history(self) -> None:
        self.values_history[-1].append(0)
        values_history_length = len(self.values_history) - 1
        for index in range(values_history_length, 0, -1):
            current_values_history = self.values_history[index]
            previous_values_history = self.values_history[index - 1]
            new_value = previous_values_history[-1] + current_values_history[-1]
            previous_values_history.append(new_value)
        first_values_history = self.values_history[0]
        new_value = self.values[-1] + first_values_history[-1]
        self.values.append(new_value)


def create_sequences(data: typing.Iterator) -> list[Sequence]:
    sequences: list[Sequence] = []
    for line in data:
        values = [int(number) for number in line.split(" ")]
        sequences.append(Sequence(values))
    return sequences


def part_one(sequences: list[Sequence]) -> int:
    total = 0
    for sequence in sequences:
        sequence.create_all_values_history()
        sequence.extrapolate_history()
        total += sequence.values[-1]
    return total


def part_two() -> int:
    return 0


def main():
    data = yield_data(FILENAME)
    sequences = create_sequences(data)
    print(f"Part one: {part_one(sequences)}")
    # print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
