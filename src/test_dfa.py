from dfa import relabel_dfa_states


class TestRelabelDfaStates:
    def test_simple_dfa(self):
        dfa_table = {
            (1,): {'a': (2,)},
            (2,): {'b': (3,)},
            (3,): {}
        }
        expected_relabel = {
            0: {'a': 1},
            1: {'b': 2},
            2: {}
        }
        assert relabel_dfa_states(dfa_table) == expected_relabel

    def test_complex_dfa(self):
        dfa_table = {
            (1,): {'a': (2, 3)},
            (2, 3): {'b': (4,)},
            (4,): {'c': (5,)},
            (5,): {}
        }
        expected_relabel = {
            0: {'a': 1},
            1: {'b': 2},
            2: {'c': 3},
            3: {}
        }
        assert relabel_dfa_states(dfa_table) == expected_relabel

    def test_empty_dfa(self):
        dfa_table = {}
        expected_relabel = {}
        assert relabel_dfa_states(dfa_table) == expected_relabel
