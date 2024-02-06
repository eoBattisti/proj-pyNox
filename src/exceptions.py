from enum import IntEnum
from typing import Any

__all__ = ("PyNoxException",
           "PyNoxSyntaxError")

class ErrorTypes(IntEnum):
    EX_OK = 0
    EX_USAGE = 64
    EX_DATAERR = 65
    EX_NOINPUT = 66
    EX_NOUSER = 67
    EX_NOHOST = 68
    EX_UNAVAILABLE = 69
    EX_SOFTWARE = 70
    EX_OSERR = 71
    EX_OSFILE = 72
    EX_CANTCREAT = 73
    EX_IOERR = 74
    EX_TEMPFAIL = 75
    EX_PROTOCOL = 76
    EX_NOPERM = 77
    EX_CONFIG = 78


class PyNoxException(Exception):
    """
    Base class for PyNox exceptions.
    """

    def __init__(self, message: str, error_type: ErrorTypes = ErrorTypes.EX_SOFTWARE):
        self.message = message
        self.error_type = error_type
        super().__init__(message)

    def __str__(self):
        return f"{self.error_type.name}: {self.message}"


class PyNoxRuntimeError(PyNoxException):

    def __init__(self, message: str, error_type: ErrorTypes = ErrorTypes.EX_USAGE):
        super().__init__(message, error_type)


class PyNoxSyntaxError(PyNoxException):

    def __init__(self, message: str, error_type: ErrorTypes = ErrorTypes.EX_USAGE):
        super().__init__(message, error_type)


class PyNoxParserError(PyNoxException):

    def __init__(self, message: str, error_type: ErrorTypes = ErrorTypes.EX_USAGE):
        super().__init__(message, error_type)


class PyNoxReturnError(PyNoxException):

    def __init__(self, message: str, value: Any, error_type: ErrorTypes = ErrorTypes.EX_SOFTWARE):
        self.value = value
        super().__init__(message, error_type)
