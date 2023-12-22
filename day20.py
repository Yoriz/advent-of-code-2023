import collections
import dataclasses
import enum
import typing

TEST_FILENAME = "day20_testdata.txt"
FILENAME = "day20_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class PulseType(enum.Enum):
    HIGH = enum.auto()
    LOW = enum.auto()


@dataclasses.dataclass(slots=True)
class Pulse:
    sent_name: str
    type: PulseType
    destinations: list[str] = dataclasses.field(default_factory=list)


class ModuleProtocol(typing.Protocol):
    name: str
    destinations: list[str]

    def process_pulse(self, pulse: Pulse) -> typing.Optional[Pulse]:
        ...


@dataclasses.dataclass(slots=True)
class FlipFlop:
    name: str
    destinations: list[str] = dataclasses.field(default_factory=list)
    _on: bool = dataclasses.field(init=False, default=False)

    def process_pulse(self, pulse: Pulse) -> typing.Optional[Pulse]:
        match pulse.type:
            case PulseType.LOW if not self._on:
                self._on = True
                return Pulse(self.name, PulseType.HIGH, self.destinations)
            case PulseType.LOW if self._on:
                self._on = False
                return Pulse(self.name, PulseType.LOW, self.destinations)
            case PulseType.HIGH:
                return None


@dataclasses.dataclass(slots=True)
class Conjunction:
    name: str
    destinations: list[str] = dataclasses.field(default_factory=list)
    _recent_pulses: dict[str, PulseType] = dataclasses.field(
        init=False, default_factory=dict
    )

    def add_connected_module(self, module_name: str):
        self._recent_pulses[module_name] = PulseType.LOW

    def process_pulse(self, pulse: Pulse) -> typing.Optional[Pulse]:
        self._recent_pulses[pulse.sent_name] = pulse.type

        if all(
            (
                pulse_type == PulseType.HIGH
                for pulse_type in self._recent_pulses.values()
            )
        ):
            return Pulse(self.name, PulseType.LOW, self.destinations)

        return Pulse(self.name, PulseType.HIGH, self.destinations)


@dataclasses.dataclass(slots=True)
class Broadcaster:
    name: str = "broadcaster"
    destinations: list[str] = dataclasses.field(default_factory=list)

    def process_pulse(self, pulse: Pulse) -> typing.Optional[Pulse]:
        return Pulse(self.name, pulse.type, self.destinations)


@dataclasses.dataclass(slots=True)
class Button:
    name: str = "Button"

    def process_pulse(self) -> Pulse:
        return Pulse(self.name, PulseType.LOW, ["broadcaster"])


@dataclasses.dataclass(slots=True)
class Output:
    name: str = "output"
    destinations: list[str] = dataclasses.field(default_factory=list)

    def process_pulse(self, pulse: Pulse) -> typing.Optional[Pulse]:
        # print(f"Output: {pulse=}")

        return None


@dataclasses.dataclass(slots=True)
class HeadQuaters:
    pulses: collections.deque[Pulse] = dataclasses.field(
        default_factory=collections.deque
    )
    modules: dict[str, ModuleProtocol] = dataclasses.field(default_factory=dict)

    def add_module(self, module_name: str, module: ModuleProtocol) -> None:
        self.modules[module_name] = module

        return None

    def press_button(self, print_: bool = False) -> tuple[int, int]:
        pulse = Button().process_pulse()
        self.pulses.append(pulse)
        count = 0
        low_pulses_count = 0
        high_pulses_count = 0
        while True:
            # if count == 13:
            #     break
            if len(self.pulses) == 0:
                if print_:
                    print("Pulses exhausted")
                break
            count += 1
            pulse = self.pulses.popleft()
            if pulse.type == PulseType.HIGH:
                high_pulses_count += 1
            else:
                low_pulses_count += 1
            if print_:
                print(pulse)
            for destination in pulse.destinations:
                module = self.modules[destination]
                recieved_pulse = module.process_pulse(pulse)
                if recieved_pulse:
                    for destination in recieved_pulse.destinations:
                        self.pulses.append(
                            Pulse(module.name, recieved_pulse.type, [destination])
                        )

        return low_pulses_count, high_pulses_count


def create_headquaters(data: typing.Iterator[str]) -> HeadQuaters:
    headquaters = HeadQuaters()
    conjuntions: dict[str, Conjunction] = {}
    for line in data:
        moduletype_name, destinations_str = line.split(" -> ")
        module_type = moduletype_name[0]
        name = moduletype_name[1:]
        destinations = destinations_str.split(", ") or [destinations_str]
        match module_type:
            case "b":
                broadcaster = Broadcaster(destinations=destinations)
                headquaters.add_module(broadcaster.name, broadcaster)
            case "%":
                flip_flop = FlipFlop(name, destinations)
                headquaters.add_module(name, flip_flop)
            case "&":
                conjunction = Conjunction(name, destinations)
                headquaters.add_module(name, conjunction)
                conjuntions[name] = conjunction

    for module in headquaters.modules.values():
        for destination_name in module.destinations:
            if destination_name in conjuntions.keys():
                conjunction = conjuntions[destination_name]
                conjunction.add_connected_module(module.name)
    output = Output()
    headquaters.add_module(output.name, output)
    rx_output = Output("rx")
    headquaters.add_module(rx_output.name, rx_output)
    return headquaters


def part_one() -> int:
    data = yield_data(FILENAME)
    headquaters = create_headquaters(data)
    total_low_pulses = 0
    total_high_pulses = 0
    for press in range(1, 1000 + 1):  # 8 times
        print(f"{press=}")
        low_pulses_count, high_pulses_count = headquaters.press_button()
        total_low_pulses += low_pulses_count
        total_high_pulses += high_pulses_count

    total = total_low_pulses * total_high_pulses
    return total  # 737343750 is too low


def part_two() -> int:
    return 0


def main():
    print(f"Part one: {part_one()}")
    # print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
