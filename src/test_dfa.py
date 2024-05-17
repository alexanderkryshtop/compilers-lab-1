from dfa import relabel_dfa_states


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

