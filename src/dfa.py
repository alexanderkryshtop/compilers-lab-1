from collections import defaultdict, deque
from typing import Optional

from graphviz import Digraph
from typing_extensions import Self

from nfa import NFA
from nfa import nfa_to_dfa
from src.converter import ALPHABET

RawDFATable = dict[tuple[int, ...], dict[str, tuple[int, ...]]]
RawAcceptingStates = set[tuple[int, ...]]


class DFA:

    def __init__(
        self,
        table: Optional[dict[int, dict[str, int]]] = None,
        accepts: Optional[set[int]] = None,
        initial_state: int = 0,
    ):
        self.table = table
        self.accepts = accepts
        self.initial_state = initial_state

    @property
    def terms(self) -> list[str]:
        terms = []
        if self.table:
            for _, v in self.table.items():
                for k in v:
                    terms.append(k)
        return terms

    @classmethod
    def from_nfa(cls, nfa: NFA) -> Self:
        dfa = DFA()
        raw_dfa_table, raw_dfa_accepts = nfa_to_dfa(nfa)

        dfa.table, dfa.accepts = relabel_dfa_states(raw_dfa_table, raw_dfa_accepts)
        dfa.initial_state = 0
        return dfa

    def test(self, string: str) -> bool:
        current_state = 0
        for symbol in string:
            if symbol in self.table[current_state]:
                current_state = self.table[current_state][symbol]
            else:
                return False
        return current_state in self.accepts

    def draw_graph(self, minimized: bool = False):
        dot = Digraph()
        dot.attr(rankdir='LR')

        for state in self.table:
            if state in self.accepts:
                dot.node(str(state), str(state), shape='doublecircle')
            else:
                dot.node(str(state), str(state), shape='circle')

        dot.node('start', '', shape='none')  # invisible node
        dot.edge('start', '0', '')

        for state, paths in self.table.items():
            for symbol, next_state in paths.items():
                label = str(symbol)
                dot.edge(str(state), str(next_state), label=label)

        if minimized:
            dot.render("min_dfa_output", format="png", view=True)
        else:
            dot.render("dfa_output", format="png", view=True)

    def _build_reverse_transitions(self):
        reverse_transitions = defaultdict(lambda: defaultdict(set))
        for state, transitions in self.table.items():
            for symbol, next_state in transitions.items():
                reverse_transitions[next_state][symbol].add(state)
        max_state = max(self.table.keys())
        aux_state_id = max_state + 1
        for state, transitions in self.table.items():
            for key in self.terms:
                if key not in transitions:
                    reverse_transitions[aux_state_id][key].add(state)
        for key in self.terms:
            reverse_transitions[aux_state_id][key].add(aux_state_id)
        return reverse_transitions

    def _is_terminal(self, state):
        return state in self.accepts

    def _reachable(self):
        reachable = [False] * (len(self.table) + 1)
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
            for j in range(n):
                if not marked[i][j] and is_terminal[i] != is_terminal[j]:
                    marked[i][j] = marked[j][i] = True
                    queue.append((i, j))

        while queue:
            u, v = queue.popleft()
            for symbol in self.terms:
                for r in reverse_transitions[u][symbol]:
                    for s in reverse_transitions[v][symbol]:
                        if not marked[r][s]:
                            marked[r][s] = marked[s][r] = True
                            queue.append((r, s))

        return marked

    def build_min_dfa(self) -> Self:
        n = len(self.table) + 1
        states = list(self.table.keys()) + [max(self.table.keys()) + 1]
        is_terminal = [self._is_terminal(state) for state in states]
        reverse_transitions = self._build_reverse_transitions()
        reachable = self._reachable()

        marked = self._build_table(n, is_terminal, reverse_transitions)

        component = [-1] * n
        for i in range(n):
            if not marked[0][i]:
                component[i] = 0

        components_count = 0

        for i in range(1, n):
            if not reachable[i]:
                continue
            if component[i] == -1:
                components_count += 1
                component[i] = components_count
                for j in range(i+1, n):
                    if not marked[i][j]:
                        component[j] = components_count

        return self._build_minimization(component)

    def _build_minimization(self, component) -> Self:
        new_state_dict = {}
        for from_state, value_dict in self.table.items():
            new_from_state = component[from_state]
            for sign, to_state in value_dict.items():
                new_to_state = component[to_state]
                new_state_dict.setdefault(new_from_state, {})[sign] = new_to_state

        min_table = new_state_dict
        min_initial_state = component[self.initial_state]
        min_accepts = {component[state] for state in self.accepts}

        for accept in min_accepts:
            if accept not in min_table:
                min_table[accept] = {}

        minimized_dfa = DFA(table=min_table, accepts=min_accepts, initial_state=min_initial_state)
        return minimized_dfa


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
