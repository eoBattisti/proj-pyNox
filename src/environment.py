from typing import Any, Dict, Optional
from .exceptions import PyNoxRuntimeError

from .lexer.tokens import Token


class Environment:

    def __init__(
        self,
        enclosing: Optional["Environment"] = None,
        values: Dict[str, Any] = {}
    ) -> None:
        self.enclosing: Optional[Environment] = enclosing
        self.values = values

    def define(self, name: Token, value: Any) -> None:
        self.values[name.lexeme] = value 

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values.keys():
            return self.values.get(name.lexeme)

        if self.enclosing is not None:
            return self.enclosing.get(name=name)

        raise PyNoxRuntimeError(f"{name} Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values.keys():
            self.values[name.lexeme] = value
            return None

        if self.enclosing is not None:
            self.enclosing.assign(name=name, value=value)
            return None

        raise PyNoxRuntimeError(f"{name} Undefined variable '{name.lexeme}'")
