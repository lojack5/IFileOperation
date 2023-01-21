"""Exposes lower-level COM related methods."""
__all__ = [
    'FileAttributeFlags',
    'create_IFileOperation',
    'parse_filename',
    'WIN32_FIND_DATAW',
]

from ctypes import POINTER, PyDLL, byref, c_bool, c_void_p, py_object
from ctypes.wintypes import DWORD, PWIN32_FIND_DATAW, WIN32_FIND_DATAW
from functools import wraps
from os import PathLike, fspath
from typing import Callable, ParamSpec, TypeAlias, TypeVar, cast

# pywin32
import pythoncom
import pywintypes
import win32api

# comtypes
from comtypes import COMMETHOD, GUID, HRESULT, COMObject, IUnknown
from comtypes.hresult import S_OK
from win32com.shell import shell  # type: ignore (module *does* exist)

from .errors import FileOperatorError
from .flags import FileAttributeFlags
from .interfaces import IFileOperation

StrPath: TypeAlias = str | PathLike[str]
P_IUnknown = POINTER(IUnknown)  # type: ignore
P = ParamSpec('P')
T = TypeVar('T')


def create_IFileOperation() -> IFileOperation:
    """Create a IFileOperation instance."""
    ifo = pythoncom.CoCreateInstance(
        shell.CLSID_FileOperation, None, pythoncom.CLSCTX_ALL, shell.IID_IFileOperation
    )
    return cast(IFileOperation, ifo)


def parse_filename(path: StrPath, force: bool = False):
    """Parse a filename into an IShellItem2 instance. If `force` is True, then
    an IShellItem2 instance will be returned even if the file does not exist.
    """
    path = fspath(path)
    try:
        return shell.SHCreateItemFromParsingName(path, None, shell.IID_IShellItem2)  # type: ignore
    except pywintypes.com_error as e:
        if e.hresult == E_FILE_NOT_FOUND and force:  # type: ignore
            return shell.SHCreateItemFromParsingName(
                path, FOLDER_BIND_CTX, shell.IID_IShellItem2
            )
        else:
            raise


_PYCOM_PyObjectFromIUnknown = PyDLL(pythoncom.__file__).PyCom_PyObjectFromIUnknown
_PYCOM_PyObjectFromIUnknown.restype = py_object
_PYCOM_PyObjectFromIUnknown.argtypes = (P_IUnknown, c_void_p, c_bool)


def comtypes_to_pywin32(com_ptr, interface: type[IUnknown] = IUnknown):
    """Convert a comtypes pointer to a pythoncom PyI<interface> object."""
    # Cribbed from comtypes\test\test_win32com_interop.py
    # It uses pythoncom.dll to convert a COM pointer to a pythoncom pointer
    return _PYCOM_PyObjectFromIUnknown(com_ptr, byref(interface._iid_), True)


class IFileSysBindData(IUnknown):
    """Define the IFileSysBindData interface using comtypes, see
    https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nn-shobjidl_core-ifilesystembinddata
    """

    _iid_ = GUID('{01e18d10-4d8b-11d2-855d-006008059367}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'SetFindData', (['in'], PWIN32_FIND_DATAW, 'pfd')),
        COMMETHOD(
            [], HRESULT, 'GetFindData', (['out'], POINTER(PWIN32_FIND_DATAW), 'ppfd')
        ),
    ]


class FileSysBindData(COMObject):
    """Implement the IFileSysBindData interface"""

    _com_interfaces_ = [IFileSysBindData]

    def SetFindData(self, pfd) -> int:
        self.find_data = pfd
        return S_OK

    def GetFindData(self, ppfd) -> int:
        ppfd = self.find_data
        return S_OK


E_FILE_NOT_FOUND = -2147024894


def create_bind_ctx(find_data: WIN32_FIND_DATAW):
    """Create an IBindCtx instance with a custom WIN32_FIND_DATA structure."""
    bind_data = FileSysBindData()
    bind_data.SetFindData(byref(find_data))  # type: ignore
    bind_ctx = pythoncom.CreateBindCtx()
    bind_ctx.RegisterObjectParam(
        'File System Bind Data', comtypes_to_pywin32(bind_data)
    )
    return bind_ctx


def convert_exceptions(callable: Callable[P, T]) -> Callable[P, T]:
    @wraps(callable)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return callable(*args, **kwargs)
        except pythoncom.com_error as e:
            raise FileOperatorError(*e.args) from None

    return wrapped

FOLDER_BIND_CTX = create_bind_ctx(WIN32_FIND_DATAW(DWORD(FileAttributeFlags.DIRECTORY)))
