from typing import List, Optional

from ..exceptions import PyNoxParserError
from ..interpreter.expression import Assign, Binary, Call, Expr, Grouping, Literal, Logical, Unary, Variable
from ..lexer.tokens import EOFTokenType, KeywordTokens, LiteralTokenType, OperatorTokenType, SingleCharTokenType, Token, TokenType
from ..logger import Logger
from ..interpreter.statements import Block, Function, If, Print, Stmt, Expression, Var, While


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
            if self.__match(KeywordTokens.FUNCTION):
                return self.__function_declaration("function")
            if self.__match(KeywordTokens.VAR):
                return self.__var_declaration()
            return self.__statement()
        except PyNoxParserError:
            self.__synchronize()
            return None

    def __statement(self) -> Stmt: 
        if self.__match(KeywordTokens.FOR):
            return self.__for_stmt()
        if self.__match(KeywordTokens.IF):
            return self.__if_stmt()
        if self.__match(KeywordTokens.PRINT):
            return self.__print_stmt()
        if self.__match(KeywordTokens.WHILE):
            return self.__while_stmt()
        if self.__match(SingleCharTokenType.LEFT_BRACE):
            return Block(self.__block())

        return self.__expression_stmt()

    def __for_stmt(self) -> Stmt:
        self.__consume(SingleCharTokenType.LEFT_PAREN, "Expected '(' after 'for'. ")

        initializer: Optional[Stmt] = None
        if self.__match(SingleCharTokenType.SEMICOLON):
            initializer = None
        elif self.__match(KeywordTokens.VAR):
            initializer = self.__var_declaration()
        else:
            initializer = self.__expression_stmt()

        condition: Optional[Expr] = None
        if not self.__match(SingleCharTokenType.SEMICOLON):
            condition = self.expression()
        self.__consume(SingleCharTokenType.SEMICOLON, "Expected ';' after loop condition.")

        increment: Optional[Expr] = None
        if not self.__match(SingleCharTokenType.RIGHT_PAREN):
            increment = self.expression()

        self.__consume(SingleCharTokenType.RIGHT_PAREN, "Expected ')' after for clause.")

        body = self.__statement()

        if increment is not None:
            body = Block(stmts=[body, Expression(increment)])

        if condition is None:
            condition = Literal(True)

        body = While(condition=condition, body=body)

        if initializer is not None:
            body = Block(stmts=[initializer, body])

        return body



    def __if_stmt(self) -> Stmt:
        self.__consume(SingleCharTokenType.LEFT_PAREN, "Expected '(' after 'if'. ")
        condition: Expr = self.expression()
        self.__consume(SingleCharTokenType.RIGHT_PAREN, "Expected ')' after 'if'. ")

        then_branch: Stmt = self.__statement()
        else_branch: Optional[Stmt] = None

        if self.__match(KeywordTokens.ELSE):
            else_branch = self.__statement()

        return If(condition=condition, then_branch=then_branch, else_branch=else_branch)


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

    def __function_declaration(self, kind: str) :
        name: Token = self.__consume(LiteralTokenType.IDENTIFIER, f"Expect {kind} name")
        self.__consume(SingleCharTokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        parameters: List[Token] = []
        if (not self.__check(SingleCharTokenType.RIGHT_PAREN)):
            while True:
                if len(parameters) >= 255:
                    self.__error(self.__peek(), "Can't have more than 255 parameters")

                parameters.append(self.__consume(LiteralTokenType.IDENTIFIER, "Expect parameter name"))
                if not self.__match(SingleCharTokenType.COMMA):
                    break
        self.__consume(SingleCharTokenType.RIGHT_PAREN, "Expected ')' after 'while'.")
        self.__consume(SingleCharTokenType.LEFT_BRACE, "Expect '{' before " + f"{kind} body.")
        body: List[Stmt] = self.__block()
        return Function(name, parameters, body)


    def __while_stmt(self) -> Stmt:
        self.__consume(SingleCharTokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        condition = self.expression()
        self.__consume(SingleCharTokenType.RIGHT_PAREN, "Expected ')' after 'while'.")

        body = self.__statement()

        return While(condition=condition, body=body)


    def __expression_stmt(self) -> Stmt:
        expression = self.expression()
        self.__consume(SingleCharTokenType.SEMICOLON, "Expected ';' after value.")
        return Expression(expression)
    
    def __block(self) -> List[Stmt]:
        statements = []

        while not self.__check(SingleCharTokenType.RIGHT_BRACE) and not self.__is_at_end():
            statements.append(self.__declaration())

        self.__consume(SingleCharTokenType.RIGHT_BRACE, "Expected '}' after block.")
        return statements

    def __assignment(self) -> Expr:
        expression = self.__or()

        if self.__match(OperatorTokenType.EQUAL):
            equals: Token = self.__previous()
            value = self.__assignment()
            if isinstance(expression, Variable):
                name = expression.name
                return Assign(name=name, value=value)
            self.__error(token=equals, message="Invalid assignmnet target.")

        return expression

    def __or(self) -> Expr:
        expr = self.__and()

        while self.__match(KeywordTokens.OR):
            operator = self.__previous()
            right = self.__and()
            expr = Logical(operator=operator, right=right, left=expr)

        return expr

    def __and(self) -> Expr:
        expr = self.equality()

        while self.__match(KeywordTokens.AND):
            operator = self.__previous()
            right = self.equality()
            expr = Logical(operator=operator, right=right, left=expr)

        return expr

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

        return self.call() 

    def __finish_call(self, callee: Expr):
        arguments = []
        
        if not self.__check(SingleCharTokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.__error(self.__peek(), "Can't have more than 255 arguments ")
                arguments.append(self.expression())
                if not self.__match(SingleCharTokenType.COMMA):
                    break

        paren = self.__consume(SingleCharTokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return Call(callee=callee, paren=paren, arguments=arguments)

    def call(self) -> Expr:

        expr = self.primary()

        while True:
            if self.__match(SingleCharTokenType.LEFT_PAREN):
                expr = self.__finish_call(callee=expr)
            else:
                break

        return expr

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
