import pytest

from dfa import relabel_dfa_states

from nfa import concat
from nfa import rep
from nfa import plus
from nfa import opt
from nfa import union
from nfa import char
from nfa import nfa_to_dfa

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
        dfa = DFA(nfa)

        assert dfa.table == {0: {'a': 1}, 1: {'b': 2}, 2: {}}
        assert dfa.accepts == {2}

    def test_init_rep(self):
        nfa = rep(char("a"))
        dfa = DFA(nfa)

        assert dfa.table == {0: {'a': 1}, 1: {'a': 1}}
        assert dfa.accepts == {0, 1}

    def test_init_plus(self):
        nfa = plus(char("a"))
        dfa = DFA(nfa)

        assert dfa.table == {0: {'a': 1}, 1: {'a': 1}}
        assert dfa.accepts == {1}

    def test_init_opt(self):
        nfa = opt(char("a"))
        dfa = DFA(nfa)

        assert dfa.table == {0: {'a': 1}, 1: {}}
        assert dfa.accepts == {0, 1}

    @pytest.mark.skip
    def test_init_union(self):
        nfa = union(
            char("a"),
            char("b"),
        )
        dfa = DFA(nfa)

        assert dfa.table == {
            0: {'a': 2, 'b': 1},
            1: {},
            2: {}
        }
        assert dfa.accepts == {1, 2}


class TestAccept:
    def test_concat_dfa(self):
        nfa = concat(char("a"), char("b"))
        dfa = DFA(nfa)

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
        dfa = DFA(nfa)

        assert not dfa.test("ab")
        assert not dfa.test("b")
        assert not dfa.test("baaa")

        assert dfa.test("")
        assert dfa.test("a")
        assert dfa.test("aa")
        assert dfa.test("aaa")

    def test_plus_dfa(self):
        nfa = plus(char("a"))
        dfa = DFA(nfa)

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
        dfa = DFA(nfa)

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
        dfa = DFA(nfa)

        assert not dfa.test("")
        assert not dfa.test("ab")
        assert not dfa.test("ba")
        assert not dfa.test("aba")
        assert not dfa.test("bab")

        assert dfa.test("a")
        assert dfa.test("b")

    def test_char(self):
        nfa = char("a")
        dfa = DFA(nfa)

        assert not dfa.test("")
        assert not dfa.test("b")
        assert not dfa.test("1")
        assert not dfa.test("aa")
        assert not dfa.test("ba")

        assert dfa.test("a")


class TestDFAMinimization:
    def test_simple(self):
        initial_table = {
            0: {'a': 1, 'b': 3},
            1: {'a': 2, 'b': 4},
            2: {'a': 1, 'b': 5},
            3: {'a': 4, 'b': 0},
            4: {'a': 5, 'b': 1},
            5: {'a': 4, 'b': 2}
        }
        initial_accepts = {1, 4}

        dfa = DFA(None)
        dfa.table = initial_table
        dfa.accepts = initial_accepts

        expected_table = {
            0: {'a': 1, 'b': 2},
            1: {'a': 1, 'b': 1},
            2: {'a': 1, 'b': 0},
        }
        expected_accepts = {1}
        dfa.minimize()

        assert dfa.min_table == {
            0: {'a': 1, 'b': 2},
            1: {'a': 2, 'b': 1},
            2: {'a': 1, 'b': 2}
        }
        assert dfa.min_accepts == {1}
