from dataclasses import fields
from typing import List, Generator, Tuple, Any

from grom.lexer import lexer, TokenType
from grom.scanner import scanner, Lexeme


def check_scanning(data, expected_lexemes):
    lexemes = scanner(path='testing', data=data)
    for lexeme, expected in zip(lexemes, expected_lexemes, strict=True):
        # print(lexeme)
        if lexeme.value != expected:
            print()
            print('---=== Lexeme Mismatch ===---')
            print(f'value         : \'{lexeme.value}\' != \'{expected}\'')
            print(f'value type    : {type(lexeme.value).__name__}')
            print(f'expected type : {type(expected).__name__}')
            print(lexeme)

        assert lexeme.value == expected


def check_scanning_lexemes(data, expected_lexemes: List[Lexeme]):
    lexemes = scanner(path='testing', data=data)
    for lexeme, expected in zip(lexemes, expected_lexemes, strict=True):
        if lexeme != expected:
            print()
            print('---=== Lexeme Mismatch ===---')
            print(f'lexeme    : {expected.value}')
            for field in fields(lexeme):
                lexeme_value = getattr(lexeme, field.name)
                expected_value = getattr(expected, field.name)
                if lexeme_value != expected_value:
                    print(f'{field.name:<10}: "{lexeme_value}" != "{expected_value}"')

        assert lexeme == expected


def check_lexing(data: str, expected_tokens: List[Tuple[Any, TokenType]]):
    lexemes = scanner(path='testing', data=data)
    tokens = lexer(lexemes)

    for token, expected_token in zip(tokens, expected_tokens, strict=True):
        if token.value != expected_token[0] or token.type != expected_token[1]:
            print()
            print('---=== Token Mismatch ===---')
            if token.value != expected_token[0]:
                print(f'value    : \'{token.value}\' != \'{expected_token[0]}\'')
            if token.type != expected_token[1]:
                print(f'type     : {token.type} != {expected_token[1]}')
            print(f'token    : {token}')
            assert False, "Token mismatch"
