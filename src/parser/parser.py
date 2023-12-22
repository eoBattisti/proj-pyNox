from typing import List

from ..exceptions import PyNoxParserError
from ..interpreter.expression import Assign, Binary, Expr, Grouping, Literal, Unary, Variable
from ..lexer.tokens import EOFTokenType, KeywordTokens, LiteralTokenType, OperatorTokenType, SingleCharTokenType, Token, TokenType
from ..logger import Logger
from ..interpreter.statements import Print, Stmt, Expression, Var


class Parser:

    def __init__(self, * , logger: Logger, tokens: List[Token], debug: bool = False) -> None:
        self.tokens = tokens
        self.__debug = debug
        self.__logger = logger
        self.current = 0

    def parse(self):
        try:
            statements: List[Stmt] = []
            while not self.__is_at_end():
                statements.append(self.__declaration())
            return statements
        except PyNoxParserError as error:
            self.__logger.error(str(error))

    def __declaration(self) -> Stmt:
        try:
            if self.__match(KeywordTokens.VAR):
                return self.__var_declaration()
            return self.__statement()
        except PyNoxParserError:
            self.__synchronize()
            return None

    def __statement(self) -> Stmt: 
        if self.__match(KeywordTokens.PRINT):
            return self.__print_stmt()

        return self.__expression_stmt()

    def __print_stmt(self) -> Stmt:
        value = self.expression()
        self.__consume(SingleCharTokenType.SEMICOLON, "Expected ';' after value.")
        return Print(value)

    def __var_declaration(self) -> Stmt:
        name = self.__consume(LiteralTokenType.IDENTIFIER, "Expected variable name.")
        initializer = None

        if self.__match(OperatorTokenType.EQUAL):
            initializer = self.expression()

        self.__consume(SingleCharTokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return Var(name=name, initializer=initializer)


    def __expression_stmt(self) -> Stmt:
        expression = self.expression()
        self.__consume(SingleCharTokenType.SEMICOLON, "Expected ';' after value.")
        return Expression(expression)

    def __assignment(self) -> Expr:
        expression = self.equality()

        if self.__match(OperatorTokenType.EQUAL):
            equals: Token = self.__previous()
            value = self.__assignment()
            if isinstance(expression, Variable):
                name = expression.name
                return Assign(name=name, value=value)
            self.__error(token=equals, message="Invalid assignmnet target.")

        return expression

    def expression(self) -> Expr:
        return self.__assignment()

    def equality(self) -> Expr:
        expression = self.comparison()

        while self.__match(OperatorTokenType.BANG_EQUAL, OperatorTokenType.EQUAL_EQUAL):
            operator = self.__previous()
            right = self.comparison()
            expression = Binary(expression, operator, right)
        return expression


    def comparison(self) -> Expr:
        expression = self.term()

        while self.__match(OperatorTokenType.GREATER, OperatorTokenType.GREATER_EQUAL,
                           OperatorTokenType.LESS, OperatorTokenType.LESS_EQUAL):
            operator = self.__previous()
            right = self.term()
            expression = Binary(left=expression, operator=operator, right=right)

        return expression

    def term(self) -> Expr:
        expression = self.factor()

        while self.__match(SingleCharTokenType.MINUS, SingleCharTokenType.PLUS):
            operator = self.__previous()
            right = self.factor()
            expression = Binary(left=expression,  operator=operator, right=right)

        return expression

    def factor(self) -> Expr:

        expression = self.unary()

        while self.__match(SingleCharTokenType.SLASH, SingleCharTokenType.STAR):
            operator = self.__previous()
            right = self.unary()
            expression = Binary(left=expression, operator=operator, right=right)
        return expression

    def unary(self) -> Expr:

        if self.__match(OperatorTokenType.BANG, SingleCharTokenType.MINUS):
            operator = self.__previous()
            right = self.unary()
            return Unary(operator=operator, right=right)

        return self.primary() 

    def primary(self) -> Expr:

        if self.__match(KeywordTokens.FALSE):
            return Literal(value=False)
        if self.__match(KeywordTokens.TRUE):
            return Literal(value=True)
        if self.__match(KeywordTokens.NIL):
            return Literal(value=None)

        if self.__match(LiteralTokenType.NUMBER, LiteralTokenType.STRING):
            return Literal(self.__previous().literal)

        if self.__match(LiteralTokenType.IDENTIFIER):
            return Variable(self.__previous())

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
