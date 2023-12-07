import collections
import dataclasses
import enum
import itertools
import typing

TEST_FILENAME = "day7_testdata.txt"
FILENAME = "day7_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class CardType(enum.Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class HandType(enum.Enum):
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    FULL_HOUSE = 5
    FOUR_OF_A_KIND = 6
    FIVE_OF_A_KIND = 7


string_to_card_type = {
    "2": CardType.TWO,
    "3": CardType.THREE,
    "4": CardType.FOUR,
    "5": CardType.FIVE,
    "6": CardType.SIX,
    "7": CardType.SEVEN,
    "8": CardType.EIGHT,
    "9": CardType.NINE,
    "T": CardType.TEN,
    "J": CardType.JACK,
    "Q": CardType.QUEEN,
    "K": CardType.KING,
    "A": CardType.ACE,
}


@dataclasses.dataclass
class Card:
    card_type: CardType
    string: str

    def __lt__(self, other: "Card") -> bool:
        return self.card_type.value < other.card_type.value


@dataclasses.dataclass
class Hand:
    cards: list[Card] = dataclasses.field(default_factory=list)
    bid: int = 0

    def type(self) -> HandType:
        counter = collections.Counter("".join(card.string for card in self.cards))
        print(tuple(sorted(counter.values(), reverse=True)))
        match tuple(sorted(counter.values(), reverse=True)):
            case (5,):
                return HandType.FIVE_OF_A_KIND
            case (4, 1):
                return HandType.FOUR_OF_A_KIND
            case (3, 2):
                return HandType.FULL_HOUSE
            case (3, 1, 1):
                return HandType.THREE_OF_A_KIND
            case (2, 2, 1):
                return HandType.TWO_PAIR
            case (2, 1, 1, 1):
                return HandType.ONE_PAIR
            case _:
                return HandType.HIGH_CARD

    def __lt__(self, other: "Hand") -> bool:
        for card, othercard in zip(self.cards, other.cards):
            if card == othercard:
                continue
            return card < othercard

        print("Not sure so returning false")
        return False

    def __str__(self) -> str:
        return f"{" ".join(card.string for card in self.cards)} {self.bid}"


@dataclasses.dataclass
class HandTypeCollection:
    five_of_a_kind: list[Hand] = dataclasses.field(default_factory=list)
    four_of_a_kind: list[Hand] = dataclasses.field(default_factory=list)
    full_house: list[Hand] = dataclasses.field(default_factory=list)
    three_of_a_kind: list[Hand] = dataclasses.field(default_factory=list)
    two_pair: list[Hand] = dataclasses.field(default_factory=list)
    one_pair: list[Hand] = dataclasses.field(default_factory=list)
    high_card: list[Hand] = dataclasses.field(default_factory=list)

    def add_hand(self, hand: Hand) -> None:
        match hand.type():
            case HandType.FIVE_OF_A_KIND:
                self.five_of_a_kind.append(hand)
            case HandType.FOUR_OF_A_KIND:
                self.four_of_a_kind.append(hand)
            case HandType.FULL_HOUSE:
                self.full_house.append(hand)
            case HandType.THREE_OF_A_KIND:
                self.three_of_a_kind.append(hand)
            case HandType.TWO_PAIR:
                self.two_pair.append(hand)
            case HandType.ONE_PAIR:
                self.one_pair.append(hand)
            case HandType.HIGH_CARD:
                self.high_card.append(hand)

    def sort_collections(self) -> None:
        self.five_of_a_kind.sort()
        self.four_of_a_kind.sort()
        self.full_house.sort()
        self.three_of_a_kind.sort()
        self.two_pair.sort()
        self.one_pair.sort()
        self.high_card.sort()


def create_card(card_str: str) -> Card:
    return Card(string_to_card_type[card_str], card_str)


def create_hands(data: typing.Iterator) -> list[Hand]:
    hands: list[Hand] = []
    for line in data:
        cards_str, bid_str = line.split(" ")
        cards = [create_card(card_str) for card_str in cards_str]
        hand = Hand(cards, int(bid_str))
        hands.append(hand)

    return hands


def part_one(hands: list[Hand]) -> int:
    hand_type_collection = HandTypeCollection()
    for hand in hands:
        hand_type_collection.add_hand(hand)
    hand_type_collection.sort_collections()
    rank = 1
    total_winning = 0

    for hand in itertools.chain(
        hand_type_collection.high_card,
        hand_type_collection.one_pair,
        hand_type_collection.two_pair,
        hand_type_collection.three_of_a_kind,
        hand_type_collection.full_house,
        hand_type_collection.four_of_a_kind,
        hand_type_collection.five_of_a_kind,
    ):
        total_winning += hand.bid * rank
        rank += 1

    for hand in hand_type_collection.full_house:
        print(hand)

    return total_winning


def part_two() -> int:
    return 0


def main():
    data = yield_data(FILENAME)
    hands = create_hands(data)
    print(f"Part one: {part_one(hands)}")
    # print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
