from shunting_yard import format_regex
from shunting_yard import infix_to_postfix


class TestFormatRegex:
    def test_1(self):
        assert format_regex("a") == "a"

    def test2(self):
        assert format_regex("ab") == "a.b"  # . is concatenation

    def test3(self):
        assert format_regex("a+b") == "a+.b"

    def test4(self):
        assert format_regex("a|b") == "a|b"

    def test5(self):
        assert format_regex("a(bc)") == "a.(b.c)"

    def test6(self):
        assert format_regex("((ab)|(ba))*(a|b)*") == "((a.b)|(b.a))*.(a|b)*"

    def test7(self):
        assert format_regex("a(c|d)") == "a.(c|d)"


class TestInfixToPostfix:
    def test_1(self):
        assert infix_to_postfix("ab") == "ab."

    def test_2(self):
        assert infix_to_postfix("a|b") == "ab|"

    def test_3(self):
        assert infix_to_postfix("a*b") == "a*b."

    def test_4(self):
        assert infix_to_postfix("ab*") == "ab*."

    def test_5(self):
        assert infix_to_postfix("a(c|d)") == "acd|."

    def test_6(self):
        assert infix_to_postfix("((ab)|(ba))*(a|b)*") == "ab.ba.|*ab|*."

    def test_7(self):
        assert infix_to_postfix("(a|b)*abb") == "ab|*a.b.b."

    def test_8(self):
        assert infix_to_postfix("a+b+c") == "a+b+.c."

    def test_9(self):
        assert infix_to_postfix("a*b*c*") == "a*b*.c*."
