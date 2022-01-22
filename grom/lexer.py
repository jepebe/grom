from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Generator, Union

from grom import assert_exhaustive_enum
from grom.scanner import Lexeme, compiler_error, LexemeType


class TokenType(Enum):
    INTEGER = auto()
    GROUP = auto()
    STRING = auto()
    KEYWORD = auto()
    WORD = auto()
    EOL = auto()


class Keyword(Enum):
    PRINT_RAX = 'print_rax'
    IF = 'if'


class Intrinsic(Enum):
    PLUS = '+'


@dataclass
class Token:
    loc: Lexeme
    value: Union[int, str, None]
    type: TokenType


def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_keyword(value):
    try:
        Keyword(value)
        return True
    except ValueError:
        return False


def is_intrinsic(value):
    try:
        Intrinsic(value)
        return True
    except ValueError:
        return False


def lexer(lexemes: Generator[Lexeme, None, None]):
    assert_exhaustive_enum(TokenType, 6)
    for lexeme in lexemes:
        match lexeme.type:
            case LexemeType.DEFAULT:
                match lexeme.value:
                    case keyword if is_keyword(keyword):
                        yield Token(lexeme, keyword, TokenType.KEYWORD)
                    case number if is_integer(number):
                        yield Token(lexeme, int(number), TokenType.INTEGER)
                    case identifier:
                        yield Token(lexeme, identifier, TokenType.WORD)
                    # case _:
                    #     assert False, f"not implemented yet for {lexeme}"
            case LexemeType.STRING:
                yield Token(lexeme, lexeme.value, TokenType.STRING)
            case LexemeType.GROUPING:
                yield Token(lexeme, lexeme.value, TokenType.GROUP)
            case LexemeType.EOL | LexemeType.EOF:
                yield Token(lexeme, lexeme.value, TokenType.EOL)
            case _:
                assert False, "unreachable"
