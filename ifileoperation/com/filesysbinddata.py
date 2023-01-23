__all__ = [
    'FOLDER_BIND_CTX',
    'parse_filename',
]
from os import fspath, PathLike
from typing import TypeAlias
from ctypes import byref
from ctypes.wintypes import WIN32_FIND_DATAW, DWORD

import pythoncom
import pywintypes
from win32com.shell import shell # type: ignore (module *does* exist)

from comtypes import COMObject
from comtypes.hresult import S_OK

from .interfaces import IFileSysBindData
from .common import com_ptr
from ..flags import FileAttributeFlags

StrPath: TypeAlias = str | PathLike[str]


class FileSysBindData(COMObject):
    """Implement the IFileSysBindData interface"""

    _com_interfaces_ = [IFileSysBindData]

    def SetFindData(self, pfd) -> int:
        self.find_data = pfd
        return S_OK

    def GetFindData(self, ppfd) -> int:
        ppfd.contents = self.find_data
        return S_OK


def create_bind_ctx(find_data: WIN32_FIND_DATAW):
    """Create an IBindCtx instance with a custom WIN32_FIND_DATA structure."""
    # NOTE: Need the type-hint because of COMObject's __new__ method return types
    bind_data: FileSysBindData = FileSysBindData()
    bind_data.SetFindData(byref(find_data))
    bind_ctx = pythoncom.CreateBindCtx()
    bind_ctx.RegisterObjectParam('File System Bind Data', com_ptr(bind_data))
    return bind_ctx


FOLDER_BIND_CTX = create_bind_ctx(WIN32_FIND_DATAW(DWORD(FileAttributeFlags.DIRECTORY)))


E_FILE_NOT_FOUND = -2147024894


def parse_filename(path: StrPath, force: bool = False):
    """Parse a filename into an IShellItem2 instance. If `force` is True, then
    an IShellItem2 instance will be returned even if the file does not exist.
    """
    path = fspath(path)
    try:
        return shell.SHCreateItemFromParsingName(
            path, None, shell.IID_IShellItem2  # type: ignore
        )
    except pywintypes.com_error as e:
        if e.hresult == E_FILE_NOT_FOUND and force:  # type: ignore
            return shell.SHCreateItemFromParsingName(
                path, FOLDER_BIND_CTX, shell.IID_IShellItem2
            )
        else:
            raise
