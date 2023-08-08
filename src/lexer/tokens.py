import enum
from dataclasses import dataclass
from typing import Optional, Dict


class TokenType(enum.StrEnum):
    #  Base class for Token types

    @classmethod
    def as_dict(cls) -> Dict[str, str]:
        return {key: str(t) for key, t in cls.__members__.items()}


               
class SingleCharTokenType(TokenType):
    # Single character tokens
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


class OperatorTokenType(TokenType):
    EQUAL = "="
    NOT_EQUAL = "!="
    EQUAL_EQUAL = "=="
    NOT = "!" 
    GREATER_THAN = ">"
    GREATER_THAN_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_EQUAL = "<="
    SLASH = "/"

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
    literal: Optional[str] 
    line: int 
    
