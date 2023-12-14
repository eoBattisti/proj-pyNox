from typing import Any, Protocol

from ..lexer.tokens import Token

class ExpressionVisitor(Protocol):

    def visit_binary(self, expression) -> Any:
        pass

    def visit_unary(self, expression) -> Any:
        pass

    def visit_grouping(self, expression) -> Any:
        pass

    def visit_literal(self, expression) -> Any:
        pass


class Expression(Protocol):

    def accept(self, visitor: ExpressionVisitor) -> Any:
        pass


class Binary(Expression):

    def __init__(self, left: Expression, operator: Token, right : Expression) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExpressionVisitor) -> Any:
        return visitor.visit_binary(expression=self)

class Unary(Expression):

    def __init__(self, operator: Token, right: Expression) -> None:
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExpressionVisitor) -> Any:
        return visitor.visit_unary(expression=self)

class Grouping(Expression):

    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def accept(self, visitor: ExpressionVisitor) -> Any:
        return visitor.visit_grouping(expression=self)

class Literal(Expression):

    def __init__(self, value: object) -> None:
        self.value = value

    def accept(self, visitor: ExpressionVisitor) -> Any:
        return visitor.visit_literal(expression=self)
