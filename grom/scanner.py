from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


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


def token_error(lexeme, message, at_end=False, ignore_errors=False):
    """
    Print an error to screen with an indicator pointing to the exact lexeme

    Parameters
    ----------
    lexeme: Lexeme
    message: str
    at_end: bool
    ignore_errors: bool
    """
    print(f"Error encountered at line {lexeme.line_number + 1} in file {lexeme.file}")
    print(f"{lexeme.line.rstrip()}")
    skip = lexeme.col + len(lexeme.value) + 1 if at_end else lexeme.col
    print(f'{" " * skip}^')
    print(f"./{lexeme.file}:{lexeme.line_number + 1}:{lexeme.col + 1}: {message}")
    print()

    if not ignore_errors:
        raise UserWarning("token error")
        # sys.exit(1)


# def is_alpha(c):
#     return ord("a") <= ord(c) <= ord("z") or ord("A") <= ord(c) <= ord("Z")
#
#
# def is_digit(c):
#     return ord("0") <= ord(c) <= ord("9")
#
#
# def is_alphanum(c):
#     return is_alpha(c) or is_digit(c)


def is_comment(c):
    return c == "#"


def is_grouping(c):
    return c in "()[]{},:"


# def is_symbol(c):
#     return c in ".,:;@*^-+=&%$!/<>|?"


def is_string_terminator(c):
    return c == '"'


class Scanner:
    def __init__(self, path, data, ignore_errors=False):
        self._path: str = path
        self._data: str = data
        self._ignore_errors: bool = ignore_errors
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

    # def consume_number(self):
    #     self.mark()
    #     while self.can_peek() and (is_digit(self.peek()) or self.peek() == "."):
    #         self.advance()
    #     self.advance()

    def consume_comment(self):
        # Will consume line until newline has been consumed
        while not self.at_end() and self.current_character() != "\n":
            self.advance()

    # def consume_symbol(self):
    #     # merge single operators
    #     # TODO: make sure this is what we want, e.g. ?!%& is legal
    #     self.mark()
    #     if is_symbol(self.current_character()):
    #         while self.can_peek() and is_symbol(self.peek()):
    #             self.advance()
    #     self.advance()

    def consume_string(self):
        self.mark()

        while self.can_peek() and not is_string_terminator(self.peek()):
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
            token_error(self.create_lexeme(), "unterminated string")

        self.advance()

    def character_marker(self, name):
        """ Creates a lexeme that points at the current character """
        lno = self._line_number
        col = self._column
        line = self._get_line()
        idx = self._index
        return Lexeme(lno, col, line, self._path, index=idx, value=name)


def scanner(path, ignore_errors=False, data=None):
    """
    Scans a `grom` source and generates Lexemes

    Parameters
    ----------
    path: str
        Path to a file containing `grom` source or a name if data is provided

    ignore_errors: bool
        Enabling this will keep outputting error to stdout instead of stopping at the
        first error encountered.

    data: str
        source of a `grom` program in `str` form.

    Yields
    -------
    Lexeme

    """
    if data is None:
        with open(path, "r") as f:
            data = f.read()

    scn = Scanner(path, data, ignore_errors=ignore_errors)

    while not scn.at_end():
        c = scn.current_character()

        if c == "\n":
            if scn.is_marked():
                yield scn.create_lexeme()
            yield scn.eol_marker()
            scn.newline()

        elif is_comment(c):
            if scn.is_marked():
                yield scn.create_lexeme()
            scn.consume_comment()

        # elif is_digit(c) and not scn.is_marked():
        #     # number
        #     scn.consume_number()
        #     yield scn.create_lexeme()

        elif is_grouping(c):
            # grouping and operators
            if scn.is_marked():
                yield scn.create_lexeme()
            # scn.consume_symbol()
            scn.mark()
            scn.advance()
            yield scn.create_lexeme(LexemeType.GROUPING)

        elif is_string_terminator(c):
            if scn.is_marked():
                token_error(scn.character_marker('"'), "misplaced string terminator")
            scn.consume_string()
            yield scn.create_lexeme(LexemeType.STRING)

        elif not c.isspace() and not scn.is_marked():
            # start a lexeme
            scn.mark()
            scn.advance()
        elif c.isspace() and scn.is_marked():
            # finish lexeme
            yield scn.create_lexeme()
            scn.advance()
        else:
            scn.advance()

    if scn.is_marked():
        yield scn.create_lexeme()
    yield scn.eof_marker()
