from enum import IntFlag


class FileAttributeFlags(IntFlag):
    """Flags to use on a WIN32_FIND_DATAW structured to set the file attributes. See also:
    https://learn.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants"""

    ARCHIVE = 0x20
    COMPRESSED = 0x800
    DEVICE = 0x40
    DIRECTORY = 0x10
    ENCRYPTED = 0x4000
    HIDDEN = 0x2
    INTEGRITY_STREAM = 0x8000
    NORMAL = 0x80
    NOT_CONTENT_INDEXED = 0x2000
    NO_SCRUB_DATA = 0x20000
    OFFLINE = 0x1000
    READONLY = 0x1
    RECALL_ON_DATA_ACCESS = 0x400000
    RECALL_ON_OPEN = 0x40000
    REPARSE_POINT = 0x400
    SPARSE_FILE = 0x200
    SYSTEM = 0x4
    TEMPORARY = 0x100
    VIRTUAL = 0x10000
    PINNED = 0x80000
    UNPINNED = 0x200000


class FileOperationFlags(IntFlag):
    ALLOW_UNDO = 0x40
    """Allow the operation to be undone."""

    FILES_ONLY = 0x80
    """Only operate on files, not folders, if a wildcard is used."""

    NO_CONFIMATION = 0x10
    """Automatically respond to any dialog box that would be shown with 'Yes to All'."""

    NO_CONFIRM_MKDIR = 0x200
    """Do not confirm the creation of a new directory if the operation requires one to be created."""

    NO_CONNECTED_ELEMENTS = 0x2000
    """Do not move connected elements as a group."""

    NOCOPYSECURITYATTRIBS = 0x800
    """Do not copy the security attributes of the file."""

    NOERRORUI = 0x400
    """Do not display a message to the user if an error occurs. If this flag is set without
    EARLYFAILURE, any error is treated as if the user had chosen 'Ignore' or 'Continue'. It halts
    the current action, sets a flag to indicate that an action was aborted, and proceeds with the
    rest of the operation."""

    NORECURSION = 0x8000
    """Only operate in the local folder. Do not operate recursively into subdirectories."""

    RENAMEONCOLLISION = 0x8
    """Give the item being operated on a new name in a move, copy, or rename operation if an item
    with the target name already exists."""

    SILENT = 0x4
    """Do not display a progress dialog box."""

    WANTNUKEWARNING = 0x1000
    """Send a warning if a file or folder is being destroyed during a delete operation rather than
    recycled. This flag partially overrides NOCONFIRMATION."""

    ADDUNDORECORD = 0x20000000
    """Introduced in Windows 8. The file operation was user-invoked and should be placed on the undo
    stack. This flag is preferred to FOF_ALLOWUNDO."""

    NOSKIPJUNCTIONS = 0x10000
    """Walk into Shell namespace junctions. By default, junctions are not entered."""

    PREFERHARDLINK = 0x20000
    """If possible, create a hard link rather than a new instance of the file in the destination."""

    SHOWELEVATIONPROMPT = 0x40000
    """If an operation requires elevated rights and the NOERRORUI flag is set to disable error UI,
    display a UAC UI prompt nonetheless."""

    EARLYFAILURE = 0x100000
    """If EARLYFAILURE and NOERRORUI are set, the entire set of operations is stopped upon
    encountering any error in any operation."""

    PRESERVEFILEEXTENSIONS = 0x200000
    """With RENAMEONCOLLISION, rename collisions in such a way as to preserve file name extensions.
    """

    KEEPNEWERFILE = 0x400000
    """Keep the newer file or folder, based on the Date Modified property, if a collision occurs.
    This is done automatically with no prompt UI presented to the user."""

    NOCOPYHOOKS = 0x800000
    """Do not use copy hooks."""

    NOMINIMIZEBOX = 0x1000000
    """Do not allow the progress dialog to be minimized."""

    MOVEACLSACROSSVOLUMES = 0x2000000
    """Copy the security attributes of the source item to the destination item when performing a
    cross-volume move operation. Without this flag, the destination item receives the security
    attributes of its new folder."""

    DONTDISPLAYSOURCEPATH = 0x4000000
    """Do not display the path of the source item in the progress dialog."""

    DONTDISPLAYDESTPATH = 0x8000000
    """Do not display the path of the destination item in the progress dialog."""

    RECYCLEONDELETE = 0x80000
    """Introduced in Windows 8. When a file is deleted, send it to the Recycle Bin rather than
    permanently deleting it."""

    REQUIREELEVATION = 0x10000000
    """Introduced in Windows Vista SP1. The user expects a requirement for rights elevation, so do
    not display a dialog box asking for a confirmation of the elevation."""

    COPYASDOWNLOAD = 0x40000000
    """Introduced in Windows 7. Display a Downloading instead of Copying message in the progress
    dialog."""

    DONTDISPLAYLOCATIONS = 0x80000000
    """Introduced in Windows 7. Do not display the location line in the progress dialog."""
