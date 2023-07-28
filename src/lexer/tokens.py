from enum import StrEnum
import enum

class TokenType(StrEnum):
    #  Base class for Token types

    @classmethod
    def as_dict(cls):
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
    VAR = "var"
    FUNCTION = "fun"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    FOR = "for"
    RETURN = "return"
    CONTINUE = "continue"
    BREAK = "break"
    AND = "and"
    OR = "or"
    TRUE = "true"
    FALSE = "false"
    NIL = "nil"
    PRINT = "print"
    SUPER = "super"


class EOFTokenType(TokenType):
    EOF = enum.auto()


class LiteralTokenType(TokenType):
    SINGLE_QUOTE = "'"
    DOUBLE_QUOTE = '"'
    NUMBER = enum.auto()
    STRING = enum.auto()
    IDENTIFIER = enum.auto()

class Token:

    def __init__(self, ttype: TokenType, lexeme: str, literal, line: int) -> None: 
        self.ttype = ttype
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    
    def __str__(self) -> str:
        return f"{self.ttype} {self.lexeme} {self.literal}"
