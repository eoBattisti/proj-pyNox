from typing import List

from ..exceptions import PyNoxParserError
from ..interpreter.expression import Binary, Expression, Grouping, Literal, Unary
from ..lexer.tokens import EOFTokenType, KeywordTokens, LiteralTokenType, OperatorTokenType, SingleCharTokenType, Token, TokenType
from ..logger import Logger


class Parser:

    def __init__(self, * , logger: Logger, tokens: List[Token], debug: bool = False) -> None:
        self.tokens = tokens
        self.__debug = debug
        self.__logger = logger
        self.current = 0

    def parse(self):
        try:
            return self.expression()
        except PyNoxParserError as error:
            self.__logger.error(str(error))

    def expression(self) -> Expression:
        return self.equality()

    def equality(self) -> Expression:
        expression = self.comparison()

        while self.__match(OperatorTokenType.BANG_EQUAL, OperatorTokenType.EQUAL_EQUAL):
            operator = self.__previous()
            right = self.comparison()
            expression = Binary(expression, operator, right)
        return expression


    def comparison(self) -> Expression:
        expression = self.term()

        while self.__match(OperatorTokenType.GREATER, OperatorTokenType.GREATER_EQUAL,
                           OperatorTokenType.LESS, OperatorTokenType.LESS_EQUAL):
            operator = self.__previous()
            right = self.term()
            expression = Binary(left=expression, operator=operator, right=right)

        return expression

    def term(self) -> Expression:
        expression = self.factor()

        while self.__match(SingleCharTokenType.MINUS, SingleCharTokenType.PLUS):
            operator = self.__previous()
            right = self.factor()
            expression = Binary(left=expression,  operator=operator, right=right)

        return expression

    def factor(self) -> Expression:

        expression = self.unary()

        while self.__match(SingleCharTokenType.SLASH, SingleCharTokenType.STAR):
            operator = self.__previous()
            right = self.unary()
            expression = Binary(left=expression, operator=operator, right=right)
        return expression

    def unary(self) -> Expression:

        if self.__match(OperatorTokenType.BANG, SingleCharTokenType.MINUS):
            operator = self.__previous()
            right = self.unary()
            return Unary(operator=operator, right=right)

        return self.primary() 

    def primary(self) -> Expression:

        if self.__match(KeywordTokens.FALSE):
            return Literal(value=False)
        if self.__match(KeywordTokens.TRUE):
            return Literal(value=True)
        if self.__match(KeywordTokens.NIL):
            return Literal(value=None)

        if self.__match(LiteralTokenType.NUMBER, LiteralTokenType.STRING):
            return Literal(self.__previous().literal)

        if self.__match(SingleCharTokenType.LEFT_PAREN):
            expression = self.expression()
            self.__consume(SingleCharTokenType.RIGHT_PAREN, 'Expect ) after expression')
            return Grouping(expression=expression)

        self.__error(self.__peek(), "Expect expression")

    def __consume(self, type: TokenType, message: str):
        if self.__check(type=type):
            return self.__advance()
        self.__error(self.__peek(), message)

    def __error(self, token: Token, message: str):
        if self.__debug:
            self.__logger.error(f"{token.line} at end {message}")
        raise PyNoxParserError(message=f'{message} at {token.line}')

    def __synchronize(self) -> None:
        self.__advance()

        while not self.__is_at_end():
            if self.__previous() in [
                KeywordTokens.CLASS,
                KeywordTokens.FUNCTION,
                KeywordTokens.VAR,
                KeywordTokens.FOR,
                KeywordTokens.IF,
                KeywordTokens.WHILE,
                KeywordTokens.PRINT,
                KeywordTokens.RETURN
            ]:
                return
            self.__advance()

    def __match(self, *types: TokenType) -> bool:
        for type in types:
            if self.__check(type):
                self.__advance()
                return True
        return False

    def __check(self, type: TokenType) -> bool:
        if not self.__is_at_end():
            return self.__peek().token_type == type
        return False

    def __advance(self):
        if not self.__is_at_end():
            self.current += 1
        return self.__previous()

    def __is_at_end(self) -> bool:
        return self.__peek().token_type == EOFTokenType.EOF 

    def __peek(self) -> Token:
        return self.tokens[self.current]

    def __previous(self) -> Token:
        return self.tokens[self.current - 1]
