from .tokens import LiteralTokenType, OperatorTokenType, Token, EOFTokenType, SingleCharTokenType, TokenType 
from ..exceptions import PyNoxSyntaxError

__all__ : tuple[str, ...] = (
    "Lexer",
)

class Lexer:

    def __init__(self, source: str):
        self.source: str = source
        self.tokens: list[Token] = list()
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(EOFTokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        char = self.advance()
        match char:
            case '(':
                self.add_token(SingleCharTokenType.LEFT_PAREN)
            case ')':
                self.add_token(SingleCharTokenType.RIGHT_PAREN)
            case '{':
                self.add_token(SingleCharTokenType.LEFT_BRACE)
            case '}':
                self.add_token(SingleCharTokenType.RIGHT_BRACE)
            case ',':
                self.add_token(SingleCharTokenType.COMMA)
            case '.':
                self.add_token(SingleCharTokenType.DOT)
            case '-':
                self.add_token(SingleCharTokenType.MINUS)
            case '+':
                self.add_token(SingleCharTokenType.PLUS)
            case ';':
                self.add_token(SingleCharTokenType.SEMICOLON)
            case '*':
                self.add_token(SingleCharTokenType.STAR)
            case '!':
                if self.match('='):
                    self.add_token(OperatorTokenType.NOT_EQUAL)
                else 
                    self.add_token(OperatorTokenType.NOT)
            case '=':
                if self.match('='):
                    self.add_token(OperatorTokenType.EQUAL_EQUAL))
                else:
                    self.add_token(OperatorTokenType.EQUAL)
            case '<':
                if self.match('='):
                    self.add_token(OperatorTokenType.LESS_THAN_EQUAL)
                else:
                    self.add_token(OperatorTokenType.LESS_THAN)
            case '>':
                if self.match('='):
                    self.add_token(OperatorTokenType.GREATER_THAN_EQUAL)
                else:
                    self.add_token(OperatorTokenType.GREATER_THAN)
            case '/':
                if self.match('/'):
                    while self.peek() != '\n' and not self.is_at_end():
                        self.advance()
                else:
                    self.add_token(OperatorTokenType.SLASH)
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
                raise PyNoxSyntaxError(f"Unexpected character: {char}") 
    
    def process_string(self):
        while self.peek() != '"':
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            raise PyNoxSyntaxError("Unterminated string", self.line)
        
        self.advance()

        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(LiteralTokenType.STRING, value)

    def advance(self):
        self.current += 1
        return self.source[self.current]

    def match(self, char: str):
        if self.is_at_end() or self.source[self.current] != char:
            return False
        self.current += 1
        return True
    
    def peek(self):
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def add_token(self, token_type: TokenType,  literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
