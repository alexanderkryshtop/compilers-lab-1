from collections import defaultdict, deque
from typing import Optional

from graphviz import Digraph
from typing_extensions import Self

EPSILON = "ε"


class State:

    def __init__(self, accepting: bool = False):
        self.id: Optional[int] = None
        self.accepting = accepting
        self.transition_map: dict[str, list[Self]] = defaultdict(list)

    def mark(self, num: int):
        self.id = num

    def add_transition_for_symbol(self, symbol: str, state: Self):
        self.transition_map[symbol].append(state)

    def get_transition_for_symbol(self, symbol: str) -> list[Self]:
        return self.transition_map[symbol]

    def test(self, string: str, visited: set = None) -> bool:
        if visited is None:
            visited = set()

        if self in visited:
            return False
        visited.add(self)

        if len(string) == 0:
            if self.accepting:
                return True
            for next_state in self.get_transition_for_symbol(EPSILON):
                if next_state.test("", visited):
                    return True
            return False

        symbol = string[0]
        rest = string[1:]

        symbol_transitions = self.get_transition_for_symbol(symbol)
        for next_state in symbol_transitions:
            if next_state.test(rest):
                return True

        for next_state in self.get_transition_for_symbol(EPSILON):
            if next_state.test(string, visited):
                return True
        return False

    def get_epsilon_closure(self) -> list[Self]:
        eps_closures = self.get_transition_for_symbol(EPSILON)
        eps_closures.append(self)
        return eps_closures

    def get_neighbors(self) -> list[Self]:
        all_neighbors = []
        for k in self.transition_map:
            all_neighbors.extend(self.get_transition_for_symbol(k))
        return all_neighbors

    def __repr__(self) -> str:
        if self.id is None:
            return f"State(accepting={self.accepting}, transitions={list(self.transition_map.keys())})"
        transitions = []
        for key, value in self.transition_map.items():
            destination_ids = []
            for v in value:
                destination_ids.append(v.id)
            transitions.append(f"{key} -> {destination_ids}")
        return f"State(id={self.id}, transitions={transitions}, accepting={self.accepting})"


class NFA:
    def __init__(self, in_state: State, out_state: State):
        self.in_state = in_state
        self.out_state = out_state

        self._node_mapping: dict[int, State] = {}

    def test(self, string: str):
        return self.in_state.test(string)

    def __repr__(self):
        return f"[in = {self.in_state}] [out = {self.out_state}]"

    def get_full_transition_table(self) -> dict[int, dict[str, list[int]]]:
        graph = self.build_graph()

        for node_id in self._node_mapping:
            node = self._node_mapping[node_id]
            closure = node.get_epsilon_closure()
            closure_ids = []
            for c in closure:
                closure_ids.append(c.id)
            graph[node_id][EPSILON] = sorted(closure_ids)

        return graph

    def build_graph(self) -> dict[int, dict[str, list[int]]]:
        root = self.in_state
        visited: set[State] = set()
        num = 1

        def dfs(vertex: State):
            nonlocal num
            if vertex not in visited:
                # visit node
                visited.add(vertex)
                vertex.mark(num)

                num += 1
                for neighbor in vertex.get_neighbors():
                    dfs(neighbor)

        dfs(root)

        graph = {}
        for node in visited:
            graph[node.id] = {}
            for symbol, vertices in node.transition_map.items():
                vertices_ids = []
                for v in vertices:
                    vertices_ids.append(v.id)
                graph[node.id][symbol] = vertices_ids
            self._node_mapping[node.id] = node

        return graph

    def draw_graph(self):
        dot = Digraph()
        dot.attr(rankdir='LR')

        graph = self.build_graph()

        for state in graph:
            if not graph[state] or self.out_state.id == state:
                dot.node(str(state), str(state), shape='doublecircle')
            else:
                dot.node(str(state), str(state), shape='circle')

        dot.node('start', '', shape='none')  # invisible node
        dot.edge('start', '1', '')

        for state, paths in graph.items():
            for symbol, next_states in paths.items():
                for next_state in next_states:
                    label = str(symbol)
                    dot.edge(str(state), str(next_state), label=label)

        dot.render("nfa_output", format="png", view=True)


def char(symbol: str) -> NFA:
    in_state = State()
    out_state = State(accepting=True)

    in_state.add_transition_for_symbol(symbol, out_state)
    return NFA(in_state, out_state)


def epsilon() -> NFA:
    return char(EPSILON)


def concat_pair(first: NFA, second: NFA) -> NFA:
    first.out_state.accepting = False
    second.out_state.accepting = True

    first.out_state.add_transition_for_symbol(
        EPSILON,
        second.in_state,
    )

    return NFA(first.in_state, second.out_state)


def concat(first, *fragments) -> NFA:
    for fragment in fragments:
        first = concat_pair(first, fragment)
    return first


def union_pair(first: NFA, second: NFA) -> NFA:
    in_state = State()
    out_state = State(accepting=True)

    first.out_state.accepting = False
    second.out_state.accepting = False

    in_state.add_transition_for_symbol(EPSILON, first.in_state)
    in_state.add_transition_for_symbol(EPSILON, second.in_state)

    first.out_state.add_transition_for_symbol(EPSILON, out_state)
    second.out_state.add_transition_for_symbol(EPSILON, out_state)

    return NFA(in_state, out_state)


def union(first, *fragments) -> NFA:
    first = first
    for fragment in fragments:
        first = union_pair(first, fragment)
    return first


def rep(fragment: NFA) -> NFA:
    in_state = State()
    out_state = State(accepting=True)

    fragment.out_state.accepting = False

    in_state.add_transition_for_symbol(EPSILON, out_state)
    in_state.add_transition_for_symbol(EPSILON, fragment.in_state)
    out_state.add_transition_for_symbol(EPSILON, fragment.in_state)

    fragment.out_state.add_transition_for_symbol(EPSILON, out_state)
    return NFA(in_state, out_state)


def plus(fragment: NFA) -> NFA:
    return concat(fragment, rep(fragment))


def opt(fragment: NFA) -> NFA:
    return union(fragment, char(EPSILON))


# Множество состояний, достижимых из состояния q только по ε-переходам
def epsilon_closure_of_state(state_id: int, transition_table: dict[int, dict[str, list[int]]]) -> set[int]:
    stack = [state_id]
    closure = set(stack)

    while stack:
        state = stack.pop()
        if EPSILON in transition_table[state]:
            for next_state in transition_table[state][EPSILON]:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
    return closure


def epsilon_closure_of_set(state_ids: set[int], transition_table: dict[int, dict[str, list[int]]]) -> set[int]:
    closure = set()
    for state_id in state_ids:
        closure.update(epsilon_closure_of_state(state_id, transition_table))
    return closure


def move(state_ids: set[int], symbol: str, transition_table: dict[int, dict[str, list[int]]]) -> set[int]:
    next_states = set()
    for state_id in state_ids:
        if symbol in transition_table[state_id]:
            next_states.update(transition_table[state_id][symbol])
    return next_states


def nfa_to_dfa(nfa: NFA) -> dict[tuple[int, ...], dict[str, tuple[int, ...]]]:
    transition_table = nfa.get_full_transition_table()

    initial_closure = epsilon_closure_of_set({nfa.in_state.id}, transition_table)
    dfa_transition_table = {}
    dfa_states = {tuple(sorted(initial_closure)): 0}
    queue = deque([initial_closure])

    alphabet = {symbol for state_transitions in transition_table.values() for symbol in state_transitions if
                symbol != EPSILON}
    state_id_counter = 1

    while queue:
        current = queue.popleft()
        current_tuple = tuple(sorted(current))
        if current_tuple not in dfa_transition_table:
            dfa_transition_table[current_tuple] = {}

        for symbol in alphabet:
            next_states = move(current, symbol, transition_table)
            next_closure = epsilon_closure_of_set(next_states, transition_table)
            next_tuple = tuple(sorted(next_closure))

            if next_tuple not in dfa_states:
                dfa_states[next_tuple] = state_id_counter
                state_id_counter += 1
                queue.append(next_closure)

            dfa_transition_table[current_tuple][symbol] = next_tuple

    return dfa_transition_table
