from typing import Any, List

from ..interpreter import Interpreter
from utils.callable import PyNoxCallable


class BuiltInCallable(PyNoxCallable):

    def __init__(self, name: str = "built-in") -> None:
        self.name = name

    def __str__(self) -> str:
        return f"<Built-in function '{self.name}'>"

    def __call__(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        raise NotImplementedError

    @property
    def arity(self):
        raise NotImplementedError
