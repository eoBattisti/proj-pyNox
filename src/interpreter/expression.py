from typing import Any, Protocol

from ..lexer.tokens import Token

class ExprVisitor(Protocol):

    def visit_binary(self, expression) -> Any:
        pass

    def visit_unary(self, expression) -> Any:
        pass

    def visit_grouping(self, expression) -> Any:
        pass

    def visit_literal(self, expression) -> Any:
        pass

    def visit_variable_expr(self, expression) -> Any:
        pass

    def visit_assign_expr(self, expression) -> Any:
        pass

    def visit_logical_expr(self, expression) -> Any:
        pass


class Expr(Protocol):

    def accept(self, visitor: ExprVisitor) -> Any:
        pass


class Binary(Expr):

    def __init__(self, left: Expr, operator: Token, right : Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_binary(expression=self)

class Unary(Expr):

    def __init__(self, operator: Token, right: Expr) -> None:
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_unary(expression=self)

class Grouping(Expr):

    def __init__(self, expression: Expr) -> None:
        self.expression = expression

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_grouping(expression=self)

class Literal(Expr):

    def __init__(self, value: object) -> None:
        self.value = value

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_literal(expression=self)

class Variable(Expr):

    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_variable_expr(self)

class Logical(Expr):

    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_logical_expr(self)

class Assign(Expr):

    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_assign_expr(self)
