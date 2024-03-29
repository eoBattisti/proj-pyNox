from typing import Any, Dict, List

from ..environment import Environment

from .expression import Assign, Binary, Call, Expr, ExprVisitor, Grouping, Literal, Logical, Unary, Variable
from .statements import Block, Expression, Function, If, Print, Return, Stmt, StmtVisitor, Var, While
from ..exceptions import PyNoxException, PyNoxReturnError, PyNoxRuntimeError
from ..logger import Logger
from ..lexer.tokens import KeywordTokens, OperatorTokenType, SingleCharTokenType, Token
from ..utils.callable import PyNoxCallable, PyNoxFunction


class Interpreter(ExprVisitor, StmtVisitor):

    def __init__(self, logger: Logger) -> None:
        self.__globals = Environment()
        self.__locals: Dict[Expr, int] = {}
        self.__env = self.__globals
        self.__logger = logger

    def interpret(self, statements: List[Stmt]):
        try:
            for stmt in statements:
                self.__execute(stmt)
        except PyNoxRuntimeError as error:
            self.__logger.error(str(error))

    def error(self, token: "Token", message: str) -> str:
        """Raise a runtime error."""
        error_ = f"{str(message)}"
        return f"RuntimeError at line {token.line}: {error_}"

    def look_up_variable(self, name: Token, expression: Expr) -> Any:
        distance = self.__locals.get(expression)
        if distance is not None:
            return self.__env.get_at(distance=distance, lexeme=name.lexeme)
        return self.__globals.get(name=name)

    def _resolve(self, expression: Expr, depth: int) -> None:
        self.__locals[expression] = depth

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

    def _execute_block(self, stmts: List[Stmt], env: Environment) -> None:
        previous: Environment = self.__env
        try:
            self.__env = env
            for stmt in stmts:
                self.__execute(stmt)
        finally:
            self.__env = previous
    def visit_block_stmt(self, stmt: Block) -> None:
        self._execute_block(stmt.statements, Environment(self.__env))
        return None

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

    def visit_function_stmt(self, stmt: Function) -> None:
        fn: PyNoxFunction = PyNoxFunction(declaration=stmt, closure=self.__env, is_initializer=False)
        self.__env.define(name=stmt.name, value=fn)


    def visit_if_stmt(self, stmt: If) -> None:
        if self.__is_truthy(self.__evaluate(stmt.condition)):
            self.__execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.__execute(stmt.else_branch)
        return None

    def visit_print_stmt(self, stmt: Print) -> None:
        value = self.__evaluate(stmt.expression)
        self.__logger.info(self.__stringfy(value))
        return None

    def visit_return_stmt(self, stmt: Return) -> None:
        value = None

        if stmt.value is not None:
            value = self.__evaluate(stmt.value)

        raise PyNoxReturnError(self.error(stmt.keyword, f"{stmt.keyword} Return {self.__stringfy(value)}"), value=value)

    def visit_var_stmt(self, stmt: Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = self.__evaluate(stmt.initializer)
        self.__env.define(name=stmt.name, value=value)
        return None

    def visit_while_stmt(self, stmt: While) -> None:
        while self.__is_truthy(self.__evaluate(stmt.condition)):
            self.__execute(stmt.body)
        return None

    def visit_variable_expr(self, expression: Variable) -> Any:
        return self.look_up_variable(expression.name, expression)

    def visit_assign_expr(self, expression: Assign) -> Any:
        value = self.__evaluate(expression.value)
        distance: int = self.__locals.get(expression)

        if distance is not None:
            self.__env.assign_at(distance=distance, name=expression.name, value=value)
        else:
            self.__globals.assign(name=expression.name, value=value)
        return value

    def visit_literal(self, expression: Literal) -> Any:
        return expression.value

    def visit_logical_expr(self, expression: Logical) -> Any:
        left = self.__evaluate(expression.left)

        if expression.operator.token_type == KeywordTokens.OR:
            if self.__is_truthy(left):
                return left
        else:
            if not self.__is_truthy(left):
                return left

        return self.__evaluate(expression.right)

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

    def visit_call_expr(self, expression: Call) -> Any:
        callee = self.__evaluate(expression.callee)
        arguments = [self.__evaluate(arg) for arg in expression.arguments]

        if not isinstance(callee, PyNoxCallable):
            raise PyNoxRuntimeError(f"{expression.paren}, Can only call function and classes")

        if len(arguments) != callee.arity:
            raise PyNoxRuntimeError(f"Expected {callee.arity} arguments but got {len(arguments)}")

        try:
            return callee(interpreter=self, arguments=arguments)
        except PyNoxException as e:
            print(e)
            self.__logger.error(f"Error calling function")
            raise PyNoxRuntimeError(f"{expression.paren}, Can only call function and classes")

