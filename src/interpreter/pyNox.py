import pathlib

from .interpreter import Interpreter
from ..parser import Parser
from ..lexer import Lexer
from ..logger import Logger

__all__ = ["PyNox",]


class PyNox:

    def __init__(self, source: str | pathlib.Path = "") -> None:
        self._file_path = pathlib.Path(source) if source else None
        self._had_error: bool = False
        self._source = self.__read_file(path=self._file_path) if self._file_path else ""
        self.logger = Logger(name="PyNox")
        self._interpreter = Interpreter(logger=self.logger)
        self.lexer = Lexer(source=self._source)

    def __read_file(self, path: pathlib.Path) -> str:
        with open(path, "r") as f:
            return f.read().strip()

    def run_file(self):
        if self._had_error:
            exit(65)

        tokens = self.lexer.scan_tokens()
        parser = Parser(tokens=tokens, logger=self.logger)
        expression = parser.parse()
        self._interpreter.interpret(expression=expression)
        if self._had_error:
            return

        self._had_error = False

    def run_prompt(self):
        while True:
            try:
                line = input("pyNox> ")
                if not line:
                    raise EOFError
                self.run(line)
                self._had_error = False
            except EOFError:
                print("bye!")
                exit(65)

    def run(self, source):
        for char in source:
            print(char)

if __name__ == '__main__':
    p = PyNox(source="../../test_file.txt")
    p.run_file()
