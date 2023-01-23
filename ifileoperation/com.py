"""Exposes lower-level COM related methods."""
__all__ = [
    'create_IFileOperation',
    'parse_filename',
    'WIN32_FIND_DATAW',
]

from ctypes import POINTER, PyDLL, byref, c_bool, c_void_p, py_object
from ctypes.wintypes import DWORD, PWIN32_FIND_DATAW, WIN32_FIND_DATAW, LPCWSTR, UINT, LPWSTR
from functools import wraps
from os import PathLike, fspath
from typing import Callable, ParamSpec, TypeAlias, TypeVar, cast

# pywin32
import pythoncom
import pywintypes

# comtypes
from comtypes import COMMETHOD, GUID, HRESULT, COMObject, IUnknown
from comtypes.hresult import S_OK, E_FAIL
from win32com.shell import shell  # type: ignore (module *does* exist)

from .errors import FileOperatorError
from .flags import FileAttributeFlags, TransferSourceFlags
from .interfaces import IFileOperation

StrPath: TypeAlias = str | PathLike[str]
PIUnknown = POINTER(IUnknown)  # type: ignore
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


_PYCOM_PyObjectFromIUnknown = PyDLL(pythoncom.__file__).PyCom_PyObjectFromIUnknown
_PYCOM_PyObjectFromIUnknown.restype = py_object
_PYCOM_PyObjectFromIUnknown.argtypes = (PIUnknown, c_void_p, c_bool)


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
        ppfd.contents = self.find_data
        return S_OK


class IShellItem(IUnknown):
    """partially define the IShellItem interface using comtypes, only GetDisplayName
    is implemented, see
    https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nn-shobjidl_core-ishellitem
    """
    _iid_ = GUID('{43826d1e-e718-42ee-bc55-a1e261c37bfe}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'BindToHandler'),
        COMMETHOD([], HRESULT, 'GetParent'),
        COMMETHOD([], HRESULT, 'GetDisplayName', (['in'], DWORD, 'sigdnName'), (['annotation', 'string', 'out'], POINTER(LPWSTR), 'ppszName')),
        COMMETHOD([], HRESULT, 'GetAttributes'),
    ]
PIShellItem = POINTER(IShellItem)   # type: ignore


class IFileOperationProgressSink(IUnknown):
    """Define the IFileOperationSink interface using comtypes, see
    https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nn-shobjidl_core-ifileoperationprogresssink
    """
    _iid_ = GUID('{04b0f1a7-9490-44bc-96e1-4296a31252e2}')
    _methods_ = [
        # Most c_void_p's are actually IShellItem's
        COMMETHOD([], HRESULT, 'StartOperations'),
        COMMETHOD([], HRESULT, 'FinishOperations', (['in'], HRESULT, 'hrResult')),
        COMMETHOD([], HRESULT, 'PreRenameItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
            (['in'], LPCWSTR, 'pszNewName')),
        COMMETHOD([], HRESULT, 'PostRenameItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
            (['in'], LPCWSTR, 'pszNewName'),
            (['in'], HRESULT, 'hrRename'),
            (['in'], PIShellItem, 'psiNewlyCreated')),
        COMMETHOD([], HRESULT, 'PreMoveItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
            (['in'], PIShellItem, 'psiDestinationFolder'),
            (['in'], LPCWSTR, 'pszNewName')),
        COMMETHOD([], HRESULT, 'PostMoveItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
            (['in'], PIShellItem, 'psiDestinationFolder'),
            (['in'], LPCWSTR, 'pszNewName'),
            (['in'], HRESULT, 'hrMove'),
            (['in'], PIShellItem, 'psiNewlyCreated')),
        COMMETHOD([], HRESULT, 'PreCopyItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
            (['in'], PIShellItem, 'psiDestinationFolder'),
            (['in'], LPCWSTR, 'pszNewName')),
        COMMETHOD([], HRESULT, 'PostCopyItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
            (['in'], PIShellItem, 'psiDestinationFolder'),
            (['in'], LPCWSTR, 'pszNewName'),
            (['in'], HRESULT, 'hrCopy'),
            (['in'], PIShellItem, 'psiNewlyCreated')),
        COMMETHOD([], HRESULT, 'PreDeleteItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem')),
        COMMETHOD([], HRESULT, 'PostDeleteItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiItem'),
            (['in'], HRESULT, 'hrDelete'),
            (['in'], PIShellItem, 'psiNewlyCreated')),
        COMMETHOD([], HRESULT, 'PreNewItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiDestinationFolder'),
            (['in'], LPCWSTR, 'pszNewName')),
        COMMETHOD([], HRESULT, 'PostNewItem',
            (['in'], DWORD, 'dwFlags'),
            (['in'], PIShellItem, 'psiDestinationFolder'),
            (['in'], LPCWSTR, 'pszNewName'),
            (['in'], LPCWSTR, 'pszTemplateName'),
            (['in'], DWORD, 'dwFileAttributes'),
            (['in'], HRESULT, 'hrNew'),
            (['in'], PIShellItem, 'psiNewItem')),
        COMMETHOD([], HRESULT, 'UpdateProgress',
            (['in'], UINT, 'iWorkTotal'),
            (['in'], UINT, 'iWorkSoFar')),
        COMMETHOD([], HRESULT, 'ResetTimer'),
        COMMETHOD([], HRESULT, 'PauseTimer'),
        COMMETHOD([], HRESULT, 'ResumeTimer'),
    ]


class FileOperationProgressSink:
    """Python implementation of the IFileOperationProgresSink interface.

    This should be subclassed and applicable methods overridden. If an operation
    should fail, raise an exception from the applicable handling method.
    """
    def start_operations(self) -> None:
        pass

    def finish_operations(self, hrsult: int) -> None:
        pass

    def pre_rename_item(self, transfer_flags: TransferSourceFlags, source: str, new_name: str) -> None:
        pass

    def post_rename_item(self, transfer_flags: TransferSourceFlags, source: str, new_name: str, hr_rename: int) -> None:
        pass

    def pre_move_item(self, transfer_flags: TransferSourceFlags, source: str, destination: str, new_name: str) -> None:
        pass

    def post_move_item(self, transfer_flags: TransferSourceFlags, source: str, destination: str, new_name: str, hr_move: int) -> None:
        pass

    def pre_copy_item(self, transfer_flags: TransferSourceFlags, source: str, destination: str, new_name: str) -> None:
        pass

    def post_copy_item(self, transfer_flags: TransferSourceFlags, source: str, destination: str, new_name: str, hr_copy: int) -> None:
        pass

    def pre_delete_item(self, transfer_flags: TransferSourceFlags, source: str) -> None:
        pass

    def post_delete_item(self, transfer_flags: TransferSourceFlags, source: str, hr_delete: int, recycled: bool) -> None:
        pass

    def pre_new_item(self, transfer_flags: TransferSourceFlags, destination: str, new_name: str) -> None:
        pass

    def post_new_item(self, transfer_flags: TransferSourceFlags, destination: str, new_name: str, file_attributes: int, hr_new: int) -> None:
        pass

    def update_progress(self, work_total: int, work_so_far: int) -> None:
        pass

    def reset_timer(self) -> None:
        pass

    def pause_timer(self) -> None:
        pass

    def resume_timer(self) -> None:
        pass

    def to_pywin32(self):
        return _FileOperationProgressSink.to_pywin32(self)


class _FileOperationProgressSink(COMObject):
    """Implement the IFileOperationProgressSink interface, used to wrap the the
    Python implementation class FileOperationProgressSink.
    """
    _com_interfaces_ = [IFileOperationProgressSink]

    def __init__(self, python_impl: FileOperationProgressSink):
        self.impl = python_impl

    @staticmethod
    def get_name(item) -> str:
        """Helper to call IShellItem.GetDisplayName."""
        name = item.GetDisplayName(0x80058000) # SIGDN_FILESYSPATH
        if not name:
            name = item.GetDisplayName(0) # SIGDN_NORMALDISPLAY
        return name

    def StartOperations(self) -> int:
        try:
            self.impl.start_operations()
        except Exception:
            return E_FAIL
        return S_OK

    def FinishOperations(self, hresult: HRESULT) -> int:
        try:
            self.impl.finish_operations(int(hresult))
        except Exception:
            return E_FAIL
        return S_OK

    def PreRenameItem(self, dwFlags, psiItem, pszNewName) -> int:
        try:
            self.impl.pre_rename_item(TransferSourceFlags(dwFlags), self.get_name(psiItem), pszNewName)
        except Exception:
            return E_FAIL
        return S_OK

    def PostRenameItem(self, dwFlags, psiItem, pszNewName, hrRename, psiNewlyCreated) -> int:
        try:
            self.impl.post_rename_item(TransferSourceFlags(dwFlags), self.get_name(psiItem), pszNewName, hrRename)
        except Exception:
            return E_FAIL
        return S_OK

    def PreMoveItem(self, dwFlags, psiItem, psiDestinationFolder, pszNewName) -> int:
        try:
            self.impl.pre_move_item(TransferSourceFlags(dwFlags), self.get_name(psiItem), self.get_name(psiDestinationFolder), pszNewName)
        except Exception:
            return E_FAIL
        return S_OK

    def PostMoveItem(self, dwFlags, psiItem, psiDestinationFolder, pszNewName, hrMove, psiNewlyCreated) -> int:
        try:
            self.impl.post_move_item(TransferSourceFlags(dwFlags), self.get_name(psiItem), self.get_name(psiDestinationFolder), pszNewName, hrMove)
        except Exception:
            return E_FAIL
        return S_OK

    def PreCopyItem(self, dwFlags, psiItem, psiDestinationFolder, pszNewName) -> int:
        try:
            self.impl.pre_copy_item(TransferSourceFlags(dwFlags), self.get_name(psiItem), self.get_name(psiDestinationFolder), pszNewName)
        except Exception:
            return E_FAIL
        return S_OK

    def PostCopyItem(self, dwFlags, psiItem, psiDestinationFolder, pszNewName, hrCopy, psiNewlyCreated) -> int:
        try:
            self.impl.post_copy_item(TransferSourceFlags(dwFlags), self.get_name(psiItem), self.get_name(psiDestinationFolder), pszNewName, hrCopy)
        except Exception:
            return E_FAIL
        return S_OK

    def PreDeleteItem(self, dwFlags, psiItem) -> int:
        try:
            self.impl.pre_delete_item(TransferSourceFlags(dwFlags), self.get_name(psiItem))
        except Exception:
            return E_FAIL
        return S_OK

    def PostDeleteItem(self, dwFlags, psiItem, hrDelete, psiNewlyCreated) -> int:
        try:
            recycled = False if not psiNewlyCreated else True
            self.impl.post_delete_item(TransferSourceFlags(dwFlags), self.get_name(psiItem), hrDelete, recycled)
        except Exception:
            return E_FAIL
        return S_OK

    def PreNewItem(self, dwFlags, psiDestinationFolder, pszNewName) -> int:
        try:
            self.impl.pre_new_item(TransferSourceFlags(dwFlags), self.get_name(psiDestinationFolder), pszNewName)
        except Exception:
            return E_FAIL
        return S_OK

    def PostNewItem(self, dwFlags, psiDestinationFolder, pszNewName, pszTemplateName, dwFileAttributes, hrNew, psiNewItem) -> int:
        try:
            self.impl.post_new_item(TransferSourceFlags(dwFlags), self.get_name(psiDestinationFolder), pszNewName, dwFileAttributes, hrNew)
        except Exception:
            return E_FAIL
        return S_OK

    def UpdateProgress(self, iWorkTotal, iWorkSoFar) -> int:
        try:
            self.impl.update_progress(iWorkTotal, iWorkSoFar)
        except Exception:
            return E_FAIL
        return S_OK

    def ResetTimer(self) -> int:
        try:
            self.impl.reset_timer()
        except Exception:
            return E_FAIL
        return S_OK

    def PauseTimer(self) -> int:
        try:
            self.impl.pause_timer()
        except Exception:
            return E_FAIL
        return S_OK

    @classmethod
    def to_pywin32(cls, impl: FileOperationProgressSink):
        return comtypes_to_pywin32(cls(impl))

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
    """Wraps a method to automatically convert pythoncom.com_error exceptions
    into FileOperatorError exceptions.
    """
    # TODO: Implement mapping to builtin Python exceptions for common
    # HRESULTs, e.g. E_ACCESSDENIED, E_OUTOFMEMORY, etc.
    @wraps(callable)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return callable(*args, **kwargs)
        except pythoncom.com_error as e:
            raise FileOperatorError(*e.args) from None

    return wrapped


FOLDER_BIND_CTX = create_bind_ctx(WIN32_FIND_DATAW(DWORD(FileAttributeFlags.DIRECTORY)))
