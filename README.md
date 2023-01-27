![tests](https://github.com/lojack5/structured/actions/workflows/tests.yml/badge.svg)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)


# IFileOperation- a simple wrapper to use Windows shell file operations.
This is a very small wrapper around IFileOperation to expose methods to perform file opereration (
move, copy, rename, new, delete) on files using Windows shell operations.  This means these
operations can be undone, files can be recycled, and you can allow users to handle name conflicts:
just like when you do any of these through Windows Explorer.

At the moment this is a very young and so only exposes the file operations:
- Move
- Copy
- Rename
- New
- Delete

More features may be added in the future, feel free to open a feature request for something
specific.


## Installation:
`pip install ifileoperation`

At the moment the library is tested to run on Python 3.11, but other version might work if `pywin32`
 and `comtypes` are available.


## Usage
All of the functionality is accessed via the `FileOperator` class.  This is a scheduling context
manager. If you're familiar with IFileOperation, you'll know that you queue a bunch of operations
you wish to be performed, then order them to be executed all at once:

```python
from Pathlib import Path
from ifileoperation import FileOperator, FileOperationFlags


if __name__ == '__main__':
    # Configure for recycling, showing a prompt if the file(s) can't be recyled
    # and must be deleted instead.
    recycle_flags = (
      # ALLOW_UNDO: for versions < Win8, ADDUNDORECORD is preferred for Win8+
      FileOperationFlags.ALLOW_UNDO | FileOperationFlags.ADDUNDORECORD |
      # RECYCLEONDELETE: Perform deletes as recycles
      FileOperationFlags.RECYCLEONDELETE |
      # WANTNUKEWARNING: If a file is too big to be recyled, show a warning that
      #  it will be deleted instead
      FileOperationFlags.WANTNUKEWARNING |
    )
    # Don't show any confirmation dialogs (except for WANTNUKEWARNING), or a UAC
    # prompt if elevation is required (default behavior)
    ui_flags = (
      # NO_CONFIMATION: Don't show confirmation dialogs (ie, treat all dialogs
      # as if 'Yes to All' was selected)
      FileOperationFlags.NO_CONFIRMATION |
    )
    config = recycle_flags | ui_flags
    with FileOperator(flags=config, commit_on_exit=True) as op:
        op.delete_file('Q:/foo.txt')
        op.delete_file(Path.cwd().join('bar.txt'))
```


## FileOperator
A thin wrapper around IFileOperation, exposing the move, copy, rename, and
delete operations.  All paths can be specified as anything implementing the
`os.PathLike[str]` interface: strings, `Path` objects, or your own custom
`PathLike` class.  The `FileOperator` instance is a context manager: you queue
operations in the `with` block, and then `commit` them or have them committed
automatically.

NOTE: `FileOperator` is not reentrant.  Once you've entered the `with` block and
exited, you should create a new instance to perform more operations.

### Configuring:
Configuration is done via the constructor:
```python
__init__(self, parent=None, flags=FileOperator.DEFAULT_FLAGS, commit_on_exit=False):
```
- `parent`: A optional `HANDLE` to the parent that should own any dialog boxes
  shown. You may also pass a `wx.Window` object, and `FileOperator` will extract
  the handle for you.
- `flags`: A `FileOperationFlags` instance indicating the options you want when
  performing the operations.  See the Microsoft documentation on [these flags](
  https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-ifileoperation-setoperationflags)
  for more details on what each means.  These are also in the docstrings for
  `FileOperationFlags`, so you can read there them as well.  Some common defaults are
  provided as well:
  - `FileOperator.DEFAULT_FLAGS`: This causes behavior as if the user had initiated the
    file operations from within Windows Exlorer with no modifier keys pressed (Shift,
    Ctrl, etc).
  - `FileOperator.UNDO_FLAGS`: This sets the flags needed to allow your operation to be
    undone with `Ctrl+Z`.
  - `FileOperator.SEMI_SILENT_FLAGS`: This hides the progress dialog, and only shows
    dialogs if user intervention is required. For example, if a name collision occurs, or
    when attempting to move a file that cannot be (temporarily) due to being open in
    another program, or if a file must be deleted instead of recycled.
  - `FileOperator.FULL_SILENT_FLAGS`: This performs the operations fully silently, responding
    to any prompts as if "Yes to All" or "Continue" was selected.  Note this does *not*
    resolve other errors, and will fail if any error occurs.  The only prompt that may be shown
    is a UAC prompt if elevation is required.  You can further suppress the UAC prompt with
    `FileOperationFlags.REQUIREELEVATION`.
- `commit_on_exit`: If set to `True`, all the queued operations will be
  automatically commited as long as no exceptions occurred withing the `with`
  block before exiting.  Exceptions *might* still occur during the committing
  itself though!

### Operations supported:
The basic file operations can be scheduled.  In these method signatures,
`StrPath` is defined as `str | os.PathLike[str]`.
- `move_file(source: StrPath, destination: StrPath, new_name: str | None = None)`:
  Moves the file at `source` to the destination directory `destination`.  If `new_name`
  is supplied, the file will also be renamed to the new name.
- `move_files(sources: Iterable[StrPath], destination: StrPath, new_name: str | None = None)`:
  Moves the specified files `sources` to the destination directory `destination`.  If
  `new_name` is supplied, the files will all be renamed to the new name. In this case,
  you probably also want to supply `FileOperationFlags.RENAMEONCOLLISION`.
- `copy_file(source: StrPath, destination: StrPath, new_name: str | None = None)`:
  Like move, but performs a copy instead.
- `copy_files(sources: Iterable[StrPath], destination: StrPath)`:
  Like move (without the rename), but performs a copy instead.
- `rename_file(source: StrPath, new_name: str, allow_move: bool = True)`:
  Renames a file to a new name.  Normally, `new_name` should just be the name of
  the new file, without its directory.  However, if you're used to other file
  APIs that let you "rename" a file into a different directory, `rename_file`
  supports this as well.  When `allow_move` is `True`, if it is detected that
  `new_name` is actually a path resolving to a different directory, this will
  automatically be transformed into a `move_file` operation instead.
- `rename_files(sources: Iterable[StrPath], new_name: str)`:  Renames the given
  files to have the new name.  Unlike `rename_file`, you cannot rename files
  into files in different directories.
- `delete_file(source: StrPath)`: Deletes the target file.
- `delete_files(sources: Iterable[StrPath])`: Deletes the target files.
- `commit()`: Cause all the queue operations to be performed.

### Post-commit attributes
After a `commit`, additional attributes are available on the `FileOperator` instance:
- `return_code`: The `HRESULT` return code from the overall operation. This is usually
  not required to be inspected.
- `aborted`: `True` if any of the operations were aborted / skipped.
- `results`: A mapping of source filenames to destination filenames for successful
  operations.  In the special case of deleted files, the destination will be `'RECYCLED'`
  or `'DELETED'` respectively.

### Exceptions
This library may raise any of the following exceptions:
  - `NotADirectoryError`: This can happen when trying to rename a folder if a file
    already exists with the same name, or attempting to move/copy to a directory
    that doesn't exist.
  - `IsADirectoryError`: This can happen when trying to rename a file if a folder
    already exists with the same name.
  - `PermissionError`: Can occur for various reasons, common examples are UAC
    elevation being required, or modifying a read-only file.
  - `FileExistsError`: Can occur when attempting to create a new file, when one
    of the same name already exists.
  - `FileNotFoundError`: Happens if the source file for an operation cannot be
    found.
  - `ifileoperation.IFileOperationError`: For all other errors that occur. These
    are a simple wrapper around `pythoncom.com_error`, and expose an `.hresult`
    attribute with the `HRESULT` that triggered the error.
In the future, more `HRESULT`s may be converted into standard library `OSError`s.


## Contributing
Pull requests are welcome!  We use branch protection with some (minimal) tests
at the moment: just formatting really. To install the dependencies needed for
development, use:
`pip install -r requirements-dev.txt`

And before committing make sure to check against the tests and formatters:
- `pytest`: No tests at the moment
- `black ifileoperation`: Code formatting
- `isort ifileoperation`: Code formatting
- `flake8 ifileoperation`: Linting

IFileOperation uses [semantic versioning](https://semver.org/), but if you're
unsure if your changes need a version bump feel free to note that in your pull
request and you'll get feedback!

If you're not into coding, you can open a [Bug Report or Feature Request](https://github.com/lojack5/IFileOperation/issues)
and I'll look into it.
