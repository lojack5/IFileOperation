__all__ = [
    'FOLDER_BIND_CTX',
    'filename_to_IShellItem',
    'filenames_to_IShellItemArray',
]
import os
from collections.abc import Iterable
from ctypes import byref
from ctypes.wintypes import DWORD, WIN32_FIND_DATAW
from typing import TypeAlias

import pythoncom
import pywintypes
from comtypes import COMObject
from comtypes.hresult import S_OK
from win32com.shell import shell  # type: ignore (module *does* exist)

from ..flags import FileAttributeFlags
from .common import com_ptr
from .interfaces import IFileSysBindData

StrPath: TypeAlias = str | os.PathLike[str]


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


E_FILE_NOT_FOUND = (-2147024894, -2147024893)


def filename_to_IShellItem(path: StrPath, force: bool = False):
    """Parse a filename into an IShellItem instance. If `force` is True, then an
    IShellItem instance will be returned even if the file does not exist.
    """
    path = os.path.abspath(os.fspath(path))
    ctx = FOLDER_BIND_CTX if force else None
    try:
        return shell.SHCreateItemFromParsingName(
            path, ctx, shell.IID_IShellItem  # type: ignore
        )
    except pywintypes.com_error as e:
        if e.hresult in E_FILE_NOT_FOUND:  # type: ignore
            raise FileNotFoundError(path) from None
        raise


def filenames_to_IShellItemArray(paths: Iterable[StrPath]):
    """Parse an iterable (list, etc) of filenames into an IShellItemArray, for use with
    the plural forms of IFileOperation methods. If not filenames are passed, None is
    returned (and indicates the operation would fail).
    """
    idls = []
    for path in paths:
        path = os.path.abspath(os.fspath(path))
        try:
            idl = shell.SHParseDisplayName(path, 0, None)[0]
        except pywintypes.com_error as e:
            if e.hresult in E_FILE_NOT_FOUND:  # type: ignore
                raise FileNotFoundError(path) from None
            raise
        idls.append(idl)
    return None if not idls else shell.SHCreateShellItemArrayFromIDLists(idls)
