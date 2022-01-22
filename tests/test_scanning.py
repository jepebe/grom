from grom import assert_exhaustive_enum
from grom.scanner import Lexeme, LexemeType
from tests.common import check_scanning, check_scanning_lexemes


def test_basic_scanning():
    data = ("1 2 4 8 16\n"
            "'c' \"unspaced_string\"\n"
            "0.54 4564\n"
            "method(a,b)\n"
            "array[c:d] = {}\n"
            "identifier")

    expected = ['1', '2', '4', '8', '16', 'EOL',
                '\'c\'', '"unspaced_string"', 'EOL',
                '0.54', '4564', 'EOL',
                'method', '(', 'a', ',', 'b', ')', 'EOL',
                'array', '[', 'c', ':', 'd', ']', '=', '{', '}', 'EOL',
                'identifier', 'EOF']

    check_scanning(data, expected)

    lines = ['1 2 4 8 16',
             '\'c\' \"unspaced_string\"',
             "0.54 4564",
             "method(a,b)",
             "array[c:d] = {}",
             "identifier"]
    expected = [
        Lexeme(0, 0, lines[0], 'testing', 0, '1'),
        Lexeme(0, 2, lines[0], 'testing', 2, '2'),
        Lexeme(0, 4, lines[0], 'testing', 4, '4'),
        Lexeme(0, 6, lines[0], 'testing', 6, '8'),
        Lexeme(0, 8, lines[0], 'testing', 8, '16'),
        Lexeme(0, 10, lines[0], 'testing', 10, 'EOL', LexemeType.EOL),
        Lexeme(1, 0, lines[1], 'testing', 11, '\'c\''),
        Lexeme(1, 4, lines[1], 'testing', 15, '\"unspaced_string\"', LexemeType.STRING),
        Lexeme(1, 21, lines[1], 'testing', 32, 'EOL', LexemeType.EOL),
        Lexeme(2, 0, lines[2], 'testing', 33, '0.54'),
        Lexeme(2, 5, lines[2], 'testing', 38, '4564'),
        Lexeme(2, 9, lines[2], 'testing', 42, 'EOL', LexemeType.EOL),
        Lexeme(3, 0, lines[3], 'testing', 43, 'method'),
        Lexeme(3, 6, lines[3], 'testing', 49, '(', LexemeType.GROUPING),
        Lexeme(3, 7, lines[3], 'testing', 50, 'a'),
        Lexeme(3, 8, lines[3], 'testing', 51, ',', LexemeType.GROUPING),
        Lexeme(3, 9, lines[3], 'testing', 52, 'b'),
        Lexeme(3, 10, lines[3], 'testing', 53, ')', LexemeType.GROUPING),
        Lexeme(3, 11, lines[3], 'testing', 54, 'EOL', LexemeType.EOL),
        Lexeme(4, 0, lines[4], 'testing', 55, 'array'),
        Lexeme(4, 5, lines[4], 'testing', 60, '[', LexemeType.GROUPING),
        Lexeme(4, 6, lines[4], 'testing', 61, 'c'),
        Lexeme(4, 7, lines[4], 'testing', 62, ':', LexemeType.GROUPING),
        Lexeme(4, 8, lines[4], 'testing', 63, 'd'),
        Lexeme(4, 9, lines[4], 'testing', 64, ']', LexemeType.GROUPING),
        Lexeme(4, 11, lines[4], 'testing', 66, '='),
        Lexeme(4, 13, lines[4], 'testing', 68, '{', LexemeType.GROUPING),
        Lexeme(4, 14, lines[4], 'testing', 69, '}', LexemeType.GROUPING),
        Lexeme(4, 15, lines[4], 'testing', 70, 'EOL', LexemeType.EOL),
        Lexeme(5, 0, lines[5], 'testing', 71, 'identifier'),
        Lexeme(5, 10, lines[5], 'testing', 81, 'EOF', LexemeType.EOF),
    ]
    check_scanning_lexemes(data, expected)
    assert_exhaustive_enum(LexemeType, 5)


def test_token_splitting_input():
    data = "func(a,b) array[c:d] set{e,f,0.5} dict{g:1,h:2} struct.field"
    expected = ['func', '(', 'a', ',', 'b', ')',
                'array', '[', 'c', ':', 'd', ']',
                'set', '{', 'e', ',', 'f', ',', '0.5', '}',
                'dict', '{', 'g', ':', '1', ',', 'h', ':', '2', '}',
                'struct.field', 'EOF']

    check_scanning(data, expected)


def test_operator_scanning():
    data = '1 <= 2  5 + -3.5 >>>'
    expected = ['1', '<=', '2', '5', '+', '-3.5', '>>>', 'EOF']
    check_scanning(data, expected)


def test_comments():
    data = ("# comment\n"
            "value + other # comment\n")
    expected = ['EOL', 'value', '+', 'other', 'EOL', 'EOF']
    check_scanning(data, expected)
