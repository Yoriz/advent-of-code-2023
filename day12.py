import dataclasses
import itertools
import typing
import collections


TEST_FILENAME = "day12_testdata.txt"
FILENAME = "day12_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


OPERATIONAL = "."
BROKEN = "#"
UNKNOWN = "?"


@dataclasses.dataclass
class ConditionRecord:
    springs: str
    contiguous_groups: list[int] = dataclasses.field(default_factory=list)

    def possible_arrangements(self) -> list[str]:
        arrangements: list[str] = []
        counter = collections.Counter(self.springs)
        amount = counter[UNKNOWN]
        for values in itertools.product(("#", "."), repeat=amount):
            springs_copy = self.springs
            for value in values:
                springs_copy = springs_copy.replace("?", value, 1)
            if springs_match_contiguous_groups(springs_copy, self.contiguous_groups):
                arrangements.append(springs_copy)

        return arrangements


def springs_match_contiguous_groups(springs: str, contiguous_groups: list[int]) -> bool:
    contiguous_count = 0
    test_group = []
    for spring in springs:
        if spring == BROKEN and contiguous_count == 0:
            contiguous_count = 1
            continue
        if spring == BROKEN and contiguous_count > 0:
            contiguous_count += 1
            continue
        if spring == OPERATIONAL and contiguous_count > 0:
            test_group.append(contiguous_count)
            contiguous_count = 0
    if contiguous_count > 0:
        test_group.append(contiguous_count)
    return test_group == contiguous_groups


def create_condition_records(data: typing.Iterator) -> list[ConditionRecord]:
    condition_records: list[ConditionRecord] = []
    for line in data:
        springs, contiguous_str = line.split(" ")
        contiguous_groups = [int(item) for item in contiguous_str.split(",")]
        condition_record = ConditionRecord(springs, contiguous_groups)
        condition_records.append(condition_record)

    return condition_records


def part_one() -> int:
    data = yield_data(FILENAME)
    condition_records = create_condition_records(data)
    total = 0
    for record in condition_records:
        arrangments = record.possible_arrangements()
        total += len(arrangments)
    return total


def part_two() -> int:
    return 0


def main():
    print(f"Part one: {part_one()}")
    # print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
