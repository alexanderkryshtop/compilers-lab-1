import pytest

from dfa import relabel_dfa_states

from nfa import concat
from nfa import rep
from nfa import plus
from nfa import opt
from nfa import union
from nfa import char

from dfa import DFA


class TestRelabelDfaStates:
    def test_simple_dfa(self):
        dfa_table = {
            (1,): {'a': (2,)},
            (2,): {'b': (3,)},
            (3,): {}
        }
        dfa_accepts = {(3,)}

        expected_relabel = {
            0: {'a': 1},
            1: {'b': 2},
            2: {}
        }
        expected_accepts = {2}

        relabel, accepts = relabel_dfa_states(dfa_table, dfa_accepts)
        assert relabel == expected_relabel
        assert accepts == expected_accepts

    def test_complex_dfa(self):
        dfa_table = {
            (1,): {'a': (2, 3)},
            (2, 3): {'b': (4,)},
            (4,): {'c': (5,)},
            (5,): {}
        }
        dfa_accepts = {(5,)}

        expected_relabel = {
            0: {'a': 1},
            1: {'b': 2},
            2: {'c': 3},
            3: {}
        }
        expected_accepts = {3}

        relabel, accepts = relabel_dfa_states(dfa_table, dfa_accepts)
        assert relabel == expected_relabel
        assert accepts == expected_accepts

    def test_empty_dfa(self):
        dfa_table = {}
        dfa_accepts = set()
        relabel, accepts = relabel_dfa_states(dfa_table, dfa_accepts)
        assert relabel == {}
        assert accepts == set()


class TestInitDFA:

    def test_init_concat(self):
        nfa = concat(char("a"), char("b"))
        dfa = DFA.from_nfa(nfa)

        assert dfa.table == {0: {'a': 1}, 1: {'b': 2}, 2: {}}
        assert dfa.accepts == {2}

    def test_init_rep(self):
        nfa = rep(char("a"))
        dfa = DFA.from_nfa(nfa)

        assert dfa.table == {0: {'a': 1}, 1: {'a': 1}}
        assert dfa.accepts == {0, 1}

    def test_init_plus(self):
        nfa = plus(char("a"))
        dfa = DFA.from_nfa(nfa)

        assert dfa.table == {0: {'a': 1}, 1: {'a': 1}}
        assert dfa.accepts == {1}

    def test_init_opt(self):
        nfa = opt(char("a"))
        dfa = DFA.from_nfa(nfa)

        assert dfa.table == {0: {'a': 1}, 1: {}}
        assert dfa.accepts == {0, 1}

    @pytest.mark.skip
    def test_init_union(self):
        nfa = union(
            char("a"),
            char("b"),
        )
        dfa = DFA.from_nfa(nfa)

        assert dfa.table == {
            0: {'a': 2, 'b': 1},
            1: {},
            2: {}
        }
        assert dfa.accepts == {1, 2}


class TestAccept:
    def test_concat_dfa(self):
        nfa = concat(char("a"), char("b"))
        dfa = DFA.from_nfa(nfa)

        assert not dfa.test("a")
        assert not dfa.test("b")
        assert not dfa.test("")
        assert not dfa.test("ba")
        assert not dfa.test("aba")
        assert not dfa.test("bab")
        assert not dfa.test("abc")

        assert dfa.test("ab")

    def test_rep_dfa(self):
        nfa = rep(char("a"))
        dfa = DFA.from_nfa(nfa)

        assert not dfa.test("ab")
        assert not dfa.test("b")
        assert not dfa.test("baaa")

        assert dfa.test("")
        assert dfa.test("a")
        assert dfa.test("aa")
        assert dfa.test("aaa")

    def test_plus_dfa(self):
        nfa = plus(char("a"))
        dfa = DFA.from_nfa(nfa)

        assert not dfa.test("")
        assert not dfa.test("b")
        assert not dfa.test("ab")
        assert not dfa.test("ba")
        assert not dfa.test("aba")

        assert dfa.test("a")
        assert dfa.test("aa")
        assert dfa.test("aaa")

    def test_opt_dfa(self):
        nfa = opt(char("a"))
        dfa = DFA.from_nfa(nfa)

        assert not dfa.test("aa")
        assert not dfa.test("aaa")
        assert not dfa.test("b")
        assert not dfa.test("ab")
        assert not dfa.test("ba")
        assert not dfa.test("aba")

        assert dfa.test("")
        assert dfa.test("a")

    def test_union_dfa(self):
        nfa = union(char("a"), char("b"))
        dfa = DFA.from_nfa(nfa)

        assert not dfa.test("")
        assert not dfa.test("ab")
        assert not dfa.test("ba")
        assert not dfa.test("aba")
        assert not dfa.test("bab")

        assert dfa.test("a")
        assert dfa.test("b")

    def test_char(self):
        nfa = char("a")
        dfa = DFA.from_nfa(nfa)

        assert not dfa.test("")
        assert not dfa.test("b")
        assert not dfa.test("1")
        assert not dfa.test("aa")
        assert not dfa.test("ba")

        assert dfa.test("a")


class TestDFAReverseTransitions:
    def test(self):
        initial_table = {
            0: {'a': 1, 'b': 2},
            1: {'a': 0, 'b': 2},
            2: {'a': 1, 'b': 0}
        }

        dfa = DFA(None)
        dfa.table = initial_table
        dfa.accepts = {1}

        expected_reverse_transitions = {
            0: {'a': {1}, 'b': {2}},
            1: {'a': {0, 2}},
            2: {'b': {0, 1}}
        }

        reverse_transitions = dfa._build_reverse_transitions()
        assert reverse_transitions == expected_reverse_transitions

    def test_rep(self):
        nfa = rep(char("a"))
        dfa = DFA.from_nfa(nfa)

        reverse_transitions = dfa._build_reverse_transitions()
        assert reverse_transitions == {1: {"a": {0, 1}}}


class TestReachable:
    def test_simple(self):
        initial_table = {
            0: {'a': 1, 'b': 2},
            1: {'a': 0, 'b': 2},
            2: {'a': 1, 'b': 0},
            3: {},  # unreachable state
        }
        initial_accepts = {1}

        dfa = DFA(initial_table, initial_accepts, initial_state=0)

        res = dfa._reachable()
        assert res == [True, True, True, False]


class TestDFAMinimization:
    def test_simple(self):
        nfa = rep(char("a"))
        dfa = DFA.from_nfa(nfa)

        assert dfa.table == {0: {'a': 1}, 1: {'a': 1}}
        assert dfa.accepts == {0, 1}

        min_dfa = dfa.build_min_dfa()

        assert min_dfa.table == {0: {'a': 0}}
        assert min_dfa.accepts == {0}
        assert min_dfa.initial_state == 0

    def test_complex_example(self):
        initial_table = {
            0: {"a": 1, "b": 2},
            1: {"a": 3, "b": 3},
            2: {"a": 1, "b": 0},
            3: {"a": 5, "b": 4},
            4: {"a": 4, "b": 4},
            5: {"a": 4, "b": 7},
            6: {"a": 5, "b": 4},
            7: {"a": 7, "b": 4},
        }
        initial_accepts = {4, 7}

        dfa = DFA(initial_table, initial_accepts, initial_state=0)

        min_dfa = dfa.build_min_dfa()

        assert min_dfa.table == {
            0: {'a': 1, 'b': 0},
            1: {'a': 2, 'b': 2},
            2: {'a': 4, 'b': 3},
            3: {'a': 3, 'b': 3},
            4: {'a': 3, 'b': 3}
        }
        assert min_dfa.accepts == {3}
        assert min_dfa.initial_state == 0

    # @pytest.mark.skip
    def test_concat(self):
        nfa = concat(char("a"), char("b"))
        dfa = DFA.from_nfa(nfa)
        min_dfa = dfa.build_min_dfa()

        assert min_dfa.table == {0: {'a': 1}, 1: {'b': 2}, 2: {}}
        assert min_dfa.accepts == {2}
        assert min_dfa.initial_state == 0

        assert not min_dfa.test("a")
        assert not min_dfa.test("b")
        assert not min_dfa.test("")

        assert min_dfa.test("ab")

    def test_plus(self):
        nfa = plus(char("a"))
        dfa = DFA.from_nfa(nfa)
        min_dfa = dfa.build_min_dfa()

        assert min_dfa.table == {0: {'a': 1}, 1: {'a': 1}}
        assert min_dfa.accepts == {1}
        assert min_dfa.initial_state == 0

        assert not min_dfa.test("")
        assert not min_dfa.test("b")

        assert min_dfa.test("a")
        assert min_dfa.test("aa")
        assert min_dfa.test("aaa")

    @pytest.mark.skip
    def test_opt(self):
        nfa = opt(char("a"))
        dfa = DFA.from_nfa(nfa)
        min_dfa = dfa.build_min_dfa()

        assert min_dfa.table == {0: {'a': 0}}
        assert min_dfa.accepts == {0}
        assert min_dfa.initial_state == 0

        assert not min_dfa.test("aa")
        assert not min_dfa.test("ab")
        assert not min_dfa.test("ba")

        assert min_dfa.test("a")
        assert min_dfa.test("")

    def test_union(self):
        nfa = union(char("a"), char("b"))
        dfa = DFA.from_nfa(nfa)
        min_dfa = dfa.build_min_dfa()

        assert min_dfa.table == {0: {'a': 1, 'b': 1}, 1: {}}
        assert min_dfa.accepts == {1}
        assert min_dfa.initial_state == 0

        assert not min_dfa.test("aa")
        assert not min_dfa.test("bb")
        assert not min_dfa.test("")

        assert min_dfa.test("a")
        assert min_dfa.test("b")


###########
# HELPERS #
###########


def _build_dfa(table, accepts):
    dfa = DFA(None)
    dfa.table = table
    dfa.accepts = accepts
    return dfa
