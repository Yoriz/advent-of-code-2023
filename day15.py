import typing


TEST_FILENAME = "day15_testdata.txt"
FILENAME = "day15_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


def ascii_code(value: int, character: str) -> int:
    value_plus_char_ascii = value + ord(character)
    multiplied_value = value_plus_char_ascii * 17
    remainder = multiplied_value % 256
    return remainder


def score_sequence(characters: str) -> int:
    value = 0
    for character in characters:
        value = ascii_code(value, character)
    # print(f"{characters} becomes {value}.")
    return value


def create_sequences(data: typing.Iterator) -> typing.Iterator[str]:
    line = next(data)
    for sequence in line.split(","):
        yield sequence


def part_one() -> int:
    total = 0
    data = yield_data(FILENAME)
    for sequence in create_sequences(data):
        score = score_sequence(sequence)
        total += score

    return total


def part_two() -> int:
    return 0


def main():
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
