import argparse

from src.pynox import PyNox


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog='pyNox Interpreter'
    )

    _ = parser.add_argument(
        '-f',
        '--filename',
        nargs=1,
        required=False,
        help='The lox file to be interpreted',

    )

    _ = parser.add_argument(
        '-n',
        '--dry-run',
        default=False,
        help='Do not execute the Lox code, only shows what would be executed',
    )

    _ = parser.add_argument(
        '-s',
        '--stop',
        required=False,
        nargs=1,
        choices=['s', 't', 'p', 'tree'],
        default='',
        help='''What step to stop the application and print results.
        s = Scanning;
        t = Tokens;
        p = Parsing;
        tree = Syntax Tree;
        '''
    )

    args = parser.parse_args()

    pynox = PyNox(
        filename=args.filename,
        dry_run=args.dry_run,
        stop_at=args.stop,
    )

    if args.filename:
        pynox.run_file()
    else:
        pynox.run_prompt()
