__all__ = [
    'FileAttributeFlags',
    'FileOperationFlags',
    'TransferSourceFlags',
]

from enum import Flag, IntEnum, IntFlag


class FileAttributeFlags(IntFlag):
    """Flags to use on a WIN32_FIND_DATAW structured to set the file attributes. See:
    https://learn.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants"""

    ARCHIVE = 0x20
    """A file or directory that is an archive file or directory. Applications typically
    use this attribute to mark files for backup or removal."""

    COMPRESSED = 0x800
    """A file or directory that is compressed. For a file, all of the data in the file
    is compressed. For a directory, compression is the default for newly created files
    and subdirectories."""

    DEVICE = 0x40
    """This value is reserved for system use."""

    DIRECTORY = 0x10
    """The handle that identifies a directory."""

    ENCRYPTED = 0x4000
    """A file or directory that is encrypted. For a file, all data streams in the file
    are encrypted. For a directory, encryption is the default for newly created files
    and subdirectories."""

    HIDDEN = 0x2
    """The file or directory is hidden. It is not included in an ordinary directory
    listing."""

    INTEGRITY_STREAM = 0x8000
    """The directory or user data stream is configured with integrity (only supported on
    ReFS volumes). It is not included in an ordinary directory listing. The integrity
    setting persists with the file if it's renamed. If a file is copied the destination
    file will have integrity set if either the source file or destination directory have
    integrity set."""

    NORMAL = 0x80
    """A file that does not have other attributes set. This attribute is valid only when
    used alone."""

    NOT_CONTENT_INDEXED = 0x2000
    """The file or directory is not to be indexed by the content indexing service."""

    NO_SCRUB_DATA = 0x20000
    """The user data stream not to be read by the background data integrity scanner (AKA
    scrubber). When set on a directory it only provides inheritance. This flag is only
    supported on Storage Spaces and ReFS volumes. It is not included in an ordinary
    directory listing."""

    OFFLINE = 0x1000
    """The data of a file is not available immediately. This attribute indicates that
    the file data is physically moved to offline storage. This attribute is used by
    Remote Storage, which is the hierarchical storage management software. Applications
    should not arbitrarily change this attribute."""

    READONLY = 0x1
    """A file that is read-only. Applications can read the file, but cannot write to it
    or delete it. This attribute is not honored on directories. """

    RECALL_ON_DATA_ACCESS = 0x400000
    """When this attribute is set, it means that the file or directory is not fully
    present locally. For a file that means that not all of its data is on local storage
    (e.g. it may be sparse with some data still in remote storage). For a directory it
    means that some of the directory contents are being virtualized from another
    location. Reading the file / enumerating the directory will be more expensive than
    normal, e.g. it will cause at least some of the file/directory content to be fetched
    from a remote store. Only kernel-mode callers can set this bit."""

    RECALL_ON_OPEN = 0x40000
    """This attribute only appears in directory enumeration classes
    (FILE_DIRECTORY_INFORMATION, FILE_BOTH_DIR_INFORMATION, etc.). When this attribute
    is set, it means that the file or directory has no physical representation on the
    local system; the item is virtual. Opening the item will be more expensive than
    normal, e.g. it will cause at least some of it to be fetched from a remote store."""

    REPARSE_POINT = 0x400
    """A file or directory that has an associated reparse point, or a file that is a
    symbolic link."""

    SPARSE_FILE = 0x200
    """A file that is a sparse file."""

    SYSTEM = 0x4
    """A file or directory that the operating system uses a part of, or uses
    exclusively."""

    TEMPORARY = 0x100
    """A file that is being used for temporary storage. File systems avoid writing data
    back to mass storage if sufficient cache memory is available, because typically, an
    application deletes a temporary file after the handle is closed. In that scenario,
    the system can entirely avoid writing the data. Otherwise, the data is written after
    the handle is closed."""

    VIRTUAL = 0x10000
    """This value is reserved for system use."""

    PINNED = 0x80000
    """This attribute indicates user intent that the file or directory should be kept
    fully present locally even when not being actively accessed. This attribute is for
    use with hierarchical storage management software."""

    UNPINNED = 0x200000
    """This attribute indicates that the file or directory should not be kept fully
    present locally except when being actively accessed. This attribute is for use with
    hierarchical storage management software."""


class FileOperationFlags(IntFlag):
    ALLOW_UNDO = 0x40
    """Allow the operation to be undone."""

    FILES_ONLY = 0x80
    """Only operate on files, not folders, if a wildcard is used."""

    NO_CONFIMATION = 0x10
    """Automatically respond to any dialog box that would be shown with 'Yes to All'."""

    NO_CONFIRM_MKDIR = 0x200
    """Do not confirm the creation of a new directory if the operation requires one to
    be created."""

    NO_CONNECTED_ELEMENTS = 0x2000
    """Do not move connected elements as a group."""

    NOCOPYSECURITYATTRIBS = 0x800
    """Do not copy the security attributes of the file."""

    NOERRORUI = 0x400
    """Do not display a message to the user if an error occurs. If this flag is set
    without EARLYFAILURE, any error is treated as if the user had chosen 'Ignore' or
    'Continue'. It halts the current action, sets a flag to indicate that an action was
    aborted, and proceeds with the rest of the operation."""

    NORECURSION = 0x8000
    """Only operate in the local folder. Do not operate recursively into subdirectories.
    """

    RENAMEONCOLLISION = 0x8
    """Give the item being operated on a new name in a move, copy, or rename operation
    if an item with the target name already exists."""

    SILENT = 0x4
    """Do not display a progress dialog box."""

    WANTNUKEWARNING = 0x1000
    """Send a warning if a file or folder is being destroyed during a delete operation
    rather than recycled. This flag partially overrides NOCONFIRMATION."""

    ADDUNDORECORD = 0x20000000
    """Introduced in Windows 8. The file operation was user-invoked and should be placed
    on the undo stack. This flag is preferred to ALLOWUNDO."""

    NOSKIPJUNCTIONS = 0x10000
    """Walk into Shell namespace junctions. By default, junctions are not entered."""

    PREFERHARDLINK = 0x20000
    """If possible, create a hard link rather than a new instance of the file in the
    destination."""

    SHOWELEVATIONPROMPT = 0x40000
    """If an operation requires elevated rights and the NOERRORUI flag is set to disable
    error UI, display a UAC UI prompt nonetheless."""

    EARLYFAILURE = 0x100000
    """If EARLYFAILURE and NOERRORUI are set, the entire set of operations is stopped
    upon encountering any error in any operation."""

    PRESERVEFILEEXTENSIONS = 0x200000
    """With RENAMEONCOLLISION, rename collisions in such a way as to preserve file name
    extensions."""

    KEEPNEWERFILE = 0x400000
    """Keep the newer file or folder, based on the Date Modified property, if a
    collision occurs. This is done automatically with no prompt UI presented to the
    user."""

    NOCOPYHOOKS = 0x800000
    """Do not use copy hooks."""

    NOMINIMIZEBOX = 0x1000000
    """Do not allow the progress dialog to be minimized."""

    MOVEACLSACROSSVOLUMES = 0x2000000
    """Copy the security attributes of the source item to the destination item when
    performing a cross-volume move operation. Without this flag, the destination item
    receives the security attributes of its new folder."""

    DONTDISPLAYSOURCEPATH = 0x4000000
    """Do not display the path of the source item in the progress dialog."""

    DONTDISPLAYDESTPATH = 0x8000000
    """Do not display the path of the destination item in the progress dialog."""

    RECYCLEONDELETE = 0x80000
    """Introduced in Windows 8. When a file is deleted, send it to the Recycle Bin
    rather than permanently deleting it."""

    REQUIREELEVATION = 0x10000000
    """Introduced in Windows Vista SP1. The user expects a requirement for rights
    elevation, so do not display a dialog box asking for a confirmation of the
    elevation."""

    COPYASDOWNLOAD = 0x40000000
    """Introduced in Windows 7. Display a Downloading instead of Copying message in the
    progress dialog."""

    DONTDISPLAYLOCATIONS = 0x80000000
    """Introduced in Windows 7. Do not display the location line in the progress dialog.
    """


class TransferSourceFlags(Flag):
    """Flags recieved in a Pre/Post-Move/Copy, etc event in IFileOperationProgressSink.
    https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/ne-shobjidl_core-_transfer_source_flags
    """

    # Just a Flag, not IntFlag, since we don't pass it *into* any win32 API calls.

    NORMAL = 0x0
    FAIL_EXIST = 0x0
    """Fail if the destination already exists, unless OVERWRITE_EXIST is specified. This
    is a default behavior."""

    RENAME_EXIST = 0x1
    """Rename with auto-name generation if the destination already exists."""

    OVERWRITE_EXIST = 0x2
    """Overwrite or merge with the destination."""

    ALLOW_DECRYPTION = 0x4
    """Allow creation of a decrypted destination."""

    NO_SECURITY = 0x8
    """No discretionary access control list (DACL), system access control list (SACL),
    or owner."""

    COPY_CREATION_TIME = 0x10
    """Copy the creation time as part of the copy. This can be useful for a move
    operation that is being used as a copy and delete operation
    (MOVE_AS_COPY_DELETE)."""

    COPY_WRITE_TIME = 0x20
    """Copy the last write time as part of the copy."""

    USE_FULL_ACCESS = 0x40
    """Assign write, read, and delete permissions as share mode."""

    DELETE_RECYCLE_IF_POSSIBLE = 0x80
    """Recycle on file delete, if possible."""

    COPY_HARD_LINK = 0x100
    """Hard link to the desired source (not required). This avoids a normal copy
    operation."""

    COPY_LOCALIZED_NAME = 0x200
    """Copy the localized name."""

    MOVE_AS_COPY_DELETE = 0x400
    """Move as a copy and delete operation."""

    TSF_SUSPEND_SHELLEVENTS = 0x800
    """Suspend Shell events."""


class FileOperationResult(IntEnum):
    # NOTE: I haven't been able to find this in the MSDocs anwhere. The closest I've
    # found is in pywin32 this is defined as COPYENGINE_S_DONT_PROCESS_CHILDREN, which
    # doesn't make sense as a return code from the operations it's coming from. But,
    # it's the result I'm getting for successful file operations.
    SUCCESS = 0x270008
    """A successful move/copy/rename/delete operation."""

    E_DESTINATION_IS_FILE = 0x8027000B
    """A move/copy/rename tried to operate on a folder, but the target already exists as
    a file.
    """

    E_DESTINATION_IS_FOLDER = 0x8027000C
    """A move/copy/rename tried to operate on a file, but the target already exists as a
    folder.
    """

    E_REQUIRES_ELEVATION = 0x80270002
    E_ACCESS_DENIED_SOURCE = 0x80270021
    E_ACCESS_DENIED_DESTINATION = 0x80270022
    """The user requires elevated permissions to perform the operation."""

    E_ALREADY_EXISTS_NORMAL = 0x80270029
    E_ALREADY_EXISTS_READONLY = 0x8027002A
    E_ALREADY_EXISTS_SYSTEM = 0x8027002B
    E_ALREADY_EXISTS_FOLDER = 0x8027002C
    """The file already exists."""
