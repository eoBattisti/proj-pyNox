from typing import Any, List, Optional, Protocol

from .expression import Expr
from ..lexer.tokens import Token

class StmtVisitor(Protocol):

    def visit_expr_stmt(self, stmt):
        pass

    def visit_print_stmt(self, stmt):
        pass

    def visit_var_stmt(self, stmt):
        pass

    def visit_block_stmt(self, stmt):
        pass

    def visit_if_stmt(self, stmt):
        pass

    def visit_while_stmt(self, stmt):
        pass

    def visit_function_stmt(self, stmt):
        pass

    def visit_return_stmt(self, stmt):
        pass


class Stmt(Protocol):

    def accept(self, visitor: StmtVisitor):
        pass

class Block(Stmt):

    def __init__(self, stmts: List[Stmt]) -> None:
        self.statements = stmts

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_block_stmt(self)

class If(Stmt):

    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Optional[Stmt] = None) -> None:
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_if_stmt(self)


class Expression(Stmt):

    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_expr_stmt(self)


class Function(Stmt):

    def __init__(self, name: Token, params: List[Token], body: List[Stmt]) -> None:
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_function_stmt(self)

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

class While(Stmt):

    def __init__(self, condition: Expr, body: Stmt) -> None:
        self.condition = condition
        self.body = body

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_while_stmt(self)


class Return(Stmt):

    def __init__(self, keyword: Token, value: Expr) -> None:
        self.keyword = keyword
        self.value = value

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_return_stmt(self)
