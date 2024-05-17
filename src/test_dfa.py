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

