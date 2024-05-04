from nfa import char
from nfa import rep
from nfa import plus
from nfa import opt
from nfa import union
from nfa import concat

from shunting_yard import infix_to_postfix

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


class RegexToNFAConverter:
    def __init__(self, regex: str):
        self.regex = infix_to_postfix(regex)

    def parse(self):
        stack = []

        for ch in self.regex:
            if ch == ".":  # concatenation
                e2 = stack.pop()
                e1 = stack.pop()
                result = concat(e1, e2)
                stack.append(result)
            elif ch == "|":  # union
                e2 = stack.pop()
                e1 = stack.pop()
                result = union(e1, e2)
                stack.append(result)
            elif ch == "?":  # zero or none - optional
                e = stack.pop()
                result = opt(e)
                stack.append(result)
            elif ch == "*":
                e = stack.pop()
                result = rep(e)
                stack.append(result)
            elif ch == "+":
                e = stack.pop()
                result = plus(e)
                stack.append(result)
            elif ch in ALPHABET:
                e = char(ch)
                stack.append(e)

        return stack.pop() if stack else None
