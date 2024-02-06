from abc import ABC, abstractmethod
from typing import List, Any


from ..interpreter.statements import Function
from ..environment import Environment

#TODO: resolve circular import of `interpreter` in PyNoxCallable


class PyNoxCallable(ABC):

    @property
    @abstractmethod
    def arity(self):
        raise NotImplementedError

    @abstractmethod
    def __call__(self, interpreter, arguments: List[Any]) -> Any:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} at {hex(id(self))}>"


class PyNoxFunction(PyNoxCallable):

    def __init__(self, declaration: Function, closure: Environment, is_initializer: bool = False) -> None:
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

    @property
    def arity(self):
        return len(self.declaration.params)

    def __call__(self, interpreter, arguments: List[Any]) -> Any:
        env: Environment = Environment(enclosing=self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            env.define(name=param, value=arg)
        interpreter._execute_block(stmts=self.declaration.body, env=env)
        return None
