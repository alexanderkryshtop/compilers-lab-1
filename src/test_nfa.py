import pytest

from nfa import char
from nfa import concat
from nfa import opt
from nfa import rep
from nfa import union
from nfa import plus
from nfa import State
from nfa import EPSILON
from nfa import epsilon_closure_of_state
from nfa import epsilon_closure_of_set
from nfa import move
from nfa import NFA
from nfa import nfa_to_dfa


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


class TestEpsilonClosureOfState:
    def test_no_epsilon_transitions(self):
        transition_table = {
            1: {'a': [2]},
            2: {'b': [3]}
        }
        assert epsilon_closure_of_state(1, transition_table) == {1}

    def test_single_epsilon_transition(self):
        transition_table = {
            1: {EPSILON: [2]},
            2: {'b': [3]},
            3: {}
        }
        assert epsilon_closure_of_state(1, transition_table) == {1, 2}

    def test_multiple_epsilon_transitions(self):
        transition_table = {
            1: {EPSILON: [2, 3]},
            2: {EPSILON: [4]},
            3: {'b': [5]},
            4: {},
            5: {}
        }
        assert epsilon_closure_of_state(1, transition_table) == {1, 2, 3, 4}

    def test_cyclic_epsilon_transitions(self):
        transition_table = {
            1: {EPSILON: [2]},
            2: {EPSILON: [3]},
            3: {EPSILON: [1, 4]},
            4: {}
        }
        assert epsilon_closure_of_state(1, transition_table) == {1, 2, 3, 4}

    def test_complex_epsilon_transitions(self):
        transition_table = {
            1: {EPSILON: [2, 3]},
            2: {'a': [4]},
            3: {EPSILON: [5]},
            4: {EPSILON: [5, 6]},
            5: {EPSILON: [7]},
            6: {},
            7: {EPSILON: [8]},
            8: {}
        }
        assert epsilon_closure_of_state(1, transition_table) == {1, 2, 3, 5, 7, 8}


class TestEpsilonClosureOfSet:
    def test_no_epsilon_transitions_for_set(self):
        transition_table = {
            1: {'a': [2]},
            2: {'b': [3]},
            3: {}
        }
        assert epsilon_closure_of_set({1, 2}, transition_table) == {1, 2}

    def test_single_epsilon_transition_for_set(self):
        transition_table = {
            1: {EPSILON: [2]},
            2: {'b': [3]},
            3: {}
        }
        assert epsilon_closure_of_set({1}, transition_table) == {1, 2}

    def test_multiple_epsilon_transitions_for_set(self):
        transition_table = {
            1: {EPSILON: [2, 3]},
            2: {EPSILON: [4]},
            3: {'b': [5]},
            4: {},
            5: {}
        }
        assert epsilon_closure_of_set({1}, transition_table) == {1, 2, 3, 4}

    def test_cyclic_epsilon_transitions_for_set(self):
        transition_table = {
            1: {EPSILON: [2]},
            2: {EPSILON: [3]},
            3: {EPSILON: [1, 4]},
            4: {}
        }
        assert epsilon_closure_of_set({1}, transition_table) == {1, 2, 3, 4}

    def test_complex_epsilon_transitions_for_set(self):
        transition_table = {
            1: {EPSILON: [2, 3]},
            2: {'a': [4]},
            3: {EPSILON: [5]},
            4: {EPSILON: [5, 6]},
            5: {EPSILON: [7]},
            6: {},
            7: {EPSILON: [8]},
            8: {}
        }
        assert epsilon_closure_of_set({1}, transition_table) == {1, 2, 3, 5, 7, 8}

    def test_no_epsilon_transitions_mixed_states(self):
        transition_table = {
            1: {'a': [2]},
            2: {EPSILON: [3]},
            3: {}
        }
        assert epsilon_closure_of_set({1, 2}, transition_table) == {1, 2, 3}

    def test_epsilon_transitions_with_self_loop(self):
        transition_table = {
            1: {EPSILON: [1, 2]},
            2: {EPSILON: [3]},
            3: {}
        }
        assert epsilon_closure_of_set({1}, transition_table) == {1, 2, 3}


class TestMove:

    def test_move_no_transitions(self):
        transition_table = {
            1: {},
            2: {'b': [3]},
            3: {}
        }
        assert move({1}, 'a', transition_table) == set()

    def test_move_single_transition(self):
        transition_table = {
            1: {'a': [2]},
            2: {'b': [3]},
            3: {}
        }
        assert move({1}, 'a', transition_table) == {2}

    def test_move_multiple_transitions(self):
        transition_table = {
            1: {'a': [2, 3]},
            2: {'b': [4]},
            3: {'a': [5]},
            4: {},
            5: {}
        }
        assert move({1, 3}, 'a', transition_table) == {2, 3, 5}

    def test_move_cyclic_transitions(self):
        transition_table = {
            1: {'a': [2]},
            2: {'b': [3]},
            3: {'a': [1]}
        }
        assert move({1, 3}, 'a', transition_table) == {1, 2}

    def test_move_no_valid_transitions(self):
        transition_table = {
            1: {'a': [2]},
            2: {'b': [3]},
            3: {}
        }
        assert move({1, 2}, 'c', transition_table) == set()

    def test_move_complex_transitions(self):
        transition_table = {
            1: {'a': [2], 'b': [3]},
            2: {'a': [4], 'b': [5]},
            3: {'a': [6], 'b': [7]},
            4: {},
            5: {},
            6: {},
            7: {}
        }
        assert move({1, 2, 3}, 'b', transition_table) == {3, 5, 7}


class TestNfaToDfaTable:
    def test_nfa_to_dfa(self):
        nfa = concat(
            char("a"),
            char("b"),
        )
        dfa_table, accepting_states = nfa_to_dfa(nfa)

        expected_dfa = {
            (1,): {'a': (2, 3)},
            (2, 3): {'b': (4,)},
            (4,): {}
        }

        assert dfa_table == expected_dfa
        assert accepting_states == {(4,)}

    def test_nfa_to_dfa_simple(self):
        nfa = char("a")
        dfa_table, accepting_states = nfa_to_dfa(nfa)

        expected_dfa = {
            (1,): {'a': (2,)},
            (2,): {}
        }

        assert dfa_table == expected_dfa
        assert accepting_states == {(2,)}

    def test_nfa_to_dfa_plus(self):
        nfa = plus(char("a"))
        dfa_table, accepting_states = nfa_to_dfa(nfa)

        assert dfa_table == {
            (1,): {'a': (1, 2, 3, 4)},
            (1, 2, 3, 4): {'a': (1, 2, 3, 4)}
        }
        assert accepting_states == {(1, 2, 3, 4)}

    def test_nfa_to_dfa_union(self):
        nfa = union(char("a"), char("b"))
        dfa_table, accepting_states = nfa_to_dfa(nfa)

        assert dfa_table == {
            (1, 2, 5): {'a': (3, 4), 'b': (4, 6)},
            (3, 4): {},
            (4, 6): {}
        }
        assert accepting_states == {(3, 4), (4, 6)}

    def test_nfa_to_dfa_rep(self):
        nfa = rep(char("a"))
        dfa_table, accepting_states = nfa_to_dfa(nfa)

        assert dfa_table == {
            (1, 2, 3): {'a': (2, 3, 4)},
            (2, 3, 4): {'a': (2, 3, 4)}
        }
        assert accepting_states == {(1, 2, 3), (2, 3, 4)}


###########
# HELPERS #
###########


def _assert_equal(l1: list, l2: list) -> bool:
    return all(x in l2 for x in l1)
