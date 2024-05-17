from collections import defaultdict, deque

from nfa import NFA
from nfa import nfa_to_dfa

RawDFATable = dict[tuple[int, ...], dict[str, tuple[int, ...]]]
RawAcceptingStates = set[tuple[int, ...]]


class DFA:

    def __init__(self, nfa: NFA):
        if nfa:
            raw_dfa_table, raw_dfa_accepts = nfa_to_dfa(nfa)
            self.table, self.accepts = relabel_dfa_states(raw_dfa_table, raw_dfa_accepts)
        self.initial_state = 0

        self.min_table = None
        self.min_accepts = None

    def test(self, string: str) -> bool:
        current_state = 0
        for symbol in string:
            if symbol in self.table[current_state]:
                current_state = self.table[current_state][symbol]
            else:
                return False
        return current_state in self.accepts

    def _build_reverse_transitions(self):
        reverse_transitions = defaultdict(lambda: defaultdict(set))
        for state, transitions in self.table.items():
            for symbol, next_state in transitions.items():
                reverse_transitions[next_state][symbol].add(state)
        return reverse_transitions

    def _is_terminal(self, state):
        return state in self.accepts

    def _reachable(self):
        reachable = [False] * len(self.table)
        queue = deque([self.initial_state])
        reachable[self.initial_state] = True
        while queue:
            state = queue.popleft()
            for next_state in self.table[state].values():
                if not reachable[next_state]:
                    reachable[next_state] = True
                    queue.append(next_state)
        return reachable

    def _build_table(self, n, is_terminal, reverse_transitions):
        marked = [[False] * n for _ in range(n)]
        queue = deque()

        for i in range(n):
            for j in range(i + 1, n):
                if is_terminal[i] != is_terminal[j]:
                    marked[i][j] = marked[j][i] = True
                    queue.append((i, j))

        while queue:
            u, v = queue.popleft()
            for symbol in reverse_transitions[u]:
                for r in reverse_transitions[u][symbol]:
                    for s in reverse_transitions[v][symbol]:
                        if not marked[r][s]:
                            marked[r][s] = marked[s][r] = True
                            queue.append((r, s))

        return marked

    def minimize(self):
        n = len(self.table)
        states = list(self.table.keys())
        is_terminal = [self._is_terminal(state) for state in states]
        reverse_transitions = self._build_reverse_transitions()
        reachable = self._reachable()

        marked = self._build_table(n, is_terminal, reverse_transitions)

        component = [-1] * n
        component[0] = 0
        components_count = 0

        for i in range(1, n):
            if not reachable[i]:
                continue
            if component[i] == -1:
                components_count += 1
                component[i] = components_count
                for j in range(i + 1, n):
                    if not marked[i][j]:
                        component[j] = components_count

        minimized_table = {}
        minimized_accepts = set()

        for state, transitions in self.table.items():
            i = states.index(state)
            representative = component[i]
            if representative not in minimized_table:
                minimized_table[representative] = {}
            if state in self.accepts:
                minimized_accepts.add(representative)
            for symbol, next_state in transitions.items():
                ni = states.index(next_state)
                minimized_table[representative][symbol] = component[ni]

        self.min_table = minimized_table
        self.min_accepts = minimized_accepts


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
