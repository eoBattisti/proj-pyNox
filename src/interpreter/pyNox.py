import sys


class PyNox:

    def __init__(self, args):
        self._had_error: bool = False
        if len(args) > 1:
            print(f"Too many arguments: {args}")
            exit(64)
        elif len(args) == 1:
            self.run_file(args[0]) 
        else:
            self.run_prompt()
    
    def run_file(self, file):
        try:
            if self._had_error:
                exit(65)
            with open(file, "r") as f:
                self.run(f.read())
                self._had_error = False
        except FileNotFoundError:
            print(f"File not found: {file}")

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

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        print(f"Error: {where} on line {line}: {message}")
        self._had_error = True

if __name__ == '__main__':
    PyNox(sys.argv[1:])
