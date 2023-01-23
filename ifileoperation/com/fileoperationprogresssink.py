"""
Python implementation/version of the IFileOperationProgressSink interface.
"""
from __future__ import annotations

__all__ = [
    'FileOperationProgressSink',
]

from functools import cached_property, wraps
from typing import Callable, ParamSpec, overload

from comtypes import COMObject
from comtypes.hresult import E_FAIL, S_OK

from ..flags import FileAttributeFlags, TransferSourceFlags
from .common import com_ptr
from .interfaces import IFileOperationProgressSink, IShellItem

P = ParamSpec('P')


@overload
def get_name(item: None) -> None:
    ...


@overload
def get_name(item: IShellItem) -> str:
    ...


def get_name(item: IShellItem | None) -> str | None:
    """Helper to get the filename from an IShellItem"""
    if not item:
        return None
    name = item.GetDisplayName(0x80058000)  # SIGDN_FILESYSPATH
    if not name:
        name = item.GetDisplayName(0)  # SIGDN_NORMALDISPLAY
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
    def PreRenameItem(self, dwFlags: int, psiItem: IShellItem, pszNewName: str):
        self.impl.pre_rename_item(
            TransferSourceFlags(dwFlags), get_name(psiItem), pszNewName
        )

    @_err_to_hresult
    def PostRenameItem(
        self,
        dwFlags: int,
        psiItem: IShellItem,
        pszNewName: str,
        hrRename: int,
        psiNewlyCreated: IShellItem | None,
    ):
        self.impl.post_rename_item(
            TransferSourceFlags(dwFlags),
            get_name(psiItem),
            get_name(psiNewlyCreated),
            hrRename,
        )

    @_err_to_hresult
    def PreMoveItem(
        self,
        dwFlags: int,
        psiItem: IShellItem,
        psiDestinationFolder: IShellItem,
        pszNewName: str,
    ):
        self.impl.pre_move_item(
            TransferSourceFlags(dwFlags),
            get_name(psiItem),
            get_name(psiDestinationFolder),
            pszNewName,
        )

    @_err_to_hresult
    def PostMoveItem(
        self,
        dwFlags: int,
        psiItem: IShellItem,
        psiDestinationFolder: IShellItem,
        pszNewName: str,
        hrMove: int,
        psiNewlyCreated: IShellItem | None,
    ):
        self.impl.post_move_item(
            TransferSourceFlags(dwFlags),
            get_name(psiItem),
            get_name(psiDestinationFolder),
            get_name(psiNewlyCreated),
            hrMove,
        )

    @_err_to_hresult
    def PreCopyItem(
        self,
        dwFlags: int,
        psiItem: IShellItem,
        psiDestinationFolder: IShellItem,
        pszNewName: str,
    ):
        self.impl.pre_copy_item(
            TransferSourceFlags(dwFlags),
            get_name(psiItem),
            get_name(psiDestinationFolder),
            pszNewName,
        )

    @_err_to_hresult
    def PostCopyItem(
        self,
        dwFlags: int,
        psiItem: IShellItem,
        psiDestinationFolder: IShellItem,
        pszNewName: str,
        hrCopy: int,
        psiNewlyCreated: IShellItem | None,
    ):
        self.impl.post_copy_item(
            TransferSourceFlags(dwFlags),
            get_name(psiItem),
            get_name(psiDestinationFolder),
            get_name(psiNewlyCreated),
            hrCopy,
        )

    @_err_to_hresult
    def PreDeleteItem(self, dwFlags: int, psiItem: IShellItem):
        self.impl.pre_delete_item(TransferSourceFlags(dwFlags), get_name(psiItem))

    @_err_to_hresult
    def PostDeleteItem(
        self,
        dwFlags: int,
        psiItem: IShellItem,
        hrDelete: int,
        psiNewlyCreated: IShellItem | None,
    ):
        recycled = False if not psiNewlyCreated else True
        self.impl.post_delete_item(
            TransferSourceFlags(dwFlags), get_name(psiItem), hrDelete, recycled
        )

    @_err_to_hresult
    def PreNewItem(
        self, dwFlags: int, psiDestinationFolder: IShellItem, pszNewName: str
    ):
        self.impl.pre_new_item(
            TransferSourceFlags(dwFlags), get_name(psiDestinationFolder), pszNewName
        )

    @_err_to_hresult
    def PostNewItem(
        self,
        dwFlags: int,
        psiDestinationFolder: IShellItem,
        pszNewName: str,
        pszTemplateName: str,
        dwFileAttributes: int,
        hrNew: int,
        psiNewItem: IShellItem | None,
    ):
        self.impl.post_new_item(
            TransferSourceFlags(dwFlags),
            get_name(psiDestinationFolder),
            get_name(psiNewItem),
            FileAttributeFlags(dwFileAttributes),
            hrNew,
        )

    @_err_to_hresult
    def UpdateProgress(self, iWorkTotal: int, iWorkSoFar: int):
        self.impl.update_progress(iWorkTotal, iWorkSoFar)

    @_err_to_hresult
    def ResetTimer(self):
        self.impl.reset_timer()

    @_err_to_hresult
    def PauseTimer(self):
        self.impl.pause_timer()


class FileOperationProgressSink:
    """The base class for user-implemented IFileOperationProgressSink objects.

    Subclass and implement any methods for which you wish to perform additional tasks.
    In each method, to indicate an error, raise an exception (rather than returning a
    WIN32 error code).  For the post_* methods, the `new_name` paramter will be `None`
    if the operation failed, or the full path of the new object on a success.

    Note that the pre_* and post_* methods may be called multiple times per file,
    depending on the flags specified in the IFileOperation object. For example, if
    confirmation dialogs are enabled (default), and a name collision occurs, the post_*
    method for the operation can be called multiple times with a PENDING status. Once
    the user has selected a final action, you will know if it succeeded or not by
    checking `new_name` for None.

    The `result` parameter is a WIN32 HRESULT value indicating the result of the
    operation. Currently, you should only need to check this for post_delete_item, as
    there is no good way to check for success otherwise.
    """

    @cached_property
    def com_ptr(self):
        """Return a pywin32 compatible COM pointer for passing to other pywin32
        COM objects.
        """
        return com_ptr(_FileOperationProgressSink(self))

    def start_operations(self) -> None:
        """Called when the file operations are about to begin."""

    def finish_operations(self, result: int) -> None:
        """Called when all file operations are completed. `result` is a WIN32 HRESULT
        with the final result of the operation.
        """

    def pre_rename_item(
        self, transfer_flags: TransferSourceFlags, source: str, new_name: str
    ) -> None:
        """Called just prior to renaming an item."""

    def post_rename_item(
        self,
        transfer_flags: TransferSourceFlags,
        source: str,
        new_name: str | None,
        result: int,
    ) -> None:
        """Called after an item has been renamed."""

    def pre_move_item(
        self,
        transfer_flags: TransferSourceFlags,
        source: str,
        destination: str,
        new_name: str,
    ) -> None:
        """Called just prior to moving an item."""

    def post_move_item(
        self,
        transfer_flags: TransferSourceFlags,
        source: str,
        destination: str,
        new_name: str | None,
        result: int,
    ) -> None:
        """Called after an item has been moved."""

    def pre_copy_item(
        self,
        transfer_flags: TransferSourceFlags,
        source: str,
        destination: str,
        new_name: str,
    ) -> None:
        """Called just prior to copying an item."""

    def post_copy_item(
        self,
        transfer_flags: TransferSourceFlags,
        source: str,
        destination: str,
        new_name: str | None,
        result: int,
    ) -> None:
        """Called after an item has been copied."""

    def pre_delete_item(self, transfer_flags: TransferSourceFlags, source: str) -> None:
        """Called just prior to deleting an item."""

    def post_delete_item(
        self,
        transfer_flags: TransferSourceFlags,
        source: str,
        result: int,
        recycled: bool,
    ) -> None:
        """Called after an item has been deleted. `recycled` is True if the item was
        sent to the recycle bin.
        """

    def pre_new_item(
        self, transfer_flags: TransferSourceFlags, destination: str, new_name: str
    ) -> None:
        """Called just prior to creating a new item."""

    def post_new_item(
        self,
        transfer_flags: TransferSourceFlags,
        destination: str,
        new_name: str | None,
        file_attributes: FileAttributeFlags,
        result: int,
    ) -> None:
        """Called after a new item has been created."""

    def update_progress(self, work_total: int, work_so_far: int) -> None:
        """Called periodically to update the progress of the operation."""

    def reset_timer(self) -> None:
        """Called when the timer is reset."""

    def pause_timer(self) -> None:
        """Called when the timer is paused."""

    def resume_timer(self) -> None:
        """Called when the timer is resumed."""
