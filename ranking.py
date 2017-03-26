from unittest import TestCase, skip
from unittest.mock import Mock
from collections import defaultdict, OrderedDict, Counter

suits = ['s', 'c', 'd', 'h']


def parse_cards(cards):
    rank = {
        '1': 10,
        'J': 11,
        'Q': 12,
        'K': 13,
        'A': 14
    }
    return sorted([(int(rank.get(c[0], (c[0]))), c[-1]) for c in cards], key=lambda x: -x[0])


def parse_and_count_cards(cards):
    pc = parse_cards(cards)
    count = OrderedDict()
    for c in pc:
        try:
            count[c[0]] += 1
        except KeyError:
            count[c[0]] = 1
    return pc, count


def find_high_card(cards):
    """Return the ranks of the (up to) five highest cards, sorted in descending order."""
    return [card[0] for card in parse_cards(cards)][:5]


def find_n_of_a_kind(n, cards):
    """Check if *cards* contain (at least) *n* cards of the same rank. n will be either 2, 3, or 4. If several n-of-a-kinds are found, consider only the one with the highest rank.

    To correctly resolve ties, return a list of the rank of the n-of-a-kind and then ranks of the highest other cards in descending orders.
    For example: [2, 11, 8, 7] where 2 is the rank of the n-of-a-kind, and [11, 8, 7] are the ranks of the highest other cards. The whole list must not consider more than five cards (so this example would be correct for n=2).
    """
    pc, count = parse_and_count_cards(cards)
    for key in count:
        if count[key] >= n:
            return [key] + [card[0] for card in pc if card[0] != key][:(5 - n)]
    return None


def find_two_pairs(cards):
    """If *cards* contain (at least) two pairs, return a triple
    (rank of highest pair, rank of second highest pair, rank of the highest other card)
    If there is no other card, because len(cards) == 4, then just return the pairs' ranks.

    If no two pairs are found, return None.
    """
    pc, count = parse_and_count_cards(cards)
    pairs = []
    for rank in count:
        if count[rank] == 2:
            pairs.append(rank)
        if len(pairs) == 2:
            break
    if len(pairs) < 2:
        return None
    return pairs + [card[0] for card in pc if card[0] not in pairs][:1]


def find_straight(cards):
    """If *cards* contain a straight, return the rank of its highest card. Otherwise return None.
    A straight consists of five cards of sequential rank, e.g. ['2h', '3c', '4d', '5d', '6h']. As a special rule, aces may be used with rank 1, so ['Ac', '2h', '3c', '4d', '5d'] also forms a (lower) straight.
    """
    ranks = list(OrderedDict.fromkeys([rank for rank, suit in parse_cards(cards)]))
    if ranks[0] == 14:
        ranks.append(1)
    if len(ranks) < 5:
        return None
    for i in range(len(ranks)):
        cmp = ranks[i:i+5]
        if len(cmp) < 5:
            continue
        if cmp == list(range(cmp[0], cmp[0]-5, -1)):
            return cmp[0]
    return None


def find_flush(cards):
    """If *cards* contain a flush (five cards of the same suit), return the ranks of its cards, sorted in descending order. Otherwise return None."""
    pc = parse_cards(cards)
    count = defaultdict(int)
    for c in pc:
        count[c[1]] += 1
    for s in suits:
        if count[s] >= 5:
            return [card[0] for card in pc if card[1] == s][:5]
    return None


def find_full_house(cards):
    """If *cards* contain a full house (a triple and a pair), return a tuple (rank of triple, rank of pair) of the cards in the full house. Otherwise return None.
    """
    pc, count = parse_and_count_cards(cards)
    triple = pair = None
    for rank in count:
        if count[rank] == 2 and pair is None:
            pair = rank
        if count[rank] == 3:
            if triple is None:
                triple = rank
            elif pair is None:
                pair = rank
    if triple and pair:
        return [triple, pair]
    return None


def find_straight_flush(cards):
    """If *cards* contain a straight flush (a straight, where all cards are of the same suit), return the rank of its highest card. Otherwise return None.
    """
    suitcount = Counter([suit for rank, suit in parse_cards(cards)])
    for suit, count in suitcount.items():
        if count >= 5:
            return find_straight([c for c in cards if c[-1] == suit])
    return None


def rank_function(cards):
    functions = [
        find_straight_flush,
        lambda x: find_n_of_a_kind(4, x),
        find_full_house,
        find_flush,
        find_straight,
        lambda x: find_n_of_a_kind(3, x),
        find_two_pairs,
        lambda x : find_n_of_a_kind(2, x),
        find_high_card,
    ]

    for i, f in enumerate(functions):
        rank = f(cards)
        if rank:
            return 9 - i, rank


class TestFindHighCard(TestCase):
    def test_empty(self):
        self.assertEqual([], find_high_card([]))

    def test_less_than_five(self):
        cards = parse_cards(['5d', 'Jh', 'As'])
        self.assertEqual([14, 11, 5], find_high_card(cards))

    def test_more_than_five(self):
        cards = parse_cards(['5d', 'Jh', 'As', '10c', '2c', '2d', '4d'])
        self.assertEqual([14, 11, 10, 5, 4], find_high_card(cards))


class TestNOfAKind(TestCase):
    def test_not_found(self):
        cards = parse_cards(['5d', 'Jh', 'As', '10c', '2c', '3d', '4d'])
        self.assertIsNone(find_n_of_a_kind(2, cards))

    def test_one_result(self):
        cards = parse_cards(['5d', 'Jh', 'As', '10c', '2c', '2d', '4d'])
        self.assertEqual([2, 14, 11, 10], find_n_of_a_kind(2, cards))

    def test_two_results(self):
        cards = parse_cards(['5d', '5c', '5h', '2s', '2c', '2d', 'As'])
        self.assertEqual([5, 14, 2], find_n_of_a_kind(3, cards))

    def test_bigger_n(self):
        cards = parse_cards(['5d', 'Jh', 'As', '10c', '5c', '5d', '5d'])
        self.assertEqual([5, 14], find_n_of_a_kind(4, cards))


class TestFindTwoPairs(TestCase):
    def test_not_found(self):
        cards = parse_cards(['5d', 'Jh', 'As', '5c', '2c', '3d', '4d'])
        self.assertIsNone(find_two_pairs(cards))

    def test_found(self):
        cards = parse_cards(['5d', 'Jh', 'As', '5c', '2c', '2d', '4d'])
        self.assertEqual([5, 2, 14], find_two_pairs(cards))

    def test_only_four_cards(self):
        cards = parse_cards(['5d', '5c', '2c', '2d'])
        self.assertEqual([5, 2], find_two_pairs(cards))

    def test_three_pairs(self):
        cards = parse_cards(['5d', '2h', 'As', '5c', '2c', 'Jd', 'Jd'])
        self.assertEqual([11, 5, 14], find_two_pairs(cards))


class TestFindStraight(TestCase):
    def test_not_found(self):
        cards = parse_cards(['4d', '7h', '2s', '5c', '7c', '6d', 'Qd'])
        self.assertIsNone(find_straight(cards))

    def test_with_double(self):
        cards = parse_cards(['4d', '7h', '8s', '5c', '7c', '6d', 'Qd'])
        self.assertEqual(8, find_straight(cards))

    def test_straight_with_six_cards(self):
        cards = parse_cards(['4d', '8h', '3s', '5c', '7c', '6d', 'Qd'])
        self.assertEqual(8, find_straight(cards))

    def test_find_straight_low_ace(self):
        cards = parse_cards(['4d', '8h', '3s', '5c', '2c', '7d', 'Ad'])
        self.assertEqual(5, find_straight(cards))

    def test_dont_use_low_ace_if_better_straight_possible(self):
        cards = parse_cards(['4d', '8h', '3s', '5c', '2c', '6d', 'Ad'])
        self.assertEqual(6, find_straight(cards))

    def test_no_low_king(self):
        cards = parse_cards(['Kd', '8h', '3s', '4c', '2c', '7d', 'Ad'])
        self.assertIsNone(find_straight(cards))


class TestFindFlush(TestCase):
    def test_not_found(self):
        cards = parse_cards(['10d', '8d', '3c', '5h', 'Qd', '7d', 'As'])
        self.assertIsNone(find_flush(cards))

    def test_find_flush(self):
        cards = parse_cards(['10d', '8d', '3d', '5d', 'Qd', 'As'])
        self.assertEqual([12, 10, 8, 5, 3], find_flush(cards))

    def test_more_than_five_cards(self):
        cards = parse_cards(['10d', '8d', '3d', '5d', 'Qd', '7d', 'As'])
        self.assertEqual([12, 10, 8, 7, 5], find_flush(cards))


class TestFindFullHouse(TestCase):
    def test_no_triple(self):
        cards = parse_cards(['10d', '10s', '3c', '3h', 'Qd', '7d', 'As'])
        self.assertIsNone(find_full_house(cards))

    def test_no_pair(self):
        cards = parse_cards(['10d', '10s', '3c', '10h', 'Qd', '7d', 'As'])
        self.assertIsNone(find_full_house(cards))

    def test_find_full_house(self):
        cards = parse_cards(['10d', '10s', '3d', '5d', '3h', '3c', 'As'])
        self.assertEqual([3, 10], find_full_house(cards))

    def test_choose_best(self):
        cards = parse_cards(['10d', '10s', '3d', 'Qd', '3h', '3c', 'Qs'])
        self.assertEqual([3, 12], find_full_house(cards))

    def two_triples(self):
        cards = parse_cards(['10d', '10s', '10h', '3d', '3h', 'Qc', '3s'])
        self.assertEqual([3, 12], find_full_house(cards))


class TestFindStraightFlush(TestCase):
    def test_no_flush(self):
        cards = parse_cards(['2d', '3d', '4s', '5c', '6d', '7d', '8d'])
        self.assertIsNone(find_straight_flush(cards))

    def test_no_straight(self):
        cards = parse_cards(['10d', '10d', '3d', '3d', 'Qd', '7d', 'Ad'])
        self.assertIsNone(find_straight_flush(cards))

    def test_find_straight_flush(self):
        cards = parse_cards(['2d', '3d', '4d', '5d', '6d', '7d', '8c'])
        self.assertEqual(7, find_straight_flush(cards))

    def test_with_low_ace(self):
        cards = parse_cards(['2d', '3d', '4d', '5d', '6c', '7c', 'Ad'])
        self.assertEqual(5, find_straight_flush(cards))


class TestRanking(TestCase):
    def test_ranking(self):
        # In particular check cases where two rankings apply (e.g. Full House and Flush)
        card_sets = [
            # Straight Flush
            ['As', 'Ks', 'Qs', 'Js', '10s', '2c', '3c'],
            ['Ks', 'Qs', 'Js', '10s', '9s', '2c', '3c'],
            # 4 of a kind
            ['10s', '10d', '10c', '10h', 'As', '2c', '2d'],
            ['10s', '10d', '10c', '10h', 'Ks', '2c', '2d'],
            # Full House
            ['As', 'Ad', 'Ah', 'Kh', 'Ks', '2c', '2d'],
            ['3s', '3d', '3h', 'Kh', 'Ks', '2c', '2d'],
            # Flush
            ['3s', 'Ks', '4s', '10s', '7s', '2c', '2d'],
            ['3s', 'Qs', '4s', '10s', '7s', '2c', '2d'],
            # Straight
            ['3s', '4d', '5h', '6d', '7c', '2c', '2d'],
            ['As', '2c', '3s', '4d', '5h', '7c', '2d'],
            # 3 of a kind
            ['10s', '10d', '10c', 'Ah', 'Ks', '3c', '2d'],
            ['10s', '10d', '10c', 'Ah', 'Qs', '3c', '2d'],
            # Two Pairs
            ['10s', '10d', 'Kh', '4c', '4c', '2h', '6d'],
            ['10s', '10d', 'Ah', '3c', '3c', '2h', '6d'],
            ['10s', '10d', '4h', '3c', '3c', '2h', '6d'],
            # 2 of a kind
            ['10s', '10d', 'Ah', '4c', '5c', '2h', '6d'],
            ['10s', '10d', 'Kh', '3c', '5c', '2h', '6d'],
            # High card
            ['Qs', '10d', 'Ah', '3c', '5c', '2h', '6d'],
            ['Qs', '10d', 'Kh', '3c', '5c', '2h', '6d'],
        ]

        ranks = [rank_function(c) for c in card_sets]
        for rank, card_set in zip(ranks, card_sets):
            print(rank, card_set)

        sorted_card_sets = sorted(card_sets, key=rank_function, reverse=True)
        self.assertListEqual(card_sets, sorted_card_sets)
