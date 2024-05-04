from collections import defaultdict

from graphviz import Digraph
from typing_extensions import Self

EPSILON = "ε"


class State:

    def __init__(self, accepting: bool = False):
        self.id = None
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

    def test(self, string: str):
        return self.in_state.test(string)

    def __repr__(self):
        return f"[in = {self.in_state}] [out = {self.out_state}]"

    def get_transition_table(self) -> dict[str, set[str]]:
        pass

    def build_graph(self):
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
