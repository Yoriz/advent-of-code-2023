import dataclasses
import enum
import operator
import typing

TEST_FILENAME = "day19_testdata.txt"
FILENAME = "day19_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class PartStatus(enum.Enum):
    REJECTED = "R"
    ACCEPTED = "A"


class PartCategory(enum.Enum):
    X = "x"
    M = "m"
    A = "a"
    S = "s"


part_category_convertor = {
    PartCategory.X.value: PartCategory.X,
    PartCategory.M.value: PartCategory.M,
    PartCategory.A.value: PartCategory.A,
    PartCategory.S.value: PartCategory.S,
}


class Operator(enum.Enum):
    GT = ">"
    LT = "<"


operator_convertor = {Operator.GT.value: Operator.GT, Operator.LT.value: Operator.LT}


@dataclasses.dataclass(slots=True)
class Part:
    x: int
    m: int
    a: int
    s: int

    @property
    def total_rating(self) -> int:
        total = sum((self.x, self.m, self.a, self.s))

        return total


def create_part(string: str) -> Part:
    parts_strings = string[1:-1].split(",")
    _, x = parts_strings[0].split("=")
    _, m = parts_strings[1].split("=")
    _, a = parts_strings[2].split("=")
    _, s = parts_strings[3].split("=")
    part = Part(int(x), int(m), int(a), int(s))

    return part


@dataclasses.dataclass(slots=True)
class Rule:
    part_category: PartCategory
    operator: Operator
    value: int
    destination: str

    def check(self, part: Part) -> str | None:
        part_dict = dataclasses.asdict(part)
        other_value = part_dict[self.part_category.value]
        match self.operator:
            case Operator.GT:
                if operator.gt(other_value, self.value):
                    return self.destination
            case Operator.LT:
                if operator.lt(other_value, self.value):
                    return self.destination

        return None


def create_rule(string: str) -> Rule:
    part_category = part_category_convertor[string[0]]
    operator_ = operator_convertor[string[1]]
    number_str, destination = string[2:].split(":")
    rule = Rule(part_category, operator_, int(number_str), destination)

    return rule


@dataclasses.dataclass(slots=True)
class WorkFlow:
    otherwise: str
    rules: list[Rule] = dataclasses.field(default_factory=list)

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

        return None

    def perform_rules(self, part: Part) -> str:
        for rule in self.rules:
            result = rule.check(part)
            if result:
                return result

        return self.otherwise


def create_workflow(string: str) -> WorkFlow:
    workflows = string.split(",")
    workflow = WorkFlow(workflows[-1])
    for workflow_str in workflows[:-1]:
        rule = create_rule(workflow_str)
        workflow.add_rule(rule)

    return workflow


@dataclasses.dataclass(slots=True)
class System:
    workflows: dict[str, WorkFlow] = dataclasses.field(default_factory=dict)
    parts: list[Part] = dataclasses.field(default_factory=list)

    def add_workflow(self, workflow_name: str, workflow: WorkFlow) -> None:
        self.workflows[workflow_name] = workflow

        return None

    def add_part(self, part: Part) -> None:
        self.parts.append(part)

        return None

    def check_part(self, part: Part) -> PartStatus:
        name = "in"
        while True:
            workflow = self.workflows[name]
            result = workflow.perform_rules(part)
            match result:
                case PartStatus.ACCEPTED.value:
                    return PartStatus.ACCEPTED
                case PartStatus.REJECTED.value:
                    return PartStatus.REJECTED
                case _:
                    name = result

    def check_parts(self) -> list[PartStatus]:
        parts_status: list[PartStatus] = []
        for part in self.parts:
            result = self.check_part(part)
            parts_status.append(result)

        return parts_status


def create_system(data: typing.Iterator) -> System:
    system = System()
    rules = True
    for line in data:
        if not line:
            rules = False
            continue
        if rules:
            workflow_name, workflow_str = line[:-1].split("{")
            workflow = create_workflow(workflow_str)
            system.add_workflow(workflow_name, workflow)
            continue
        part = create_part(line)
        system.add_part(part)

    return system


def part_one() -> int:
    total = 0
    data = yield_data(FILENAME)
    system = create_system(data)
    results = system.check_parts()
    for part, result in zip(system.parts, results):
        if result == PartStatus.ACCEPTED:
            total += part.total_rating

    return total


def part_two() -> int:
    return 0


def main():
    print(f"Part one: {part_one()}")
    # print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
