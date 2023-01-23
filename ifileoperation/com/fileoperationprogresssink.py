"""
Python implementation/version of the IFileOperationProgressSink interface.
"""
from __future__ import annotations

__all__ = [
    'FileOperationProgressSink',
]

from functools import wraps, cached_property
from typing import Callable, ParamSpec

from comtypes import COMObject
from comtypes.hresult import S_OK, E_FAIL

from .common import com_ptr
from .interfaces import IFileOperationProgressSink
from ..flags  import TransferSourceFlags, FileAttributeFlags

P = ParamSpec('P')


def get_name(item) -> str:
    """Helper to get the filename from an IShellItem"""
    name = item.GetDisplayName(0x80058000) # SIGDN_FILESYSPATH
    if not name:
        name = item.GetDisplayName(0) # SIGDN_NORMALDISPLAY
    return name


def _err_to_hresult(method: Callable[P, None]) -> Callable[P, int]:
    @wraps(method)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> int:
        try:
            method(*args, **kwargs)
        except Exception:
            return E_FAIL
        return S_OK
    return wrapped


class _FileOperationProgressSink(COMObject):
    """Implementation of IFileOperationProgressSink, passes along calls to the
    Python implementation class FileOperationProgressSink.
    """
    _com_interfaces_ = [IFileOperationProgressSink]

    def __init__(self, impl: FileOperationProgressSink):
        self.impl = impl

    @_err_to_hresult
    def StartOperations(self):
        self.impl.start_operations()

    @_err_to_hresult
    def FinishOperations(self, hresult: int):
        self.impl.finish_operations(hresult)

    @_err_to_hresult
    def PreRenameItem(self, dwFlags, psiItem, pszNewName):
        self.impl.pre_rename_item(TransferSourceFlags(dwFlags), get_name(psiItem), pszNewName)

    @_err_to_hresult
    def PostRenameItem(self, dwFlags, psiItem, pszNewName, hrRename, psiNewlyCreated):
        self.impl.post_rename_item(TransferSourceFlags(dwFlags), get_name(psiItem), pszNewName, hrRename)

    @_err_to_hresult
    def PreMoveItem(self, dwFlags, psiItem, psiDestinationFolder, pszNewName):
        self.impl.pre_move_item(TransferSourceFlags(dwFlags), get_name(psiItem), get_name(psiDestinationFolder), pszNewName)

    @_err_to_hresult
    def PostMoveItem(self, dwFlags, psiItem, psiDestinationFolder, pszNewName, hrMove, psiNewlyCreated):
        self.impl.post_move_item(TransferSourceFlags(dwFlags), get_name(psiItem), get_name(psiDestinationFolder), pszNewName, hrMove)

    @_err_to_hresult
    def PreCopyItem(self, dwFlags, psiItem, psiDestinationFolder, pszNewName):
        self.impl.pre_copy_item(TransferSourceFlags(dwFlags), get_name(psiItem), get_name(psiDestinationFolder), pszNewName)

    @_err_to_hresult
    def PostCopyItem(self, dwFlags, psiItem, psiDestinationFolder, pszNewName, hrCopy, psiNewlyCreated):
        self.impl.post_copy_item(TransferSourceFlags(dwFlags), get_name(psiItem), get_name(psiDestinationFolder), pszNewName, hrCopy)

    @_err_to_hresult
    def PreDeleteItem(self, dwFlags, psiItem):
        self.impl.pre_delete_item(TransferSourceFlags(dwFlags), get_name(psiItem))

    @_err_to_hresult
    def PostDeleteItem(self, dwFlags, psiItem, hrDelete, psiNewlyCreated):
        recycled = False if not psiNewlyCreated else True
        self.impl.post_delete_item(TransferSourceFlags(dwFlags), get_name(psiItem), hrDelete, recycled)

    @_err_to_hresult
    def PreNewItem(self, dwFlags, psiDestinationFolder, pszNewName):
        self.impl.pre_new_item(TransferSourceFlags(dwFlags), get_name(psiDestinationFolder), pszNewName)

    @_err_to_hresult
    def PostNewItem(self, dwFlags, psiDestinationFolder, pszNewName, pszTemplateName, dwFileAttributes, hrNew, psiNewItem):
        self.impl.post_new_item(TransferSourceFlags(dwFlags), get_name(psiDestinationFolder), pszNewName, FileAttributeFlags(dwFileAttributes), hrNew)

    @_err_to_hresult
    def UpdateProgress(self, iWorkTotal, iWorkSoFar):
        self.impl.update_progress(iWorkTotal, iWorkSoFar)

    @_err_to_hresult
    def ResetTimer(self):
        self.impl.reset_timer()

    @_err_to_hresult
    def PauseTimer(self):
        self.impl.pause_timer()


class FileOperationProgressSink:
    """The base class for user-implemented IFileOperationProgressSink objects.
    For any method, if you wish to halt file operations, raise an error.
    """
    @cached_property
    def com_ptr(self):
        return com_ptr(_FileOperationProgressSink(self))

    def start_operations(self) -> None:
        pass

    def finish_operations(self, result: int) -> None:
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

    def post_new_item(self, transfer_flags: TransferSourceFlags, destination: str, new_name: str, file_attributes: FileAttributeFlags, hr_new: int) -> None:
        pass

    def update_progress(self, work_total: int, work_so_far: int) -> None:
        pass

    def reset_timer(self) -> None:
        pass

    def pause_timer(self) -> None:
        pass

    def resume_timer(self) -> None:
        pass
