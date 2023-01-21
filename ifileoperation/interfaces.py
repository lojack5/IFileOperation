"""
Interfaces for typing.  Partially typed.
"""
__all__ = [
    'IFileOperation',
]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Generic, TypeAlias, TypeVar

    from win32com.shell import shell  # type: ignore (module *does* exist)

    class IUknown:
        def AddRef(self) -> int:
            ...

        def QueryInterface(self, pp) -> int:
            ...

        def Release(self) -> int:
            ...

    # Use typing hyjinks to extract the types from pywin32 typeshed
    TIShellItem = TypeVar('TIShellItem')

    class _IFileOperation(Generic[TIShellItem], IUknown):
        def Advise(self, pfops, pdwCookie) -> int:
            ...

        def ApplyPropertiesToItem(self, item: TIShellItem) -> int:
            ...

        def ApplyPropertiesToItems(self, items: list[TIShellItem]) -> int:
            ...

        def CopyItem(
            self,
            item: TIShellItem,
            destination_folder: TIShellItem,
            new_name: str | None = ...,
        ) -> int:
            ...

        def CopyItems(
            self, items: list[TIShellItem], destination_folder: TIShellItem
        ) -> int:
            ...

        def DeleteItem(self, item: TIShellItem, pfofsItem=...) -> int:
            ...

        def DeleteItems(self, items: list[TIShellItem]) -> int:
            ...

        def GetAnyOperationsAborted(self, pfAnyOperationsAborted=...) -> int:
            ...

        def MoveItem(
            self,
            item: TIShellItem,
            destination_folder: TIShellItem,
            new_name: str | None = ...,
            pfopsItem=...,
        ) -> int:
            ...

        def MoveItems(
            self, items: list[TIShellItem], destination_folder: TIShellItem
        ) -> int:
            ...

        def NewItem(
            self,
            destination_folder: TIShellItem,
            file_attributes: int,
            name: str,
            pszTemplateName,
            pszDestinationName,
            pfopsItem=...,
        ) -> int:
            ...

        def PerformOperations(self) -> int:
            ...

        def RenameItem(self, item: TIShellItem, new_name: str, pfsopsItem=...) -> int:
            ...

        def RenameItems(self, items: list[TIShellItem], new_name: str) -> int:
            ...

        def SetOperationFlags(self, operation_flags: int) -> int:
            ...

        def SetOwnerWindow(self, hwndOwner) -> int:
            ...

        def SetProgressDialog(self, popd) -> int:
            ...

        def SetProgressMessage(self, message: str) -> int:
            ...

        def SetProperties(self, pPropArray) -> int:
            ...

        def Unadvise(self, dwCookie: int) -> int:
            ...

    def _ifile_operation(
        callable: Callable[..., TIShellItem]
    ) -> type[_IFileOperation[TIShellItem]]:
        return _IFileOperation[TIShellItem]

    IFileOperation: TypeAlias = _ifile_operation(shell.SHCreateItemFromParsingName)  # type: ignore


else:
    from typing import NewType

    IFileOperation = NewType('IFileOperation', object)
