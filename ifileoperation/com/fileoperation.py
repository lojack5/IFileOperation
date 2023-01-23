__all__ = [
    'FileOperation',
]

import pythoncom
from win32com.shell import shell  # type: ignore (module *does* exist)

from .interfaces import IFileOperation


def FileOperation() -> IFileOperation:
    return pythoncom.CoCreateInstance(
        shell.CLSID_FileOperation, None, pythoncom.CLSCTX_ALL, shell.IID_IFileOperation
    )  # type: ignore
