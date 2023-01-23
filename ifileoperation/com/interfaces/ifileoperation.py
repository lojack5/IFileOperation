"""IFileOperation is fully wrapped in pywin32, so this is purely for typehinting."""

__all__ = [
    'IFileOperation',
]

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Generic, TypeAlias, TypeVar

    from win32com.shell import shell  # type: ignore (module *does* exist)

    class IUnknown:
        def AddRef(self) -> int:
            ...

        def QueryInterface(self, pp) -> int:
            ...

        def Release(self) -> int:
            ...

    TIShellItem = TypeVar('TIShellItem')

    class _IFileOperation(Generic[TIShellItem], IUnknown):
        def Advise(self, pfops) -> int:
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
            pszTemplateName: str,
            pszDestinationName: str,
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

    def _make(
        callable: Callable[..., TIShellItem]
    ) -> type[_IFileOperation[TIShellItem]]:
        """Uses typing hijinks to extract the return type of a callable to apply to the
        IFileOperation interface.  This way typeshed hint types can be extracted and
        used as a hint for the member method parameters.
        """
        return _IFileOperation[TIShellItem]

    IFileOperation: TypeAlias = _make(shell.SHCreateItemFromParsingName)  # type: ignore
else:
    from typing import NewType

    IFileOperation = NewType('IFileOperation', object)
