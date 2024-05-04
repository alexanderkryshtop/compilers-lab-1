from converter import RegexToNFAConverter


def main():
    regex = input("Input regex: ")

    converter = RegexToNFAConverter(regex)
    nfa = converter.parse()

    nfa.draw_graph()


if __name__ == '__main__':
    main()
