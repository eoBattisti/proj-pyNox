
from typing import Dict, List, Sequence, Union
from .statements import Block, Expression, Function, If, Print, Return, Stmt, StmtVisitor, Var, While
from .expression import Assign, Binary, Call, Expr, ExprVisitor, Grouping, Literal, Logical, Unary, Variable 
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

    def _resolve(self, statements: Sequence[Union[Stmt, Expr]]) -> None:
        for stmt in statements:
            self.__resolve(stmt)

    def __resolve(self, stmt: Union[Stmt, Expr]) -> None:
        stmt.accept(self)

    def _resolve_local_expr(self, expression: Expr, name: Token) - None:
        for i, scope in enumerate(reversed(self.__scopes)):
            if name.lexeme in scope:
                self.__interpreter._resolve(expression, i)
                return None

    def _resolve_function(self, function: Function) -> None:
        self._begin_scope()
        for param in function.params:
            self._declare(name=param)
            self._define(name=param)

        self._resolve(statements=function.body)
        self._end_scope()


    def visit_block_stmt(self, stmt: Block) -> None:
        self._begin_scope()
        self._resolve(statements=stmt.statements)
        self._end_scope()

    def visit_expr_stmt(self, stmt: Expression) -> None:
        self.__resolve(stmt.expression)

    def visit_function_stmt(self, stmt: Function):
        self._declare(name=stmt.name)
        self._define(name=stmt.name)
        self._resolve_function(function=stmt)

    def visit_if_stmt(self, stmt: If) -> None:
        self.__resolve(stmt.condition)
        self.__resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self.__resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        self.__resolve(stmt.expression)

    def visit_return_stmt(self, stmt: Return) -> None:
        if stmt.value is not None:
            self.__resolve(stmt.value)

    def visit_var_stmt(self, stmt: Var) -> None:
        self._declare(name=stmt.name)
        if stmt.initializer is not None:
            self.__resolve(stmt=stmt.initializer)
        self._define(name=stmt.name)

    def visit_while_stmt(self, stmt: While) -> None:
        self.__resolve(stmt.condition)
        self.__resolve(stmt.body)

    def visit_assign_expr(self, expression: Assign) -> None:
        self.__resolve(stmt=expression.value)
        self._resolve_local_expr(expression=expression, name=expression.name)

    def visit_binary(self, expression: Binary) -> None:
        self.__resolve(expression.left)
        self.__resolve(expression.right)

    def visit_call_expr(self, expression: Call) -> None:
        self.__resolve(expression.callee)

        for arg in expression.arguments:
            self.__resolve(arg)

    def visit_grouping(self, expression: Grouping) -> None:
        self.__resolve(expression)


    def visit_literal(self, expression: Literal) -> None:
        return None

    def visit_logical_expr(self, expression: Logical) -> None:
        self.__resolve(expression.left)
        self.__resolve(expression.right)

    def visit_unary(self, expression: Unary) -> None:
        self.__resolve(expression.right)


    def visit_variable_expr(self, expression: Variable) -> None:
        if self.__scopes and self.__scopes[-1].get(expression.name.lexeme) is False:
            self.__interpreter.error(token=expression.name, message="Can't read local variable in its own initializer.")
        self._resolve_local_expr(expression=expression, name=expression.name)

