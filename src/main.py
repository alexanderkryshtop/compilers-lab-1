from converter import RegexToNFAConverter
from dfa import DFA


def main():
    regex = input("Input regex: ")

    converter = RegexToNFAConverter(regex)

    nfa = converter.parse()
    nfa.draw_graph()

    dfa = DFA.from_nfa(nfa)
    dfa.draw_graph()

    min_dfa = dfa.build_min_dfa()
    min_dfa.draw_graph(minimized=True)

    while True:
        string = input("Input string: ")
        if string is None or string == "/exit":
            break
        result = min_dfa.test(string)
        if result:
            print("OK")
        else:
            print("INVALID STRING")


if __name__ == '__main__':
    main()
