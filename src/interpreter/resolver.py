
from typing import Dict, List
from .statements import Block, Stmt, StmtVisitor
from .expression import Expr, ExprVisitor
from .interpreter import Interpreter


class Resolver(ExprVisitor, StmtVisitor):

    def __init__(self, interpreter: Interpreter) -> None:
        self.__interpreter = interpreter
        self.__scopes: List[Dict[str, bool]] = [] 

    def _begin_scope(self):
        self.__scopes.append({})

    def _end_scope(self):
        self.__scopes.pop()

    def _resolve(self, statements: List[Stmt]):
        for stmt in statements:
            self._resolve_stmt(stmt)

    def _resolve_stmt(self, stmt: Stmt):
            stmt.accept(self)

    def _resolve_expr(self, expression: Expr):
        expression.accept(self)

    def visit_block_stmt(self, stmt: Block) -> None:
        self._begin_scope()
        self._resolve(stmt.statements)
        self._end_scope()

        return None
