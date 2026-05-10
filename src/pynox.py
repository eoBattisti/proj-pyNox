import sys
from posix import EX_USAGE
from pathlib import Path


class PyNox:

    def __init__(
        self,
        filename: str | None = None,
        dry_run: bool = False,
        stop_at: str = '',

    ) -> None:
        self.filename: Path | None = Path(filename) if filename is not None else None 
        self.dry_run: bool = dry_run
        self.stop_at: str = stop_at
        self.had_error: bool = False

    def run_file(self):
        if self.filename:
            with open(self.filename, 'r') as file:
                source_code = file.read()
                self.__run(bytes=source_code)

                if self.had_error:
                    sys.exit(EX_USAGE)

    def run_prompt(self):

        while True:
            line = input("> ")
            if not line:
                break

            self.__run(bytes=line)
            self.had_error = False

    def __run(self, bytes: str):
        scanner = Scanner(source=bytes)
        tokens: list[Token] = scanner.scan_tokens()

        for t in tokens:
            print(t)

    def error(self, line: int, where: str, message: str):
        self.__report(line=line, where=where, message=message)
        pass

    def __report(self, line: int, where: str, message: str):
        print(f"[line: {line}] Error {where}: {message}", file=sys.stderr)
        self.had_error = True
