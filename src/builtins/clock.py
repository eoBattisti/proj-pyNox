import time
from typing import List, Any

from . import BuiltInCallable
from ..interpreter import Interpreter

class Clock(BuiltInCallable):

    def __init__(self, name: str = "clock") -> None:
        super().__init__(name)

    def __call__(self, interpreter: "Interpreter", arguments: List[Any]) -> float:
        return time.time()

    def arity(self):
        return 0
