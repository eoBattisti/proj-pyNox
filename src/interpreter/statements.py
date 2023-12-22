from typing import Any, Optional, Protocol

from .expression import Expr
from ..lexer.tokens import Token

class StmtVisitor(Protocol):

    def visit_expr_stmt(self, stmt):
        pass

    def visit_print_stmt(self, stmt):
        pass

    def visit_var_stmt(self, stmt):
        pass


class Stmt(Protocol):

    def accept(self, visitor: StmtVisitor):
        pass

class Expression(Stmt):

    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_expr_stmt(self)

class Print(Stmt):

    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_print_stmt(self)

class Var(Stmt):

    def __init__(self, name: Token, initializer: Optional[Expr]) -> None:
        self.initializer = initializer
        self.name = name

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_var_stmt(self)
