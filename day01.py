from typing import Iterator

ONE = "one"
TWO = "two"
THREE = "three"
FOOR = "four"
FIVE = "five"
SIX = "six"
SEVEN = "seven"
EIGHT = "eight"
NINE = "nine"

"""
for reference overlaps
oneight
twone
threeight
fiveight
sevenine
eightwo
eighthree
nineight
"""

numbers = (ONE, TWO, THREE, FOOR, FIVE, SIX, SEVEN, EIGHT, NINE)


TEST_FILENAME = "day1_testdata.txt"
FILENAME = "day1_data.txt"


def yield_data(filename: str) -> Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


def first_digit(line, reverse=False):
    if reverse:
        line = reversed(line)
    for character in line:
        if character.isdigit():
            return character


def starting_number(line):
    if line[0].isdigit():
        return int(line[0])
    for number_index, number in enumerate(numbers, 1):
        if line.startswith(number):
            return int(number_index)
    return None


def convert_string_numbers(line: str):  # doesnt work with overlaping words
    while True:
        locations = []
        for number_index, number in enumerate(numbers, 1):
            index = line.find(number)
            if index != -1:
                locations.append((index, number, str(number_index)))
        locations.sort()
        if not locations:
            return line
        line = line.replace(locations[0][1], locations[0][2])


def part_one():
    data = yield_data(FILENAME)
    calibration_values = []
    for line in data:
        calibration_values.append(
            int(f"{first_digit(line, False)}{first_digit(line, True)}")
        )
    return sum(calibration_values)


def part_two():
    data = yield_data(FILENAME)
    calibration_values = []
    for line in data:
        line_numbers = []
        for index, _ in enumerate(line):
            number = starting_number(line[index:])
            if number:
                line_numbers.append(number)
        calibration_values.append(int(f"{line_numbers[0]}{line_numbers[-1]}"))
    return sum(calibration_values)


def main():
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
