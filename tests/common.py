from dataclasses import fields
from typing import List

from grom.scanner import scanner, Lexeme


def check_scanning(data, expected_lexemes, ignore_errors=False):
    lexemes = scanner(path='testing', data=data, ignore_errors=ignore_errors)
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


def check_scanning_lexemes(data, expected_lexemes: List[Lexeme], ignore_errors=False):
    lexemes = scanner(path='testing', data=data, ignore_errors=ignore_errors)
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
