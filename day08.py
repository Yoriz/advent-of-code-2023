import dataclasses
import enum
import itertools
import math
import typing

TEST_FILENAME = "day8_testdata.txt"
FILENAME = "day8_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class Direction(enum.Enum):
    LEFT = "L"
    RIGHT = "R"

    @staticmethod
    def get_direction(letter: str):
        return {"L": Direction.LEFT, "R": Direction.RIGHT}[letter]


@dataclasses.dataclass
class Node:
    name: str
    left: str
    right: str

    def navigate(self, direction: Direction) -> str:
        return {Direction.LEFT: self.left, Direction.RIGHT: self.right}[direction]


@dataclasses.dataclass
class Map:
    directions: tuple[Direction, ...]
    nodes: dict[str, Node] = dataclasses.field(default_factory=dict)

    def add_node(self, node: Node) -> None:
        self.nodes[node.name] = node

    def starting_nodes(self) -> list[Node]:
        return [node for node in self.nodes.values() if node.name[2] == "A"]

    def navigate_to_ZZZ(self) -> int:
        steps = 0
        current_node = self.nodes["AAA"]
        for direction in itertools.cycle(self.directions):
            destination_str = current_node.navigate(direction)
            destination_node = self.nodes[destination_str]
            steps += 1
            if destination_node.name == "ZZZ":
                break
            current_node = destination_node
        return steps

    def navigate_starting_nodes_to_all_ending_Z(self) -> int:
        steps = 0
        current_nodes = self.starting_nodes()
        steps_to_end_node: list[int] = []
        for direction in itertools.cycle(self.directions):
            destination_nodes: list[Node] = []
            if not current_nodes:
                break
            steps += 1
            for current_node in current_nodes:
                destination_str = current_node.navigate(direction)
                destination_node = self.nodes[destination_str]
                if destination_node.name[2] == "Z":
                    steps_to_end_node.append(steps)
                else:
                    destination_nodes.append(destination_node)

            current_nodes = destination_nodes
            print(" ".join(node.name for node in current_nodes))

        steps = math.lcm(*steps_to_end_node)
        return steps


def create_map(data) -> Map:
    directions = tuple(Direction.get_direction(direction) for direction in next(data))
    map = Map(directions)
    next(data)
    for line in data:
        start_node = line[:3]
        left_node = line[7:10]
        right_node = line[12:-1]
        node = Node(start_node, left_node, right_node)
        map.add_node(node)
    return map


def part_one(map: Map) -> int:
    steps = map.navigate_to_ZZZ()
    return steps


def part_two(map: Map) -> int:
    steps = map.navigate_starting_nodes_to_all_ending_Z()
    return steps


def main():
    data = yield_data(FILENAME)
    map = create_map(data)

    print(f"Part one: {part_one(map)}")
    print(f"Part two: {part_two(map)}")


if __name__ == "__main__":
    main()
