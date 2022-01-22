import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from grom import assert_exhaustive_enum


class LexemeType(Enum):
    DEFAULT = auto()
    GROUPING = auto()
    STRING = auto()
    EOL = auto()
    EOF = auto()


@dataclass
class Lexeme:
    line_number: int
    col: int
    line: str  # a string that represents the content of the current line
    file: str  # filename or label of the
    index: int  # index into the original data string
    value: Optional[str] = None
    type: LexemeType = LexemeType.DEFAULT


def compiler_error(lexeme, message, at_end=False):
    """
    Print an error to screen with an indicator pointing to the exact lexeme

    Parameters
    ----------
    lexeme: Lexeme
        the lexeme object to use as a reference for source location
    message: str
        message to print as part of the error
    at_end: bool
        move the error pointer to the end of the lexeme
    """
    skip = lexeme.col + len(lexeme.value) + 1 if at_end else lexeme.col  # pos of ^
    lines = [
        f"Error encountered at line {lexeme.line_number + 1} in file {lexeme.file}",
        f"{lexeme.line.rstrip()}",
        f'{" " * skip}^',
        f"./{lexeme.file}:{lexeme.line_number + 1}:{lexeme.col + 1}: ERROR: {message}",
    ]

    print('\n'.join(lines), file=sys.stderr)

    exit(1)


class Scanner:
    def __init__(self, path, data):
        self._path: str = path
        self._data: str = data
        self._line_number: int = 0
        self._line_start = 0
        self._column: int = 0
        self._index: int = 0
        self._current_lexeme: Optional[Lexeme] = None

    def newline(self):
        self._index += 1
        self._line_number += 1
        self._line_start = self._index
        self._column = 0

    def advance(self):
        self._index += 1
        self._column += 1

    def at_end(self):
        return self._index == len(self._data)

    def can_peek(self):
        return self._index < len(self._data) - 1

    def peek(self):
        if not self.can_peek():
            assert False, "Can't peek beyond end of string!"
        return self._data[self._index + 1]

    def current_character(self):
        return self._data[self._index]

    def _get_line(self):
        start = self._line_start
        eol = self._data.find("\n", start)

        if eol == -1:
            eol = len(self._data)

        return self._data[start:eol]

    def create_lexeme(self, lexeme_type=LexemeType.DEFAULT):
        lexeme = self._current_lexeme
        idx = lexeme.index
        lexeme.value = self._data[idx: self._index]
        self._current_lexeme = None
        lexeme.type = lexeme_type
        return lexeme

    def mark(self):
        """
        Mark the current position as the start of a lexeme.
        """
        lno = self._line_number
        col = self._column
        line = self._get_line()
        idx = self._index
        path = self._path
        self._current_lexeme = Lexeme(lno, col, line, path, idx)

    def is_marked(self):
        """
        Has a mark been set?
        Returns
        -------
        bool
        """
        return self._current_lexeme is not None

    def _create_marker(self, name, lexeme_type):
        return Lexeme(
            line_number=self._line_number,
            col=self._column,
            line=self._get_line(),
            file=self._path,
            index=self._index,
            value=name,
            type=lexeme_type
        )

    def eol_marker(self):
        return self._create_marker("EOL", LexemeType.EOL)

    def eof_marker(self):
        return self._create_marker("EOF", LexemeType.EOF)

    def consume_comment(self):
        # Will consume line until newline has been consumed
        while not self.at_end() and self.current_character() != "\n":
            self.advance()

    def consume_string(self):
        self.mark()

        while self.can_peek() and not self.peek() == '"':
            if self.peek() == "\\":
                self.advance()  # TODO: safe to skip escape character?
                # check escaped character
                if self.can_peek() and self.peek() == '"':
                    # skip escaped quote
                    self.advance()
            elif self.current_character() == "\n":
                self.newline()
            else:
                self.advance()
        self.advance()

        if self.at_end():
            self.char_error("unterminated string")

        self.advance()

    def character_marker(self, name):
        """ Creates a lexeme that points at the current character """
        lno = self._line_number
        col = self._column
        line = self._get_line()
        idx = self._index
        return Lexeme(lno, col, line, self._path, index=idx, value=name)

    def scanner_error(self, message):
        compiler_error(self.create_lexeme(), message)

    def char_error(self, message):
        compiler_error(self.character_marker('"'), message)


def scanner(path, data=None):
    """
    Scans a `grom` source and generates Lexemes

    Parameters
    ----------
    path: str
        Path to a file containing `grom` source or a name if data is provided

    data: str
        source of a `grom` program in `str` form.

    Yields
    -------
    Lexeme

    """
    if data is None:
        with open(path, "r") as f:
            data = f.read()

    scn = Scanner(path, data)
    assert_exhaustive_enum(LexemeType, 5)

    while not scn.at_end():
        c = scn.current_character()

        match c:
            case '\n':
                # newline
                if scn.is_marked():
                    yield scn.create_lexeme()
                yield scn.eol_marker()
                scn.newline()
            case '#':
                # comment
                if scn.is_marked():
                    yield scn.create_lexeme()
                scn.consume_comment()
            case '(' | ')' | '[' | ']' | '{' | '}' | ',' | ':':
                # grouping
                if scn.is_marked():
                    yield scn.create_lexeme()
                scn.mark()
                scn.advance()
                yield scn.create_lexeme(LexemeType.GROUPING)
            case '"':
                # string
                if scn.is_marked():
                    scn.char_error("misplaced string terminator")
                scn.consume_string()
                yield scn.create_lexeme(LexemeType.STRING)
            case char if not char.isspace() and not scn.is_marked():
                # start a lexeme
                scn.mark()
                scn.advance()
            case char if char.isspace() and scn.is_marked():
                # finish current lexeme
                yield scn.create_lexeme()
                scn.advance()
            case _:
                scn.advance()

    if scn.is_marked():
        yield scn.create_lexeme()
    yield scn.eof_marker()
