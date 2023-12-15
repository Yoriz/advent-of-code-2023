import dataclasses
import enum
import typing
import collections

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

    return value


class SequenceOperation(enum.Enum):
    REMOVE = "-"
    ADD = "="


@dataclasses.dataclass
class Sequence:
    characters: str

    @property
    def score(self) -> int:
        return score_sequence(self.characters)

    @property
    def operation(self) -> SequenceOperation:
        if SequenceOperation.REMOVE.value in self.characters:
            return SequenceOperation.REMOVE
        elif SequenceOperation.ADD.value in self.characters:
            return SequenceOperation.ADD
        raise ValueError("No SequenceOperation found")

    @property
    def label(self) -> str:
        label, _ = self.characters.split(self.operation.value)
        return label

    @property
    def label_score(self) -> int:
        return score_sequence(self.label)

    @property
    def focal_length(self) -> int:
        if self.operation == SequenceOperation.REMOVE:
            return 0
        _, length = self.characters.split(SequenceOperation.ADD.value)

        return int(length)


def create_sequences(data: typing.Iterator) -> typing.Iterator[Sequence]:
    line = next(data)
    for characters in line.split(","):
        yield Sequence(characters)


def create_deque_default_dict() -> (
    collections.defaultdict[int, collections.deque[Sequence]]
):
    return collections.defaultdict(collections.deque)


@dataclasses.dataclass
class Boxes:
    containers: collections.defaultdict[
        int, collections.deque[Sequence]
    ] = dataclasses.field(default_factory=create_deque_default_dict)

    def process_sequence(self, sequence: Sequence) -> None:
        match sequence.operation:
            case SequenceOperation.ADD:
                self.sequnce_operation_add(sequence)
            case SequenceOperation.REMOVE:
                self.sequence_operation_remove(sequence)

    def sequnce_operation_add(self, sequence: Sequence) -> None:
        box_number = sequence.label_score
        box = self.containers[box_number]
        for index, box_sequence in enumerate(box.copy()):
            if box_sequence.label == sequence.label:
                box[index] = sequence
                return

        box.append(sequence)

    def sequence_operation_remove(self, sequence: Sequence) -> None:
        box_number = sequence.label_score
        if box_number not in self.containers:
            return
        box = self.containers[box_number]
        for index, box_sequence in enumerate(box.copy()):
            if box_sequence.label == sequence.label:
                del box[index]
        if len(box) == 0:
            del self.containers[box_number]

    def focusing_power(self) -> int:
        total = 0
        for box_number, box in self.containers.items():
            for slot_number, slot in enumerate(box, 1):
                power = (1 + box_number) * slot_number * slot.focal_length
                # print(
                #     (
                #         f"{slot.label}: {1 + box_number} (box {box_number}) * "
                #         f"{slot_number} (nth slot) * {slot.focal_length} "
                #         f"(focal length) = {power}"
                #     )
                # )
                total += power

        return total


def part_one() -> int:
    data = yield_data(FILENAME)
    total = 0
    for sequence in create_sequences(data):
        score = sequence.score
        total += score

    return total


def part_two() -> int:
    data = yield_data(FILENAME)
    boxes = Boxes()
    for sequence in create_sequences(data):
        boxes.process_sequence(sequence)

    total = boxes.focusing_power()
    return total


def main():
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")



if __name__ == "__main__":
    main()
