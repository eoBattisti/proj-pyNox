from typing import List, Optional

from .tokens import (KeywordTokens, LiteralTokenType, OperatorTokenType, Token, 
                     EOFTokenType, SingleCharTokenType, TokenType) 
from ..exceptions import PyNoxSyntaxError

__all__  = ["Lexer"]

class Lexer:

    def __init__(self, source: str) -> None:
        self.source: str = source
        self.tokens: List[Token] = list()
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1

    def scan_tokens(self) -> List[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(token_type=EOFTokenType.EOF,
                                 lexeme="",
                                 literal=None,
                                 line=self.line))
        return self.tokens

    def scan_token(self) -> None:
        char: str = self.advance()
        match char:
            case '(':
                self.add_token(token_type=SingleCharTokenType.LEFT_PAREN)
            case ')':
                self.add_token(token_type=SingleCharTokenType.RIGHT_PAREN)
            case '{':
                self.add_token(token_type=SingleCharTokenType.LEFT_BRACE)
            case '}':
                self.add_token(token_type=SingleCharTokenType.RIGHT_BRACE)
            case ',':
                self.add_token(token_type=SingleCharTokenType.COMMA)
            case '.':
                self.add_token(token_type=SingleCharTokenType.DOT)
            case '-':
                self.add_token(token_type=SingleCharTokenType.MINUS)
            case '+':
                self.add_token(token_type=SingleCharTokenType.PLUS)
            case ';':
                self.add_token(token_type=SingleCharTokenType.SEMICOLON)
            case '*':
                self.add_token(token_type=SingleCharTokenType.STAR)
            case '!':
                if self.match('='):
                    self.add_token(token_type=OperatorTokenType.NOT_EQUAL)
                else: 
                    self.add_token(token_type=OperatorTokenType.NOT)
            case '=':
                if self.match('='):
                    self.add_token(token_type=OperatorTokenType.EQUAL_EQUAL)
                else:
                    self.add_token(token_type=OperatorTokenType.EQUAL)
            case '<':
                if self.match('='):
                    self.add_token(token_type=OperatorTokenType.LESS_THAN_EQUAL)
                else:
                    self.add_token(token_type=OperatorTokenType.LESS_THAN)
            case '>':
                if self.match('='):
                    self.add_token(token_type=OperatorTokenType.GREATER_THAN_EQUAL)
                else:
                    self.add_token(token_type=OperatorTokenType.GREATER_THAN)
            case '/':
                if self.match('/'):
                    while self.peek() != '\n' and not self.is_at_end():
                        self.advance()
                else:
                    self.add_token(token_type=OperatorTokenType.SLASH)
            case ' ':
                pass
            case '\r':
                pass
            case '\t':
                pass
            case '\n':
                self.line += 1
            case '"':
                self.process_string()
            case _:
                if char.isdigit():
                    self.process_number()
                elif char.isalpha():
                    self.add_token(token_type=LiteralTokenType.IDENTIFIER)

                else:
                    raise PyNoxSyntaxError(f"Unexpected character: {char}") 
    def identifier(self) -> None:
        while self.peek().isalnum():
            self.advance()
        text: str = self.source[self.start:self.current]
        token_type = KeywordTokens.as_dict().get(text)        
        if not TokenType:
            token_type = LiteralTokenType.IDENTIFIER
        self.add_token(token_type=KeywordTokens(token_type))
    
    def process_number(self) -> None:
        while self.peek().isdigit():
            self.advance()

        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()

        self.add_token(token_type=LiteralTokenType.NUMBER,
                       literal=self.source[self.start:self.current])
    

    def process_string(self) -> None:
        while self.peek() != '"':
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            raise PyNoxSyntaxError("Unterminated string")
        
        self.advance()

        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(token_type=LiteralTokenType.STRING, literal=value)

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char

    def match(self, char: str) -> bool:
        if self.is_at_end() or self.source[self.current] != char:
            return False
        self.current += 1
        return True
    
    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def add_token(self, token_type: TokenType,  literal: Optional[str] = None) -> None:
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type=token_type,
                                 lexeme=text,
                                 literal=literal,
                                 line=self.line))

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
