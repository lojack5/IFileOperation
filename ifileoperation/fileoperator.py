__all__ = [
    'FileOperator',
]

from os import PathLike, fspath
from pathlib import Path
from typing import Iterable, TypeAlias

from .com import (
    FileOperation,
    FileOperationProgressSink,
    convert_exceptions,
    parse_filename,
)
from .errors import IFileOperationError, UnexpectedError
from .flags import FileOperationFlags, FileOperationResult, TransferSourceFlags

StrPath: TypeAlias = str | PathLike[str]


class ProgressSink(FileOperationProgressSink):
    """ProgressSink that logs successful operations."""

    def __init__(self):
        self.name_map = {}

    def finish_operations(self, result: int) -> None:
        self.result_code = result

    def post_copy_item(
        self,
        transfer_flags: TransferSourceFlags,
        source: str,
        destination: str,
        new_name: str | None,
        result: int,
    ) -> None:
        if new_name:
            self.name_map[source] = new_name

    def post_delete_item(
        self,
        transfer_flags: TransferSourceFlags,
        source: str,
        result: int,
        recycled: bool,
    ) -> None:
        if result == FileOperationResult.SUCCESS:
            if recycled:
                self.name_map[source] = 'RECYCLE_BIN'
            else:
                self.name_map[source] = 'DELETED'

    def post_move_item(
        self,
        transfer_flags: TransferSourceFlags,
        source: str,
        destination: str,
        new_name: str | None,
        result: int,
    ) -> None:
        if new_name:
            self.name_map[source] = new_name

    def post_rename_item(
        self,
        transfer_flags: TransferSourceFlags,
        source: str,
        new_name: str | None,
        result: int,
    ) -> None:
        if new_name:
            self.name_map[source] = new_name


class FileOperator:
    """A context manager for performing file operations.  Not reentrant."""

    DEFAULT_FLAGS = None
    """Default file operation behavior. File operations behave just as if the user had
    performed them in Windows Explorer with no modifiers (eg: Shift, Ctrl, etc).
    """

    UNDO_FLAGS = (
        FileOperationFlags.ADDUNDORECORD
        | FileOperationFlags.ALLOW_UNDO
        | FileOperationFlags.RECYCLEONDELETE
    )
    """Standard flags to allow operations to be undone with Ctrl + Z."""

    SEMI_SILENT_FLAGS = (
        FileOperationFlags.WANTNUKEWARNING
        | FileOperationFlags.SILENT
        | FileOperationFlags.NO_CONFIRM_MKDIR
    )
    """Flags to suppress progress dialogs, but still show dialogs for name collisions
    and temporary errors (eg: due to a file open in another program), allowing the user
    to Try Again or Skip.
    """

    FULL_SILENT_FLAGS = (
        FileOperationFlags.SILENT
        | FileOperationFlags.NO_CONFIMATION
        | FileOperationFlags.NOERRORUI
        | FileOperationFlags.EARLYFAILURE
        | FileOperationFlags.NO_CONFIRM_MKDIR
        | FileOperationFlags.SHOWELEVATIONPROMPT
    )
    """Flags to suppress all dialogs (as if Yes to All was selected), except for a UAC
    prompt if necessary.  If errors occur, the operation will fail immediately.
    """

    @convert_exceptions
    def __init__(
        self,
        parent=None,
        flags: FileOperationFlags | None = DEFAULT_FLAGS,
        *,
        commit_on_exit: bool = False,
    ):
        """Create a FileOperator instance for managing file operations.  To be used with
        the `with` statement. Operations are scheduled first, then performed with the
        `commit` method, or optionally automatically when the with block is exited.

        The context manager is not reentrant.

        :param parent: A HANDLE to the window that should own any dialog boxes that are
            displayed. Also supports wx.Window instances.
        :param flags: The FileOperationFlags to use for the operations.
        :param commit_on_exit: If True (default: False), `commit` will be performed
            automatically when the with block is exited if no exceptions were raised.
        """
        self.ifo = FileOperation()
        self.sink = ProgressSink()
        self.sink_cookie = self.ifo.Advise(self.sink.com_ptr)
        if parent is not None:
            try:
                parent = parent.GetHandle()  # wx.Window
            except AttributeError:
                pass
        if parent is not None:
            self.ifo.SetOwnerWindow(parent)
        if flags is not None:
            self.ifo.SetOperationFlags(int(flags))
        self.commit_on_exit = commit_on_exit
        self.entered = False
        self._operations_queued = False

    def __enter__(self):
        if self.entered:
            raise IFileOperationError(f'{type(self).__name__} is not reentrant')
        else:
            self.entered = True
            return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.commit_on_exit and not exc_type:
            self.commit()
            self.ifo.Unadvise(self.sink_cookie)
        # Delete the IFileOperation instance, so reentrance will raise an error
        del self.ifo

    @convert_exceptions
    def move_file(
        self, source: StrPath, destination: StrPath, new_name: str | None = None
    ) -> None:
        """Schedule to move a file from `source` to `destination`.  Optionally rename
        the file in the process. NOTE: Windows performs a move to a different logical
        drive as a copy and delete.

        :param source: The file to be moved.
        :param destination: The destination *directory* to move to.
        :param new_name: The new name for the file if desired.
        """
        self.ifo.MoveItem(
            parse_filename(source), parse_filename(destination, True), new_name
        )
        self._operations_queued = True

    @convert_exceptions
    def move_files(self, sources: Iterable[StrPath], destination: StrPath) -> None:
        """Schedule to move the files `sources` to `destination`. NOTE: Windows performs
        a move to a different logical drive as a copy and delete.

        :param sources: And iterable of filenames to be moved.
        :param destination: The destination *directory* to move to.
        """
        srcs = [parse_filename(s) for s in sources]
        self.ifo.MoveItems(srcs, parse_filename(destination, True))
        self._operations_queued = True

    @convert_exceptions
    def rename_file(
        self, source: StrPath, new_name: str, allow_move: bool = True
    ) -> None:
        """Schedule to rename `source` to `new_name`.  If `allow_move` is True and the
        destination is in a different directory, this will perform a move instead.

        :param source: The file to be renamed.
        :param new_name: The new name of the file.
        :param allow_move: If True, then converts a rename into a move when new_name is
            in a different directory than the source.
        """
        if allow_move:
            # Check if new_name refers to a file in a different directory
            dest_path = Path(new_name)
            if len((dest_parts := dest_path.parts)) == 1:
                # No directory on the new_name, all good for a rename
                pass
            elif Path(source).parts[:-1] != dest_parts[:-1]:
                # new_name wants the file to be in a different directory, do a move
                # instead
                self.move_file(source, dest_path.parent, dest_path.name)
                return
            else:
                # new_name includes the directory, but it's the same directory, so a
                # rename is fine
                new_name = dest_path.name
        self.ifo.RenameItem(parse_filename(source), new_name)
        self._operations_queued = True

    @convert_exceptions
    def rename_files(self, sources: Iterable[StrPath], new_name: StrPath) -> None:
        """Schedule to rename the files `sources` to `new_name`.  All files will be
        renamed to the new name.

        :param sources: An iterable of filenames to be renamed.
        :param new_name: The new name of the files.
        """
        srcs = [parse_filename(s) for s in sources]
        self.ifo.RenameItems(srcs, fspath(new_name))
        self._operations_queued = True

    @convert_exceptions
    def copy_file(
        self, source: StrPath, destination: StrPath, new_name: str | None = None
    ) -> None:
        """Schedule to copy a file from `source` to `destination`. Optionally rename the
        file in the process.

        :param source: The file to be copied.
        :param destination: The destination *directory* to copy to.
        :param new_name: Optional new name of the file.
        """
        self.ifo.CopyItem(
            parse_filename(source), parse_filename(destination, True), new_name
        )
        self._operations_queued = True

    @convert_exceptions
    def copy_files(self, sources: Iterable[StrPath], destination: StrPath) -> None:
        """Schedule to copy the files `sources` to `destination`.

        :param sources: An iterable of filenames to be copied.
        :param destination: The destination *directory* to copy to.
        """
        srcs = [parse_filename(s) for s in sources]
        self.ifo.CopyItems(srcs, parse_filename(destination, True))
        self._operations_queued = True

    @convert_exceptions
    def delete_file(self, source: StrPath) -> None:
        """Schedule to delete a file.

        :param source: The file to be deleted.
        """
        self.ifo.DeleteItem(parse_filename(source))
        self._operations_queued = True

    @convert_exceptions
    def delete_files(self, sources: Iterable[StrPath]) -> None:
        """Schedule to delete the files `sources`.

        :param sources: An iterable of filenames to be deleted.
        """
        srcs = [parse_filename(s) for s in sources]
        self.ifo.DeleteItems(srcs)
        self._operations_queued = True

    @convert_exceptions
    def _perform_operations(self):
        self.return_code = self.ifo.PerformOperations()

    def commit(self):
        """Perform all scheduled file operations."""
        try:
            self._perform_operations()
        except UnexpectedError:
            if not self._operations_queued:
                # Actually expected when no operations have been queued
                self.return_code = 0
                self.aborted = False
                self.results = {}
            else:
                raise
        else:
            self.aborted = self.ifo.GetAnyOperationsAborted()
            self.results = self.sink.name_map
            if self.return_code is None:
                self.return_code = self.sink.result_code
