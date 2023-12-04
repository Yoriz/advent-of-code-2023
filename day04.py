import collections
import typing

TEST_FILENAME = "day4_testdata.txt"
FILENAME = "day4_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


def parse_scratch_card_line(line: str) -> tuple[str, list[str], list[str]]:
    line = line.replace("  ", " ")
    card_number, numbers = line.split(":")
    numbers1, numbers2 = numbers.strip().split("|")
    winning_numbers = numbers1.strip().split(" ")
    scratch_card_numbers = numbers2.strip().split(" ")
    return card_number, winning_numbers, scratch_card_numbers


def score_scratch_card(
    winning_numbers: list[str], scratch_card_numbers: list[str]
) -> int:
    score = 0
    for number in scratch_card_numbers:
        if number in winning_numbers:
            if not score:
                score = 1
            else:
                score *= 2
    return score


def part_one() -> int:
    data = yield_data(FILENAME)
    total_score = 0
    for line in data:
        card_number, winning_numbers, scratch_card_numbers = parse_scratch_card_line(
            line
        )
        score = score_scratch_card(winning_numbers, scratch_card_numbers)
        total_score += score
    return total_score


def scratch_card_wins(
    winning_numbers: list[str], scratch_card_numbers: list[str]
) -> int:
    wins = 0
    for number in scratch_card_numbers:
        if number in winning_numbers:
            wins += 1
    return wins


def part_two():
    data = yield_data(FILENAME)
    copies = collections.Counter()
    orignal_amount = 0
    for number, line in enumerate(data, 1):
        orignal_amount += 1
        card_number, winning_numbers, scratch_card_numbers = parse_scratch_card_line(
            line
        )
        wins = scratch_card_wins(winning_numbers, scratch_card_numbers)
        for copy_number in range(number + 1, number + 1 + wins):
            copies[copy_number] += 1 + copies[number]
    total_amount = 0
    for card_number in range(1, orignal_amount + 1):
        total_amount += 1 + copies[card_number]
    return total_amount


def main():
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
