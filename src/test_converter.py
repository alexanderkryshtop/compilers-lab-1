from converter import RegexToNFAConverter

from nfa import concat
from nfa import char
from nfa import union
from nfa import plus
from nfa import rep

from deepdiff import DeepDiff


def test_simple_regex():
    converter = RegexToNFAConverter("ab")
    nfa = converter.parse()

    expected_nfa = concat(
        char("a"),
        char("b")
    )

    diff = DeepDiff(expected_nfa, nfa)
    assert not diff

    assert not nfa.test("a")
    assert not nfa.test("b")
    assert not nfa.test("abc")
    assert not nfa.test("")

    assert nfa.test("ab")


def test_complex_plus():
    converter = RegexToNFAConverter("ab+")
    nfa = converter.parse()

    expected_nfa = concat(
        char("a"),
        plus(
            char("b")
        ),
    )

    diff = DeepDiff(expected_nfa, nfa)
    assert not diff

    assert not nfa.test("a")
    assert not nfa.test("b")
    assert not nfa.test("abc")
    assert not nfa.test("")

    assert nfa.test("ab")
    assert nfa.test("abb")
    assert nfa.test("abbb")
    assert nfa.test("abbbb")


def test_concat():
    converter = RegexToNFAConverter("a|b")
    nfa = converter.parse()

    expected_nfa = union(
        char("a"),
        char("b")
    )

    diff = DeepDiff(expected_nfa, nfa)
    assert not diff

    assert not nfa.test("aa")
    assert not nfa.test("bb")
    assert not nfa.test("abc")
    assert not nfa.test("ab")
    assert not nfa.test("ba")

    assert nfa.test("a")
    assert nfa.test("b")


def test_rep():
    converter = RegexToNFAConverter("a*")
    nfa = converter.parse()

    expected_nfa = rep(
        char("a")
    )

    diff = DeepDiff(expected_nfa, nfa)
    assert not diff

    assert not nfa.test("b")
    assert not nfa.test("ab")
    assert not nfa.test("abc")

    assert nfa.test("")
    assert nfa.test("a")
    assert nfa.test("aa")
    assert nfa.test("aaa")


def test_plus():
    converter = RegexToNFAConverter("a+")
    nfa = converter.parse()

    expected_nfa = plus(
        char("a")
    )

    diff = DeepDiff(expected_nfa, nfa)
    assert not diff

    assert not nfa.test("")
    assert not nfa.test("b")
    assert not nfa.test("bc")

    assert nfa.test("a")
    assert nfa.test("aa")
    assert nfa.test("aaa")


def test_parentheses():
    converter = RegexToNFAConverter("a(b|c)d")
    nfa = converter.parse()

    expected_nfa = concat(
        char("a"),
        union(
            char("b"),
            char("c"),
        ),
        char("d")
    )

    diff = DeepDiff(expected_nfa, nfa)
    assert not diff

    assert not nfa.test("ad")
    assert not nfa.test("bd")
    assert not nfa.test("cd")
    assert not nfa.test("a")
    assert not nfa.test("d")
    assert not nfa.test("b")
    assert not nfa.test("c")
    assert not nfa.test("")

    assert nfa.test("abd")
    assert nfa.test("acd")


def test_complex():
    converter = RegexToNFAConverter("((ab)|(ba))")
    nfa = converter.parse()

    expected_nfa = union(
        concat(
            char("a"),
            char("b"),
        ),
        concat(
            char("b"),
            char("a")
        )
    )

    diff = DeepDiff(expected_nfa, nfa)
    assert not diff

    assert not nfa.test("a")
    assert not nfa.test("b")
    assert not nfa.test("aa")
    assert not nfa.test("bb")
    assert not nfa.test("")

    assert nfa.test("ab")
    assert nfa.test("ba")


class TestComplex:
    def test_1(self):
        converter = RegexToNFAConverter("((ab)|(ba))*")
        nfa = converter.parse()

        expected_nfa = rep(
            union(
                concat(
                    char("a"),
                    char("b"),
                ),
                concat(
                    char("b"),
                    char("a")
                )
            )
        )

        diff = DeepDiff(expected_nfa, nfa)
        assert not diff

        assert not nfa.test("a")
        assert not nfa.test("b")
        assert not nfa.test("aa")
        assert not nfa.test("bb")

        assert nfa.test("ab")
        assert nfa.test("ba")
        assert nfa.test("")

    def test_2(self):
        converter = RegexToNFAConverter("((ab)|(ba))*(a|b)*")
        nfa = converter.parse()

        expected_nfa = concat(
            rep(
                union(
                    concat(
                        char("a"),
                        char("b"),
                    ),
                    concat(
                        char("b"),
                        char("a")
                    )
                )
            ),
            rep(
                union(
                    char("a"),
                    char("b")
                )
            )
        )

        diff = DeepDiff(expected_nfa, nfa)
        assert not diff

        assert not nfa.test("abc")
        assert not nfa.test("cab")
        assert not nfa.test("abac")
        assert not nfa.test("abacaba")

        assert nfa.test("abbaaa")
        assert nfa.test("ab")
        assert nfa.test("ba")
        assert nfa.test("a")
        assert nfa.test("")

    def test_3(self):
        converter = RegexToNFAConverter("(a|b)*abb")
        nfa = converter.parse()

        expected_nfa = concat(
            rep(
                union(
                    char("a"),
                    char("b")
                )
            ),
            char("a"),
            char("b"),
            char("b")
        )

        diff = DeepDiff(expected_nfa, nfa)
        assert not diff

        assert not nfa.test("bbaaab")
        assert not nfa.test("ab")

        assert nfa.test("aabb")
        assert nfa.test("babb")
        assert nfa.test("abb")
        assert nfa.test("aaabb")
        assert nfa.test("bbabb")

    def test_4(self):
        converter = RegexToNFAConverter("a+b+c")
        nfa = converter.parse()

        expected_nfa = concat(
            plus(
                char("a")
            ),
            plus(
                char("b")
            ),
            char("c")
        )

        diff = DeepDiff(expected_nfa, nfa)
        assert not diff

        assert not nfa.test("abbccc")
        assert not nfa.test("abca")
        assert not nfa.test("ab")

        assert nfa.test("aaabbc")

    def test_5(self):
        converter = RegexToNFAConverter("a*b*c*")
        nfa = converter.parse()

        expected_nfa = concat(
            rep(
                char("a")
            ),
            rep(
                char("b")
            ),
            rep(
                char("c")
            )
        )

        diff = DeepDiff(expected_nfa, nfa)
        assert not diff

        assert not nfa.test("aaccbb")

        assert nfa.test("abc")
        assert nfa.test("bbbcccc")
        assert nfa.test("cccccccc")
        assert nfa.test("aaabbc")
