
from typing import Dict, List
from .statements import Block, Stmt, StmtVisitor, Var
from .expression import Expr, ExprVisitor
from .interpreter import Interpreter
from ..lexer.tokens import Token


class Resolver(ExprVisitor, StmtVisitor):

    def __init__(self, interpreter: Interpreter) -> None:
        self.__interpreter = interpreter
        self.__scopes: List[Dict[str, bool]] = [] 

    def _begin_scope(self) -> None:
        self.__scopes.append({})

    def _declare(self, name: Token) -> None:
        if not self.__scopes:
            return None

        scope = self.__scopes[-1]
        scope[name.lexeme] = False

    def _define(self, name: Token) -> None:
        if not self.__scopes:
            return None

        self.__scopes[-1][name.lexeme] = True


    def _end_scope(self) -> None:
        self.__scopes.pop()

    def _resolve(self, statements: List[Stmt]) -> None:
        for stmt in statements:
            self._resolve_stmt(stmt)

    def _resolve_stmt(self, stmt: Stmt) -> None:
            stmt.accept(self)

    def _resolve_expr(self, expression: Expr) -> None:
        expression.accept(self)

    def visit_block_stmt(self, stmt: Block) -> None:
        self._begin_scope()
        self._resolve(stmt.statements)
        self._end_scope()

        return None

    def visit_var_stmt(self, stmt: Var) -> None:
        self._declare(stmt.name)
        if stmt.initializer is not None:
            self._resolve_expr(stmt.initializer)
        self._define(stmt.name)
        return None
