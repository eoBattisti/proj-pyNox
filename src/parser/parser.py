from typing import List

from lexer.tokens import Token


class Parser:

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0

