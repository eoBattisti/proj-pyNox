
from typing import Dict, List, Sequence, Union
from .statements import Block, Stmt, StmtVisitor, Var
from .expression import Assign, Expr, ExprVisitor, Variable 
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

    def visit_block_stmt(self, stmt: Block) -> None:
        self._begin_scope()
        self._resolve(stmt.statements)
        self._end_scope()

        return None

    def visit_var_stmt(self, stmt: Var) -> None:
        self._declare(stmt.name)
        if stmt.initializer is not None:
            self.__resolve(stmt.initializer)
        self._define(stmt.name)
        return None

    def visit_variable_expr(self, expression: Variable) -> None:
        if self.__scopes and self.__scopes[-1].get(expression.name.lexeme) is False:
            self.__interpreter.error(token=expression.name, message="Can't read local variable in its own initializer.")
        self._resolve_local_expr(expression, expression.name)
        return None

    def visit_assign_expr(self, expression: Assign) -> None:
        self.__resolve(expression.value)
        self._resolve_local_expr(expression, expression.name)
        return None
