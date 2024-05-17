RawDFATable = dict[tuple[int, ...], dict[str, tuple[int, ...]]]
RawAcceptingStates = set[tuple[int, ...]]


class DFA:

    def __init__(self, raw_dfa_table: RawDFATable):
        self._table = relabel_dfa_states(raw_dfa_table)

    def test(self, string: str) -> bool:
        pass
        # logic


def relabel_dfa_states(
    dfa_table: RawDFATable,
    accepts: RawAcceptingStates
) -> tuple[dict[int, dict[str, int]], set[int]]:
    original_to_new = {}
    new_dfa_table = {}
    new_accepts = set()
    state_counter = 0

    def get_state_number(state):
        nonlocal state_counter
        if state not in original_to_new:
            original_to_new[state] = state_counter
            state_counter += 1
        return original_to_new[state]

    for original_state, transitions in dfa_table.items():
        new_state = get_state_number(original_state)
        new_transitions = {}

        for symbol, next_state in transitions.items():
            new_transitions[symbol] = get_state_number(next_state)

        new_dfa_table[new_state] = new_transitions

    for accept_state in accepts:
        new_accepts.add(get_state_number(accept_state))

    return new_dfa_table, new_accepts
