import pytest

from nfa import char
from nfa import concat
from nfa import opt
from nfa import rep
from nfa import union
from nfa import State
from nfa import EPSILON


def test_concat():
    fsm = concat(
        char('a'),
        char('b')
    )

    assert fsm.test("ab")

    assert not fsm.test("a")
    assert not fsm.test("aa")
    assert not fsm.test("aab")
    assert not fsm.test("aabb")
    assert not fsm.test("ba")
    assert not fsm.test("")


def test_union():
    fsm = union(
        char("a"),
        char("b")
    )

    assert fsm.test("a")
    assert fsm.test("b")

    assert not fsm.test("")
    assert not fsm.test("ab")
    assert not fsm.test("ba")


def test_rep():
    fsm = rep(char("a"))

    assert fsm.test("")
    assert fsm.test("a")
    assert fsm.test("aa")
    assert fsm.test("aaa")

    assert not fsm.test("ab")


def test_opt():
    fsm = opt(char("a"))

    assert fsm.test("")
    assert fsm.test("a")

    assert not fsm.test("aa")


def test_complex():
    fsm = concat(
        rep(
            union(
                concat(
                    char("a"),
                    char("b"),
                ),
                concat(
                    char("b"),
                    char("a"),
                )
            )
        ),
        rep(
            union(
                char("a"),
                char("b")
            )
        )
    )

    assert fsm.test("aba")
    assert fsm.test("baa")
    assert fsm.test("")
    assert fsm.test("bbb")
    assert fsm.test("aaa")
    assert fsm.test("abaa")


def test_epsilon_closure():
    start = State()
    end = State(accepting=True)
    start.add_transition_for_symbol(EPSILON, end)

    eps_closures = start.get_epsilon_closure()

    assert _assert_equal(eps_closures, [start, end])


def test_neighbors():
    fsm = union(
        char("a"),
        char("b")
    )

    neighbors = fsm.in_state.get_neighbors()
    transitions = fsm.in_state.get_transition_for_symbol(EPSILON)

    assert _assert_equal(neighbors, transitions)


def test_build_graph():
    fsm = union(
        char("a"),
        char("b")
    )

    graph = fsm.build_graph()
    assert graph == {
        1: {EPSILON: [2, 5]},
        2: {"a": [3]},
        3: {EPSILON: [4]},
        4: {},
        5: {"b": [6]},
        6: {EPSILON: [4]},
    }


def test_get_full_transition_table():
    fsm = union(
        char("a"),
        char("b")
    )

    table = fsm.get_full_transition_table()
    assert table == {
        1: {'ε': [1, 2, 5]},
        2: {'a': [3], 'ε': [2]},
        3: {'ε': [3, 4]},
        4: {'ε': [4]},
        5: {'b': [6], 'ε': [5]},
        6: {'ε': [4, 6]}
    }


###########
# HELPERS #
###########

def _assert_equal(l1: list, l2: list) -> bool:
    return all(x in l2 for x in l1)
