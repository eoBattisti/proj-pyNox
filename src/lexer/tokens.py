import enum
from dataclasses import dataclass
from typing import Any, Optional, Dict


class TokenType(enum.StrEnum):
    """
    Base class for token types.
    """

    @classmethod
    def as_dict(cls) -> Dict[str, str]:
        """
        Get a dictionary mapping token names to their string representations.

        :return: A dictionary of token names and their string representations.
        """
        return {key: str(t) for key, t in cls.__members__.items()}


               
class SingleCharTokenType(TokenType):
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    RIGHT_BRACKET = "]"
    LEFT_BRACKET = "["
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    COMMA = ","
    DOT = "."
    MINUS = "-"
    PLUS = "+"
    SEMICOLON = ";"
    STAR = "*"
    SLASH = "/"


class OperatorTokenType(TokenType):
    EQUAL = "="
    BANG_EQUAL= "!="
    EQUAL_EQUAL = "=="
    BANG = "!" 
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="

class KeywordTokens(TokenType):
    AND = "and"
    BREAK = "break"
    CLASS = "class"
    CONTINUE = "continue"
    ELSE = "else"
    FALSE = "false"
    FOR = "for"
    FUNCTION = "fun"
    IF = "if"
    NIL = "nil"
    OR = "or"
    PRINT = "print"
    RETURN = "return"
    SUPER = "super"
    THIS = "this"
    TRUE = "true"
    VAR = "var"
    WHILE = "while"


class EOFTokenType(TokenType):
    EOF = enum.auto()


class LiteralTokenType(TokenType):
    SINGLE_QUOTE = "'"
    DOUBLE_QUOTE = '"'
    NUMBER = enum.auto()
    STRING = enum.auto()
    IDENTIFIER = enum.auto()

@dataclass(kw_only=True, frozen=True)
class Token:
    token_type: TokenType
    lexeme: str
    literal: Any
    line: int 
    
