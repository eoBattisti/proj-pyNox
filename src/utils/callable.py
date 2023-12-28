from abc import ABC, abstractmethod
from typing import List, Any

from ..interpreter import Interpreter


class PyNoxCallable(ABC):

    @property
    @abstractmethod
    def arity(self):
        raise NotImplementedError

    @abstractmethod
    def __call__(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} at {hex(id(self))}>"


class PyNoxFunction(PyNoxCallable):

    def __call__(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        pass
