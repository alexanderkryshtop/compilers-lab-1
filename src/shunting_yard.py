precedence_map = {
    "(": 1,
    "|": 2,
    ".": 3,
    "?": 4,
    "*": 4,
    "+": 4
}


def format_regex(regex: str) -> str:
    res = ""
    all_operators = ["|", "?", "+", "*"]
    binary_operators = ["|"]

    for i in range(len(regex)):
        c1 = regex[i]
        if i + 1 < len(regex):
            c2 = regex[i + 1]
            res += c1
            if (c1 != "(" and c2 != ")") and (c2 not in all_operators) and (c1 not in binary_operators):
                res += "."
    res += regex[-1]
    return res


def infix_to_postfix(regex: str) -> str:
    postfix = ""
    stack = []

    formatted_regex = format_regex(regex)

    for c in formatted_regex:
        if c == "(":
            stack.append(c)
        elif c == ")":
            while stack[-1] != "(":
                postfix += stack.pop()
            stack.pop()
        else:
            while len(stack) > 0:
                peeked_char = stack[-1]

                peeked_char_precedence = precedence_map.get(peeked_char, 5)
                current_char_precedence = precedence_map.get(c, 5)

                if peeked_char_precedence >= current_char_precedence:
                    postfix += stack.pop()
                else:
                    break
            stack.append(c)

    while len(stack) > 0:
        postfix += stack.pop()

    return postfix
