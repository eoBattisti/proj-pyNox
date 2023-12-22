from typing import Any, List

from ..environment import Environment

from .expression import Assign, Binary, Expr, ExprVisitor, Grouping, Literal, Unary, Variable
from .statements import Expression, Print, Stmt, StmtVisitor, Var
from ..exceptions import PyNoxRuntimeError
from ..logger import Logger
from ..lexer.tokens import KeywordTokens, OperatorTokenType, SingleCharTokenType, Token


class Interpreter(ExprVisitor, StmtVisitor):

    def __init__(self, logger: Logger) -> None:
        self.__env = Environment()
        self.__logger = logger

    def interpret(self, statements: List[Stmt]):
        try:
            for stmt in statements:
                self.__execute(stmt)
        except PyNoxRuntimeError as error:
            self.__logger.error(str(error))

    def __stringfy(self, obj: Any) -> str:
        if not obj:
            return str(KeywordTokens.NIL)
        if isinstance(obj, bool):
            return str(obj).lower()
        return str(obj)

    def __evaluate(self, expression: Expr):
        return expression.accept(self)

    def __execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def __is_truthy(self, obj: Any):
        return bool(obj)

    def __is_equal(self, left: Any, right: Any):
        if type(left) != type(right):
            return False
        return left == right

    def __check_number_operand(self, operator: Token, *operands: Any) -> None:
        for operand in operands:
            if not isinstance(operand, (int, float)):
                raise PyNoxRuntimeError(message=f"{operator} must be a number.")
        return None

    def visit_expr_stmt(self, stmt: Expression) -> None:
        self.__evaluate(stmt.expression)
        return None

    def visit_print_stmt(self, stmt: Print) -> None:
        value = self.__evaluate(stmt.expression)
        self.__logger.info(self.__stringfy(value))
        return None

    def visit_var_stmt(self, stmt: Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = self.__evaluate(stmt.initializer)
        self.__env.define(name=stmt.name, value=value)
        return None

    def visit_variable_expr(self, expression: Variable) -> Any:
        return self.__env.get(expression.name)

    def visit_assign_expr(self, expression: Assign) -> Any:
        value = self.__evaluate(expression.value)
        self.__env.assign(expression.name, value)
        return value

    def visit_literal(self, expression: Literal) -> Any:
        return expression.value

    def visit_grouping(self, expression: Grouping) -> Any:
        return self.__evaluate(expression.expression)

    def visit_unary(self, expression: Unary) -> Any:
        right = self.__evaluate(expression.right)

        match expression.operator.token_type:
            case OperatorTokenType.BANG:
                return not self.__is_truthy(right)
            case SingleCharTokenType.MINUS:
                self.__check_number_operand(expression.operator, right)
                return -right
        return None

    def visit_binary(self, expression: Binary) -> Any:
        left = self.__evaluate(expression.left)
        right = self.__evaluate(expression.right)

        match expression.operator.token_type:
            case OperatorTokenType.GREATER:
                self.__check_number_operand(expression.operator, right, left)
                return left > right
            case OperatorTokenType.GREATER_EQUAL:
                self.__check_number_operand(expression.operator, right, left)
                return left >= right
            case OperatorTokenType.LESS:
                self.__check_number_operand(expression.operator, right, left)
                return left < right
            case OperatorTokenType.LESS_EQUAL:
                self.__check_number_operand(expression.operator, right, left)
                return left <= right
            case OperatorTokenType.BANG_EQUAL:
                return not self.__is_equal(left, right)
            case OperatorTokenType.EQUAL_EQUAL:
                return self.__is_equal(left, right)
            case SingleCharTokenType.MINUS:
                self.__check_number_operand(expression.operator, right, left)
                return left - right
            case SingleCharTokenType.PLUS:
                if type(left) in (int, float) and type(right) in (int, float):
                    return left + right

                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)

                raise RuntimeError(f"{expression.operator}. Operands must be two numbers or two strings.")
            case SingleCharTokenType.SLASH:
                self.__check_number_operand(expression.operator, right, left)
                return left / right
            case SingleCharTokenType.STAR:
                return left * right

        return None

