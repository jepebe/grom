import pytest

from grom.scanner import Lexeme, LexemeType
from tests.common import check_scanning, check_scanning_lexemes


def test_double_quote_string():
    data = """\"hello, world!\""""
    expected = ['"hello, world!"', "EOF"]
    check_scanning(data, expected)


def test_double_inside_double_quote_string_raises():
    data = """\"hello,"world!\""""
    expected = ['"hello,"', "world", "!", '"', "EOF"]

    with pytest.raises(SystemExit):
        check_scanning(data, expected)


def test_single_inside_double_quote_string():
    data = """\"hello, ' world!\""""
    expected = ['"hello, \' world!"', "EOF"]
    check_scanning(data, expected)


def test_escaped_double_inside_double_quote_string():
    data = """\"hello, \\" world!\""""
    expected = ['"hello, \\" world!"', "EOF"]
    check_scanning(data, expected)


def test_multiple_strings():
    data = '''"hello," "world!"'''
    expected = ['"hello,"', '"world!"', "EOF"]
    check_scanning(data, expected)


def test_strings_with_newline():
    data = '''"hello, \n world!"'''
    expected = ['"hello, \n world!"', "EOF"]
    check_scanning(data, expected)

    expected = [
        Lexeme(0, 0, '"hello, ', "testing", 0, data, LexemeType.STRING),
        Lexeme(1, 8, ' world!"', "testing", 17, "EOF", LexemeType.EOF),
    ]
    check_scanning_lexemes(data, expected)
