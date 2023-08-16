from abc import ABC, abstractmethod
from typing import Any

from lexer.tokens import Token

class ExpressionVisitor(ABC):
    
    @abstractmethod
    def visit_binary(self, expression) -> Any:
        pass

    @abstractmethod
    def visit_unary(self, expression) -> Any:
        pass

    @abstractmethod
    def visit_grouping(self, expression) -> Any:
        pass

    @abstractmethod
    def visit_literal(self, expression) -> Any:
        pass


class Expression(ABC):
    
    @abstractmethod
    def accept(self, visitor: ExpressionVisitor) -> Any:
        pass


class Binary(Expression):

    def __init__(self, left: Expression, operator: Token, righ : Expression) -> None:
        self.left = left
        self.operator = operator
        self.right = righ   

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
