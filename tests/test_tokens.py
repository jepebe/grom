from grom import assert_exhaustive_enum
from grom.lexer import TokenType, Keyword
from tests.common import check_lexing


def test_simple_expression():
    data = "100 + 2 * (4 + 5) / 3"

    expected = [
        (100, TokenType.INTEGER),
        ('+', TokenType.WORD),
        (2, TokenType.INTEGER),
        ('*', TokenType.WORD),
        ('(', TokenType.GROUP),
        (4, TokenType.INTEGER),
        ('+', TokenType.WORD),
        (5, TokenType.INTEGER),
        (')', TokenType.GROUP),
        ('/', TokenType.WORD),
        (3, TokenType.INTEGER),
        ('EOF', TokenType.EOL)
    ]
    check_lexing(data, expected)


def test_another_expression():
    data = 'sys.write("hello, world!")'

    expected = [
        ('sys.write', TokenType.WORD),
        ('(', TokenType.GROUP),
        ('"hello, world!"', TokenType.STRING),
        (')', TokenType.GROUP),
        ('EOF', TokenType.EOL)
    ]
    check_lexing(data, expected)
    assert_exhaustive_enum(TokenType, 6)


def test_keywords():
    data = [keyword.value for keyword in Keyword]
    data = ' '.join(data)
    expected = [
        ('print_rax', TokenType.KEYWORD),
        ('if', TokenType.KEYWORD),
        ('EOF', TokenType.EOL)
    ]
    assert_exhaustive_enum(Keyword, len(expected) - 1)
    check_lexing(data, expected)
